from typing import Any, List, Tuple
from urllib.parse import urlparse, urlunparse

from uplink import (
    Body,
    Consumer,
    Query,
    delete,
    get,
    json,
    post,
    put,
    response_handler,
    returns,
)

from bpkio_api.caching import cache_api_results
from bpkio_api.exceptions import BroadpeakIoHelperError, ResourceExistsError
from bpkio_api.helpers.list import collect_from_ids, get_all_with_pagination
from bpkio_api.helpers.objects import find_duplicates_of
from bpkio_api.helpers.search import SearchMethod, search_array_with_filters
from bpkio_api.models import Sources as S
from bpkio_api.response_handler import raise_for_status


@response_handler(raise_for_status)
class SourcesApi(Consumer):
    def __init__(self, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)

        self.asset = AssetSourcesApi(parent_api=self, base_url=base_url, **kwargs)
        self.live = LiveSourcesApi(parent_api=self, base_url=base_url, **kwargs)
        self.asset_catalog = AssetCatalogSourcesApi(
            parent_api=self, base_url=base_url, **kwargs
        )
        self.ad_server = AdServerSourcesApi(
            parent_api=self, base_url=base_url, **kwargs
        )
        self.slate = SlateSourcesApi(parent_api=self, base_url=base_url, **kwargs)

    def _mappings(self, model):
        match model:
            case S.AssetSourceIn():
                return self.asset
            case S.LiveSourceIn():
                return self.live
            case S.AdServerSourceIn():
                return self.ad_server
            case S.AssetCatalogSourceIn():
                return self.asset_catalog
            case S.SlateSourceIn():
                return self.slate
            case _:
                raise Exception(
                    f"Model {model.__class__.__name__} not recognised as a valid source type"
                )

    @returns.json()
    @get("sources")
    def get_page(self, offset: Query = 0, limit: Query = 5) -> List[S.SourceSparse]:  # type: ignore
        """Get a partial list of Sources"""

    @returns.json()
    @get("sources/{type}/check")
    def check(self, type: S.SourceType, url: Query) -> List[S.SourceCheckResult]:
        """Check a URL for compliance as a Source"""

    # === Helpers ===

    @cache_api_results("list_sources")
    def list(self):
        return get_all_with_pagination(self.get_page)

    def search_by_type(self, type: S.SourceType) -> List[S.SourceSparse]:
        all_items = self.list()
        return [i for i in all_items if i.type == type]

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
    ) -> List[S.SourceSparse]:
        """Searches the list of sources for those matching a particular filter query

        You can search for full or partial matches in all or specific fields.
        All searches are done as string matches (regarding of the actual type of each field)

        Args:
            value (Any, optional): The string value to search. Defaults to None.
            field (str, optional): The field name in which to search for the value.
                Defaults to None.
            method (SearchMethod, optional): How to perform the search.
                SearchMethod.STRING_SUB searches for partial string match. This is the default.
                SearchMethod.STRING_MATCH searches for a complete match (after casting to string).
                SearchMethod.STRICT searches for a strict match (including type)
            filters (List[Tuple[Any, Optional[str], Optional[SearchMethod]]], optional):
                Can be used as an alternatitve to using `value`, `field` and `method`,
                in particular if multiple search patterns need to be specified
                (which are then treated as logical `AND`). Defaults to None.

        Returns:
            List[Svc.SourceSpare]: List of matching sources
        """
        if not filters:
            filters = [(value, field, method)]

        sources = self.list()
        return search_array_with_filters(sources, filters=filters)

    def retrieve(
        self, source_id: int
    ) -> (
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
        | None
    ):
        """Gets a source by its ID

        This is a helper method that allows you to get the full Source sub-type (eg. asset, asset-catalog)
        without having to know its type in advance and calling the specific endpoint

        Args:
            source_id (int): The source identifier

        Raises:
            e: _description_

        Returns:
            AssetSource | AssetCatalogSource | LiveSource | AdServerSource | SlateSource : A specific sub-type of source
        """

        candidates = self.search(int(source_id), field="id", method=SearchMethod.STRICT)
        try:
            source = candidates[0]
            match source.type:
                case S.SourceType.ASSET:
                    return self.asset.retrieve(source_id)
                case S.SourceType.ASSET_CATALOG:
                    return self.asset_catalog.retrieve(source_id)
                case S.SourceType.LIVE:
                    return self.live.retrieve(source_id)
                case S.SourceType.SLATE:
                    return self.slate.retrieve(source_id)
                case S.SourceType.AD_SERVER:
                    return self.ad_server.retrieve(source_id)
                case _:
                    raise BroadpeakIoHelperError(
                        status_code=404,
                        message=f"Source type not supported: {source.type}",
                        original_message="",
                    )
        except IndexError as e:
            raise BroadpeakIoHelperError(
                status_code=404,
                message=f"There is no source with ID {source_id}",
                original_message=e.args[0],
            )

    def create(
        self, source: S.SourceIn
    ) -> (
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
    ):
        """Create a source"""
        endpoint = self._mappings(source)
        return endpoint.create(source)

    def _update(
        self, source_id: int, source: S.SourceIn
    ) -> (
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
    ):
        """Update a source"""
        endpoint = self._mappings(source)
        return endpoint.update(source_id, source)

    def upsert(
        self,
        source: S.SourceIn,
        if_exists: str = "retrieve",
        unique_fields: List[str | Tuple] = [],
    ) -> Tuple[
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
        | S.SourceIn,
        int,
    ]:
        """Creates a source with adaptable behaviour if it already exist.

        Args:
            source (SourceIn): The payload for the source to create
            if_exists (str): What action to take if it exists:
              `error` (default) returns an error;
              `retrieve` returns the existing object;
              `update` updates the existing object.
            unique_fields (List[str | Tuple], optional): List of the fields
            or combination of fields to check for unicity. Defaults to [].

        Returns:
            Tuple[AssetSource | AdServerSource | AssetCatalogSource | SlateSource | LiveSource | None, int]:
            The resource created or retrieved, with an indicator: 1 = created, 0 = retrieved, 2 = updated, -1 = failed

        """

        try:
            return (self.create(source), 1)
        except ResourceExistsError as e:
            if if_exists == "error":
                return (source, -1)

            unique_fields = list(set(unique_fields + ["name"]))
            for fld in unique_fields:
                # single field
                if isinstance(fld, str):
                    fld = (fld,)

                # find duplicates
                dupes = find_duplicates_of(
                    obj=source, in_list=self.list(), by_fields=fld
                )
                if dupes:
                    existing_resource = self.retrieve(dupes[0][1].id)

                    if if_exists == "retrieve":
                        return (existing_resource, 0)
                    elif if_exists == "update":
                        updated_resource = self._update(existing_resource.id, source)
                        return (updated_resource, 2)

    def check_by_id(self, source_id: int) -> List[S.SourceCheckResult]:
        source = self.retrieve(source_id=source_id)

        if source:
            url = source.url
            if source.type == S.SourceType.ASSET_CATALOG:
                url = url + source.assetSample

            return self.check(type=source.type, url=url)


