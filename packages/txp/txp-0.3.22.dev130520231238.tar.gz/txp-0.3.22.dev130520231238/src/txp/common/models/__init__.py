"""
    Imports all the entities from TXP Project Model
"""
from .asset import Asset
from .asset_metrics import AssetMetrics
from .assets_group import AssetsGroup
from .device import *
from .edge import Edge
from .gateway import Gateway
from .vibration_mock_components import VibrationMockComponent
from .perception import Perception
from .sampling_job import *
from .firestore_models_client import FirestoreModelsClient, FirestoreModelsQuery


class ProjectFirestoreModel:
    """This class represents the project model snapshot instance downloaded
    from the database

        References:
        - https://tranxpert.atlassian.net/wiki/spaces/TD/pages/345538579/Project+structure
        - https://tranxpert.atlassian.net/wiki/spaces/TD/pages/345571390/Job+Structure
    """

    def __init__(
        self,
        assets_groups: List[AssetsGroup] = None,
        assets: List[Asset] = None,
        devices: List[Device] = None,
        edges: List[Edge] = None,
        gateways: List[Gateway] = None
    ):
        self.assets_groups: List[AssetsGroup] = assets_groups

        self.assets_groups_table: Dict[str, AssetsGroup] = dict(map(
            lambda ag: (ag.name, ag),
            assets_groups
        ))

        self.assets_table: Dict[str, Asset] = dict(map(
            lambda a: (a.asset_id, a),
            assets
        ))

        self.devices_table: Dict[str, Device] = dict(map(
            lambda d: (d.kind, d),
            devices
        ))

        self.edges_table: Dict[str, Edge] = dict(map(
            lambda e: (e.logical_id, e),
            edges
        ))

        self.gateway_table: Dict[str, Gateway] = dict(map(
            lambda g: (g.gateway_id, g),
            gateways
        ))

    def get_dict(self):
        l = lambda entity: entity.get_dict()
        assets_groups = list(map(l, self.assets_groups))
        assets = list(map(l, self.assets_table.values()))
        devices = list(map(l, self.devices_table.values()))
        edges = list(map(l, self.edges_table.values()))
        gateways = list(map(l, self.gateway_table.values()))

        return {
            'assets_groups': assets_groups,
            'assets': assets,
            'devices': devices,
            'edges': edges,
            'gateways': gateways
        }

    @staticmethod
    def from_dict(d: Dict):
        assets_groups = list(map(
            lambda dd: AssetsGroup.from_dict(dd),
            d['assets_groups']
        ))
        assets = list(map(
            lambda dd: Asset.from_dict(dd),
            d['assets']
        ))
        devices = list(map(
            lambda dd: Device.from_dict(dd),
            d['devices']
        ))
        edges = list(map(
            lambda dd: Edge.from_dict(dd),
            d['edges']
        ))
        gateways = list(map(
            lambda dd: Gateway.from_dict(dd),
            d['gateways']
        ))
        return ProjectFirestoreModel(
            assets_groups,
            assets,
            devices,
            edges,
            gateways
        )

def get_project_model(
    credentials,
    tags: List[type(models_pb2.EntityFieldRequiredByEnum)],
    tenant_id: str
):
    db = FirestoreModelsClient(credentials)

    assets_groups = FirestoreModelsQuery(AssetsGroup, tenant_id, [],
                                         AssetsGroup.get_db_query_fields(tags))
    assets_query = FirestoreModelsQuery(Asset, tenant_id, [],
                                        Asset.get_db_query_fields(tags))
    device_query = FirestoreModelsQuery(Device, tenant_id, [],
                                        Device.get_db_query_fields(tags))
    edges_query = FirestoreModelsQuery(Edge, tenant_id, [],
                                       Edge.get_db_query_fields(tags))
    gateway_query = FirestoreModelsQuery(Gateway, tenant_id, [],
                                         Gateway.get_db_query_fields(tags))

    db.add_query(
       [assets_groups, assets_query, device_query, edges_query, gateway_query]
    )

    r = db.get_query_results()

    return ProjectFirestoreModel(
        r[0], r[1], r[2], r[3], r[4]
    )


def get_assets_metrics(
    credentials,
    assets_ids: List[str],
    tenant_id: str
) -> List[AssetMetrics]:
    db = FirestoreModelsClient(credentials)

    for asset_id in assets_ids:
        db.add_query(
            FirestoreModelsQuery(
                AssetMetrics,
                tenant_id,
                [("asset_id", "==", asset_id)],
                AssetMetrics.get_db_query_fields([models_pb2.WEB_REQUIRED]),
                "asset_metrics/gao-001/assets",
                False
            )
        )

    r = db.get_query_results()
    r = list(map(
        lambda rls: rls[0] if rls else None,
        r
    ))
    r = list(filter(
        lambda rs: rs is not None,
        r
    ))
    return r
