#!/usr/bin/env python3

import argparse
import asyncio
import hashlib
import io
import json
import os
import re
import requests
import sys
import time
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from threading import Thread, Lock

import jsonschema
from adjust_precision_for_schema import adjust_decimal_precision_for_schema
from c8 import C8Client, DocumentInsertError
from c8.collection import StandardCollection
from jsonschema import Draft4Validator
from prometheus_client import Counter, Gauge, start_http_server
from singer import get_logger

logger = get_logger('macrometa_target_collection')

DEFAULT_BATCH_SIZE_ROWS = 100
DEFAULT_BATCH_FLUSH_INTERVAL = 10
DEFAULT_MIN_BATCH_FLUSH_TIME_GAP = 10

# Prometheus metrics
ingested_bytes = Counter('ingested_bytes', 'Total number of bytes ingested', ['region', 'tenant', 'fabric', 'workflow'])
ingested_documents = Counter('ingested_documents', 'Total number of documents ingested', ['region', 'tenant', 'fabric', 'workflow'])
ingest_errors = Counter('ingest_errors', 'Total number of errors during ingestion', ['region', 'tenant', 'fabric', 'workflow'])
ingest_lag = Gauge('ingest_lag', 'Average time lag between data changes in GDN collections and external data sources', ['region', 'tenant', 'fabric', 'workflow'])
scrape_complete_flag = Counter("scrape_complete_flag", "Flag to check if the last scrape has been completed", ['workflow'])

region_label = os.getenv("GDN_FEDERATION", "NA")
tenant_label = os.getenv("GDN_TENANT", "NA")
fabric_label = os.getenv("GDN_FABRIC", "NA")
workflow_label = os.getenv("WORKFLOW_UUID", "NA")
metric_service_url = os.getenv("METRIC_SERVICE_API")
is_metrics_enabled = os.getenv("MACROMETA_TARGET_COLLECTION_IS_METRICS_ENABLED", 'False')

# Start the Prometheus HTTP server for exposing metrics
if is_metrics_enabled.lower() == 'true':
    logger.info("Target is starting the metrics server.")
    start_http_server(8000)

class RecordBatch:
    """Class wrapping the record batch in order to make it thread safe."""

    def __init__(self, config: dict):
        self._list = list()
        self._lock = Lock()
        self.interval = config.get('batch_flush_interval', DEFAULT_BATCH_FLUSH_INTERVAL)
        self.last_executed_time = datetime.now(timezone.utc)
        self.min_time_gap = config.get('batch_flush_min_time_gap', DEFAULT_MIN_BATCH_FLUSH_TIME_GAP)
        self.max_batch_size = config.get('batch_size_rows', DEFAULT_BATCH_SIZE_ROWS)

    def append(self, value) -> None:
        """Acquire the lock and add a record to the list."""
        with self._lock:
            self._list.append(value)

    def length(self) -> int:
        """Acquire the lock and return the number of items in the list."""
        with self._lock:
            return len(self._list)

    def flush(self) -> list:
        """Acquire the lock, create a copy of the existing batch,
        clear the existing batch, and return the copy."""
        with self._lock:
            c = self._list.copy()
            self._list.clear()
            return c