# === ASSET SOURCES ===


@response_handler(raise_for_status)
class AssetSourcesApi(Consumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.AssetSource)
    @get("sources/asset/{source_id}")
    def retrieve(self, source_id):
        """Get a single asset source, by ID"""

    @json
    @returns.json(S.AssetSource)
    @post("sources/asset")
    def create(self, source: Body(type=S.AssetSourceIn)) -> S.AssetSource:  # type: ignore
        """Create a new asset source"""

    @json
    @returns.json(S.AssetSource)
    @put("sources/asset/{source_id}")
    def update(self, source_id: int, source: Body(type=S.AssetSourceIn)) -> S.AssetSource:  # type: ignore
        """Update an asset source"""

    @delete("sources/asset/{source_id}")
    def delete(self, source_id: int):
        """Delete an asset source, by ID"""

    def upsert(
        self, source: S.AssetSourceIn, if_exists: str = "retrieve"
    ) -> Tuple[S.AssetSource, int]:
        """Conditionally create, retrieve or update an Asset source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_assets")
    def list(self) -> List[S.AssetSource]:
        """List all Asset sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.ASSET, field="type", method=SearchMethod.STRICT
        )
        return collect_from_ids(
            ids=[src.id for src in sparse_sources], get_fn=self.retrieve
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
    ) -> List[S.AssetSource]:
        """Search the list of Asset sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list()
        return search_array_with_filters(sources, filters=filters)


# === LIVE SOURCES ===


@response_handler(raise_for_status)
class LiveSourcesApi(Consumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.LiveSource)
    @get("sources/live/{source_id}")
    def retrieve(self, source_id):
        """Get a single live source, by ID"""

    @json
    @returns.json(S.LiveSource)
    @post("sources/live")
    def create(self, source: Body(type=S.LiveSourceIn)) -> S.LiveSource:  # type: ignore
        """Create a new live source"""

    @json
    @returns.json(S.LiveSource)
    @put("sources/live/{source_id}")
    def update(self, source_id: int, source: Body(type=S.LiveSourceIn)) -> S.LiveSource:  # type: ignore
        """Update a live source"""

    @delete("sources/live/{source_id}")
    def delete(self, source_id: int):
        """Delete a live source, by ID"""

    def upsert(
        self, source: S.LiveSourceIn, if_exists: str | None = None
    ) -> Tuple[S.LiveSource, int]:
        """Conditionally create, retrieve or update a Live source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_live")
    def list(self) -> List[S.LiveSource]:
        """List all Live sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.LIVE, field="type", method=SearchMethod.STRICT
        )
        return collect_from_ids(
            ids=[src.id for src in sparse_sources], get_fn=self.retrieve
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
    ) -> List[S.LiveSource]:
        """Search the list of Live sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list()
        return search_array_with_filters(sources, filters=filters)


# === ASSET CATALOG SOURCES ===


