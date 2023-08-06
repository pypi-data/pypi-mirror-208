"""Manage GDN collection streams"""

import json
import logging
import os
import uuid

import pulsar
import singer
from c8 import C8Client
from datetime import datetime, timezone
from prometheus_client import start_http_server, Counter, Histogram
from singer import utils
from singer.catalog import CatalogEntry

LOGGER = singer.get_logger('macrometa_source_collection')

region_label = os.getenv("GDN_FEDERATION", "NA")
tenant_label = os.getenv("GDN_TENANT", "NA")
fabric_label = os.getenv("GDN_FABRIC", "NA")
workflow_label = os.getenv("WORKFLOW_UUID", "NA")
metric_service_url = os.getenv("METRIC_SERVICE_API")
is_metrics_enabled = os.getenv("MACROMETA_SOURCE_COLLECTION_IS_METRICS_ENABLED", 'False')

class GDNCollectionClient:
    """Client for handling GDN collection streams."""

    def __init__(self, config) -> None:
        """Init new GDN Collection Client."""
        self._host = config.get("region")
        self._fabric = config.get("fabric")
        _apikey = config.get("api_key")
        self._wf_uuid = os.getenv('WORKFLOW_UUID')
        self._collection = config.get("source_collection")
        self._c8_client = C8Client(
            "https",
            host=self._host,
            port=443,
            geofabric=self._fabric,
            apikey=_apikey
        )
        self._auth = pulsar.AuthenticationToken(_apikey)
        self._tenant = self._c8_client.tenant(apikey=_apikey).tenant_name

        # enable collection stream on the source collection.
        self._c8_client.update_collection_properties(self._collection, has_stream=True)

        self.exported_bytes = Counter("exported_bytes", "Total number of bytes exported from GDN collections", ['region', 'tenant', 'fabric', 'workflow'])
        self.exported_documents = Counter("exported_documents", "Total number of documents exported from GDN collections", ['region', 'tenant', 'fabric', 'workflow'])
        self.export_errors = Counter("export_errors", "Total count of errors while exporting data from GDN collections", ['region', 'tenant', 'fabric', 'workflow'])
        self.export_lag = Histogram("export_lag", "The average time from when the data changes in GDN collections are reflected in external data sources", ['region', 'tenant', 'fabric', 'workflow'])
        
        # Start the Prometheus HTTP server for exposing metrics
        if is_metrics_enabled.lower() == 'true':
            LOGGER.info("Source is starting the metrics server.")
            start_http_server(8000)

    def sync(self, stream):
        """Return documents in target GDN collection as records."""
        if self._c8_client.has_collection(self._collection):
            self.send_schema_message(stream)
            columns = list(stream.schema.properties.keys())
            columns.remove("_sdc_deleted_at")
            schema_properties = stream.schema.properties
            self.load_existing_data(stream, columns, schema_properties)
            LOGGER.info("Full table sync completed.")

            # pulsar client throws some messages into stdout when subscribed to a topic. Meltano tap/target doesn't like
            # this and tries to process the pulsar log messages in stdout as input singer records. Therefore we are trying
            #  to turn off pulsar logging here. This is the best way I found with the current pulsar client API.
            _pulsar_logger = logging.getLogger("pulsar-logger")
            _pulsar_logger.setLevel(logging.CRITICAL)
            _pulsar_logger.addHandler(logging.NullHandler())

            _pulsar_client = pulsar.Client(
                f"pulsar+ssl://{self._host}:6651/",
                authentication=self._auth,
                tls_allow_insecure_connection=False,
                logger=_pulsar_logger,
            )
            _sub_name = self._wf_uuid if self._wf_uuid else f"cs_{uuid.uuid1()}"
            _topic = f"persistent://{self._tenant}/c8local.{self._fabric}/{self._collection}"
            _consumer: pulsar.Consumer = _pulsar_client.subscribe(_topic, _sub_name)

            while True:
                try: 
                    msg = _consumer.receive()
                    data = msg.data()
                    if data == None or not data:
                        continue
                    props = msg.properties()
                    j = json.loads(data.decode("utf8"))
                    j.pop('_id', None)
                    j.pop('_rev', None)

                    if props["op"] == "INSERT" or props["op"] == "UPDATE":
                        # skip inserts not having valid schema
                        if len(j.keys() ^ columns) == 0 and all(
                            get_singer_data_type(j[key]) == schema_properties[key].type
                            for key in j.keys()
                        ):
                            j['_sdc_deleted_at'] = None
                            singer_record = self.msg_to_singer_message(stream, j, None, utils.now())
                            singer.write_message(singer_record)
                    elif props["op"] == "DELETE":
                        # Currently, we don't have a way to validate schema here
                        j.pop('_delete', None)
                        j['_sdc_deleted_at'] = singer.utils.strftime(utils.now())
                        singer_record = self.msg_to_singer_message(stream, j, None, utils.now())
                        singer.write_message(singer_record)
                    _consumer.acknowledge(msg.message_id())
                    self.exported_bytes.labels(region_label, tenant_label, fabric_label, workflow_label).inc(len(data))
                    self.exported_documents.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
                    time = datetime.fromtimestamp(msg.publish_timestamp()/1000)
                    time_str = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    event_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    self.export_lag.labels(region_label, tenant_label, fabric_label, workflow_label).observe((utils.now() - event_time).total_seconds())
                except Exception as e:
                    LOGGER.warn(f"Exception received: {e}")
                    self.export_errors.labels(region_label, tenant_label, fabric_label, workflow_label).inc()
        
        else:
            raise FileNotFoundError("Collection {} not found".format(self._collection))


    def load_existing_data(self, stream, columns, schema_properties):
        cursor = self._c8_client._fabric.c8ql.execute(f"FOR d IN @@collection RETURN d",
                                               bind_vars={"@collection": self._collection},
                                               stream=True)
        while (not cursor.empty()) or cursor.has_more():
            rec = cursor.next()
            rec.pop('_id', None)
            rec.pop('_rev', None)
            # skip existing data not having valid schema
            if len(rec.keys() ^ columns) == 0 and all(
                get_singer_data_type(rec[key]) == schema_properties[key].type
                for key in rec.keys()
            ):
                singer_record = self.msg_to_singer_message(stream, rec, None, utils.now())
                singer.write_message(singer_record)
                self.exported_bytes.labels(region_label, tenant_label, fabric_label, workflow_label).inc(len(rec))
                self.exported_documents.labels(region_label, tenant_label, fabric_label, workflow_label).inc()

    def send_schema_message(self, stream: CatalogEntry, bookmark_properties=[]):
        schema_message = singer.SchemaMessage(stream=stream.stream,
                                              schema=stream.schema.to_dict(),
                                              key_properties=stream.key_properties,
                                              bookmark_properties=bookmark_properties)
        singer.write_message(schema_message)

    def msg_to_singer_message(self, stream, msg, version, time_extracted):
        return singer.RecordMessage(
            stream=stream.stream,
            record=msg,
            version=version,
            time_extracted=time_extracted
        )


def get_singer_data_type(val):
    if type(val) == str:
        return "string"
    elif type(val) == int:
        return "integer"
    elif type(val) == float:
        return "number"
    elif type(val) == bool:
        return "boolean"
    else:
        return "object"
