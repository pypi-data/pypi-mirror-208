from txp.common.models.firestore_models_client import (
    FirestoreModelsQuery,
    FirestoreModelsClient,
)

from .relational_entity import TxpRelationalEntity
import txp.common.models.protos.models_pb2 as models_pb2
import google.protobuf.timestamp_pb2 as timestamp_pb2
import dataclasses
import google.cloud.firestore as firestore
import datetime
from typing import Any, Union
import pytz
import logging


@dataclasses.dataclass
class AssetMetrics(TxpRelationalEntity):
    asset_type: str = ""
    last_seen: Union[str, datetime.datetime] = ""
    rpm: float = 0.0
    temperature: float = 0.0
    worked_hours: float = 0.0
    asset_id: str = ""

    @classmethod
    def last_seen_format(cls) -> str:
        return "%Y-%m-%d %H:%M:%S"

    def __post_init__(self):
        self.last_seen_datetime = datetime.datetime.strptime(
            self.last_seen, AssetMetrics.last_seen_format()
        )
        self.last_seen_datetime.replace(
            tzinfo=pytz.timezone("America/Mexico_City")
        )

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "asset_metrics"

    @classmethod
    def get_proto_class(cls):
        return models_pb2.AssetMetricsProto

    @classmethod
    def update_metric_in_firestore(cls, new_values: "AssetMetrics", tenant_id: str):
        client = FirestoreModelsClient(credentials=None)
        assets_query = FirestoreModelsQuery(
            AssetMetrics,
            tenant_id,
            [("asset_id", "==", new_values.asset_id)],
            AssetMetrics.get_db_query_fields([models_pb2.WEB_REQUIRED]),
            f"asset_metrics/{tenant_id}/assets",
            False,
        )

        client.add_query(assets_query)
        r = client.get_query_results()

        if not r[0]:
            # The metrics were not found, the object will be created
            db = firestore.Client()
            assets_col: firestore.CollectionReference = (
                db.collection("asset_metrics").document(tenant_id).collection("assets")
            )
            assets_col.document(new_values.asset_id).set(new_values.get_dict())
            logging.info(
                f"Asset Metrics Created in Firestore for {new_values.asset_id}"
            )
        else:
            # The metrics did exists, we need to update values.
            old_metrics: AssetMetrics = r[0][0]
            new_values.worked_hours += old_metrics.worked_hours
            new_values._proto.worked_hours = new_values.worked_hours
            logging.info(
                f"New worked hours total for {new_values.asset_id} : {new_values.worked_hours} hrs"
            )
            db = firestore.Client()
            assets_col: firestore.CollectionReference = (
                db.collection("asset_metrics").document(tenant_id).collection("assets")
            )
            assets_col.document(new_values.asset_id).update(new_values.get_dict())
            logging.info(
                f"Asset Metrics Updated in Firestore for {new_values.asset_id}"
            )