@response_handler(raise_for_status)
class AssetCatalogSourcesApi(Consumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.AssetCatalogSource)
    @get("sources/asset-catalog/{source_id}")
    def retrieve(self, source_id):
        """Get a single asset catalog source, by ID"""

    @json
    @returns.json(S.AssetCatalogSource)
    @post("sources/asset-catalog")
    def create(self, source: Body(type=S.AssetCatalogSourceIn)) -> S.AssetCatalogSource:  # type: ignore
        """Create a new asset catalog source"""

    @json
    @returns.json(S.AssetCatalogSource)
    @put("sources/asset-catalog/{source_id}")
    def update(self, source_id: int, source: Body(type=S.AssetCatalogSourceIn)) -> S.AssetCatalogSource:  # type: ignore
        """Updates an asset source"""

    @delete("sources/asset-catalog/{source_id}")
    def delete(self, source_id: int):
        """Delete an asset catalog source, by ID"""

    def upsert(
        self, source: S.AssetCatalogSourceIn, if_exists: str | None = None
    ) -> Tuple[S.AssetCatalogSource, int]:
        """Conditionally create, retrieve or update an Asset Catalog source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_assetcatalogs")
    def list(self) -> List[S.AssetCatalogSource]:
        """List all Asset Catalog sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.ASSET_CATALOG, field="type", method=SearchMethod.STRICT
        )
        return collect_from_ids(
            ids=[src.id for src in sparse_sources], get_fn=self.retrieve
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
    ) -> List[S.AssetCatalogSource]:
        """Search the list of Asset Catalog sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list()
        return search_array_with_filters(sources, filters=filters)


# === AD SERVER SOURCES ===


@response_handler(raise_for_status)
class AdServerSourcesApi(Consumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.AdServerSource)
    @get("sources/ad-server/{source_id}")
    def retrieve(self, source_id):
        """Get a single ad server source, by ID"""

    @json
    @returns.json(S.AdServerSource)
    @post("sources/ad-server")
    def create(self, source: Body(type=S.AdServerSourceIn)) -> S.AdServerSource:  # type: ignore
        """Create a new ad server source"""

    @json
    @returns.json(S.AdServerSource)
    @put("sources/ad-server/{source_id}")
    def update(self, source_id: int, source: Body(type=S.AdServerSourceIn)) -> S.AdServerSource:  # type: ignore
        """Update an Ad Server source"""

    @delete("sources/ad-server/{source_id}")
    def delete(self, source_id: int):
        """Delete an ad server source, by ID"""

    def upsert(
        self, source: S.AdServerSourceIn, if_exists: str | None = None
    ) -> Tuple[S.AdServerSource, int]:
        """Conditionally create, retrieve or update an Ad Server source"""
        return self.parent_api.upsert(
            source, unique_fields=["url", "queries"], if_exists=if_exists
        )

    def create_from_url(self, name: str, url: str) -> S.AdServerSource:
        """Convenience function to create an ad-server from a full URL

        Args:
            name (str): Name of the Ad Server source
            url (str): The full URL, including query parameters

        Returns:
            AdServerSource: the created Ad Server source
        """

        def split_url(url: str):
            parsed_url = urlparse(url)

            # Reconstruct the URL without the query part
            first_part = urlunparse(parsed_url._replace(query=""))

            # Get the query part
            second_part = parsed_url.query

            return first_part, second_part

        parts = split_url(url)
        ad_server_source = S.AdServerSourceIn(
            name=name, url=parts[0], queries=parts[1], description=None
        )
        return self.create(ad_server_source)

    @cache_api_results("list_adservers")
    def list(self) -> List[S.AdServerSource]:
        """List all Ad Server sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.AD_SERVER, field="type", method=SearchMethod.STRICT
        )
        return collect_from_ids(
            ids=[src.id for src in sparse_sources], get_fn=self.retrieve
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
    ) -> List[S.AdServerSource]:
        """Searches the list of Ad Server sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list()
        return search_array_with_filters(sources, filters=filters)


# === SLATE SOURCES ===


@response_handler(raise_for_status)
class SlateSourcesApi(Consumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.SlateSource)
    @get("sources/slate/{source_id}")
    def retrieve(self, source_id):
        """Get a single slate source, by ID"""

    @json
    @returns.json(S.SlateSource)
    @post("sources/slate")
    def create(self, source: Body(type=S.SlateSourceIn)) -> S.SlateSource:  # type: ignore
        """Create a new slate source"""

    @json
    @returns.json(S.SlateSource)
    @put("sources/slate/{source_id}")
    def update(self, source_id: int, source: Body(type=S.SlateSourceIn)) -> S.SlateSource:  # type: ignore
        """Update a slate source"""

    @delete("sources/slate/{source_id}")
    def delete(self, source_id: int):
        """Delete a slate source, by ID"""

    def upsert(
        self, source: S.SlateSourceIn, if_exists: str | None = None
    ) -> Tuple[S.SlateSource, int]:
        """Conditionally create, retrieve or update a slate source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_slates")
    def list(self) -> List[S.SlateSource]:
        """List all Slate sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.SLATE, field="type", method=SearchMethod.STRICT
        )
        return collect_from_ids(
            ids=[src.id for src in sparse_sources], get_fn=self.retrieve
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
    ) -> List[S.SlateSource]:
        """Searches the list of Slate sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list()
        return search_array_with_filters(sources, filters=filters)
