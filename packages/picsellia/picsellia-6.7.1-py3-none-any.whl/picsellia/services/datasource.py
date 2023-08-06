from functools import partial
from typing import List, Optional
from uuid import UUID

from orjson import orjson

from picsellia import exceptions
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.datasource import DataSource
from picsellia.utils import filter_payload


class DataSourceService:
    @classmethod
    def create_datasource(
        cls, connexion: Connexion, organization_id: UUID, name: str
    ) -> DataSource:
        params = {"name": name}
        r = connexion.post(
            f"/sdk/organization/{organization_id}/datasources",
            data=orjson.dumps(params),
        ).json()
        return DataSource(connexion, r)

    @classmethod
    def get_datasource(
        cls, connexion: Connexion, organization_id: UUID, name: str
    ) -> DataSource:
        params = {"name": name}
        r = connexion.get(
            f"/sdk/organization/{organization_id}/datasources/find",
            params=params,
        ).json()
        return DataSource(connexion, r)

    @classmethod
    def get_or_create_datasource(
        cls, connexion: Connexion, organization_id: UUID, name: str
    ) -> DataSource:
        try:
            return cls.get_datasource(connexion, organization_id, name)
        except exceptions.ResourceNotFoundError:
            return cls.create_datasource(connexion, organization_id, name)

    @classmethod
    def list_datasources(
        cls,
        connexion: Connexion,
        organization_id: UUID,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[DataSource]:
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        r = connexion.get(
            f"/sdk/organization/{organization_id}/datasources",
            params=params,
        ).json()
        return list(map(partial(DataSource, connexion), r["items"]))