def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        logger.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def try_upsert(collection: StandardCollection, record_batch: RecordBatch, force=False):
    if record_batch.length() >= record_batch.max_batch_size or force:
        to_insert = record_batch.flush()
        to_update = []
        records_array = remove_time_extracted(to_insert)

        for i, r in enumerate(collection.insert_many(records_array)):
            if type(r) is DocumentInsertError:
                to_update.append(to_insert[i])
            else:
                # Update ingested_documents and ingested_bytes metrics
                ingested_documents.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
                ingested_bytes.labels(region_label, tenant_label, fabric_label, workflow_label).inc(len(json.dumps(r)))
                # Update ingest_lag metric
                diff = datetime.now(timezone.utc) - ensure_datetime(to_insert[i]["time_extracted"])
                ingest_lag.labels(region_label, tenant_label, fabric_label, workflow_label).set(diff.total_seconds())

        if len(to_update) > 0:
            records_array = remove_time_extracted(to_update)
            for i, r in enumerate(collection.update_many(records_array)):
                if type(r) is DocumentInsertError:
                    # Increment ingest_errors metric
                    ingest_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
                    print(f'Failed to insert/update record: {to_update[i]}. {r}')
                else:
                    # Update ingest_lag metric
                    diff = datetime.now(timezone.utc) - ensure_datetime(to_update[i]["time_extracted"])
                    ingest_lag.labels(region_label, tenant_label, fabric_label, workflow_label).set(diff.total_seconds())
        record_batch.last_executed_time = datetime.now(timezone.utc)


def remove_time_extracted(records):
    return [{k: v for k, v in record.items() if k != 'time_extracted'} for record in records]


def try_delete(collection: StandardCollection, _key: str):
    try:
        collection.delete(_key)
    except Exception as e:
        # Increment ingest_errors metric
        ingest_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
        logger.warn(f'Failed to delete record with _key: {_key}. {e}')


def persist_messages(collection: StandardCollection, messages: io.TextIOWrapper, record_batch: RecordBatch):
    state = None
    schemas = {}
    key_properties = {}
    validators = {}

    for message in messages:
        try:
            o = json.loads(message)
        except json.decoder.JSONDecodeError as e:
            # Increment ingest_errors metric
            ingest_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
            logger.error(f"Unable to parse:\n{message}")
            raise e

        message_type = o['type']
        if message_type == 'RECORD':
            stream = o['stream']
            if stream not in schemas:
                # Increment ingest_errors metric
                ingest_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
                raise Exception(f"A record for stream {stream} was encountered before a corresponding schema")

            try:
                validators[stream].validate((o['record']))
            except jsonschema.ValidationError as e:
                # Increment ingest_errors metric
                ingest_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
                logger.error(f"Failed parsing the json schema for stream: {stream}.")
                raise e

            try:
                rec = o['record']
                if 'time_extracted' in o:
                    rec["time_extracted"] = ensure_datetime(o["time_extracted"])
                else:
                    rec["time_extracted"] = ensure_datetime(record_batch.last_executed_time)
                try:
                    kps = key_properties.get(stream)
                    _key = None
                    # Appending _ to keys inorder for preserving values of reserved keys in source data
                    reserved_keys = ['_key', '_id', '_rev']

                    if kps:
                        if len(kps) > 1:
                            logger.warn(f'Multiple key_properties found ({",".join(kps)}).'
                                        f' Only `{kps[0]}` will be considered.')
                        _key = str(rec[kps[0]]).strip()
                        if kps[0] == '_key':
                            reserved_keys.remove('_key')

                    for reserved_key in reserved_keys:
                        if rec.get(reserved_key):
                            new_key = "_" + reserved_key
                            while True:
                                if rec.get(new_key):
                                    new_key = "_" + new_key
                                else:
                                    break
                            rec[new_key] = rec.pop(reserved_key)

                    if _key and not (1 <= len(_key) <= 254 and bool(re.match("^[-_!\$%'\(\)\*\+,\.:;=@a-zA-Z0-9]+$", _key))):
                        hashed_key = hashlib.sha256(_key.encode('utf-8'))
                        _key = hashed_key.hexdigest()
                        logger.info(f"Primary key of the source doesn't satisfy the constraints of macrometa "
                                    f"document key, Hashing the key and using it in hex form to make it compliant.")
                    if _key:
                        rec['_key'] = _key
                except:
                    _key = None

                if '_sdc_deleted_at' in rec:
                    if rec['_sdc_deleted_at']:
                        if _key:
                            try_delete(collection, _key)
                    else:
                        rec.pop('_sdc_deleted_at', None)
                        logger.info(f'record is {rec}')
                        record_batch.append(rec)
                else:
                    record_batch.append(rec)
            except TypeError as e:
                # Increment ingest_errors metric
                ingest_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
                # TODO: This is temporary until json serializing issue for Decimals are fixed in pyC8
                logger.debug("pyC8 error occurred")

            state = None
            try_upsert(collection, record_batch)
        elif message_type == 'STATE':
            logger.debug('Setting state to {}'.format(o['value']))
            state = o['value']
            emit_state(state)
        elif message_type == 'SCHEMA':
            stream = o['stream']
            schemas[stream] = o['schema']
            adjust_decimal_precision_for_schema(schemas[stream])
            validators[stream] = Draft4Validator((o['schema']))
            key_properties[stream] = o['key_properties']
        else:
            # Increment ingest_errors metric
            ingest_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
            logger.warning("Unknown message type {} in message {}".format(o['type'], o))

    scrape_complete_flag.labels(workflow_label).inc()
    return state


def ensure_datetime(time_extracted):
    if isinstance(time_extracted, str):
        time_extracted = datetime.strptime(time_extracted, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Make the datetime object timezone-aware by setting it to UTC timezone
        time_extracted = time_extracted.replace(tzinfo=timezone.utc)
    elif time_extracted.tzinfo is None:
        # If the datetime object is timezone-naive, set it to UTC timezone
        time_extracted = time_extracted.replace(tzinfo=timezone.utc)
    return time_extracted


def setup_batch_task(collection: StandardCollection, record_batch: RecordBatch) -> AbstractEventLoop:
    event_loop = asyncio.new_event_loop()
    Thread(target=start_background_loop, args=(event_loop,), daemon=True).start()
    asyncio.run_coroutine_threadsafe(process_batch(collection, record_batch), event_loop)
    return event_loop


async def process_batch(collection: StandardCollection, record_batch: RecordBatch) -> None:
    while True:
        await asyncio.sleep(record_batch.interval)
        timedelta = datetime.now(timezone.utc) - ensure_datetime(record_batch.last_executed_time)
        if timedelta.total_seconds() >= record_batch.min_time_gap:
            # if batch has records that need to be processed but haven't reached batch size then process them.
            try_upsert(collection, record_batch, force=True)


def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    args = parser.parse_args()
    if args.config:
        with open(args.config) as input_json:
            config = json.load(input_json)
    else:
        raise Exception("Required '--config' parameter was not provided")
    region = config['region']
    fabric = config['fabric']
    apikey = config['api_key']
    target_collection = config['target_collection']
    client = C8Client(
        protocol='https',
        host=region,
        port=443,
        apikey=apikey,
        geofabric=fabric
    )

    if not client.has_collection(target_collection):
        client.create_collection(name=target_collection)

    collection = client.get_collection(target_collection)
    record_batch = RecordBatch(config)
    event_loop = setup_batch_task(collection, record_batch)
    input_messages = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    state = persist_messages(collection, input_messages, record_batch)

    # There can still be records in the `record_batch` which is not processed,
    # So, we have to force process it one last time before the workflow terminates.
    try_upsert(collection, record_batch, force=True)

    # Wait for Prometheus to scrape the metrics
    logger.info("Waiting for metrics scrape...")
    while not is_scrape_complete(metric_service_url, f"{scrape_complete_flag._name}_total", f"workflow=\"{workflow_label}\""):
        time.sleep(15)
    logger.info("Metrics scrape complete. Exiting...")

    emit_state(state)
    event_loop.stop()
    logger.info("Completing normally...")


def is_scrape_complete(prometheus_url, metric_name, filter):
    response = requests.get(f"{prometheus_url}/query", params={"query": f"{metric_name}{{{filter}}}"})
    if response.status_code == 200:
        json_data = response.json()
        if json_data["data"]["result"] and len(json_data["data"]["result"]) > 0:
            return True
    return False


if __name__ == '__main__':
    main()
