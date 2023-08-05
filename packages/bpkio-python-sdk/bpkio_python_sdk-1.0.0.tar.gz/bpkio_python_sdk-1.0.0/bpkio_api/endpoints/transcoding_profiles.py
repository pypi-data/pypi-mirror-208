from typing import Any, List, Tuple

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
from bpkio_api.exceptions import ResourceExistsError
from bpkio_api.helpers.list import get_all_with_pagination
from bpkio_api.helpers.objects import find_duplicates_of
from bpkio_api.helpers.search import SearchMethod, search_array_with_filters
from bpkio_api.models.TranscodingProfiles import (
    TranscodingProfile,
    TranscodingProfileIn,
)
from bpkio_api.response_handler import raise_for_status


@response_handler(raise_for_status)
class TranscodingProfilesApi(Consumer):
    def __init__(self, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)

    @returns.json()
    @get("transcoding-profiles")
    def get_page(
        self, offset: Query = 0, limit: Query = 50, tenantId: Query = None
    ) -> List[TranscodingProfile]:  # type: ignore
        """List all transcoding profiles"""

    @returns.json()
    @get("transcoding-profiles/{transcoding_profile_id}")
    def retrieve(
        self, transcoding_profile_id, tenantId: Query = None
    ) -> TranscodingProfile:
        """Get a single transcoding profile, by ID"""

    @json
    @returns.json()
    @post("transcoding-profiles")
    def create(self, profile: Body(type=TranscodingProfileIn)) -> TranscodingProfile:  # type: ignore
        """Create a new transcoding profile"""

    @json
    @returns.json()
    @put("transcoding-profiles/{transcoding_profile_id}")
    def update(self, transcoding_profile_id: int, profile: Body(type=TranscodingProfileIn)) -> TranscodingProfile:  # type: ignore
        """Update a transcoding profile"""

    @delete("transcoding-profiles/{transcoding_profile_id}")
    def delete(self, transcoding_profile_id):
        """Delete a single transcoding profile, by ID"""

    # === Helpers ===

    @cache_api_results("list_profiles")
    def list(self, tenantId: int = None):
        return get_all_with_pagination(self.get_page, tenantId=tenantId)

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        tenantId: int = None,
    ) -> List[TranscodingProfile]:
        """Searches the list of transcoding profiles for those matching a particular filter query

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

        profiles = self.list(tenantId=tenantId)
        return search_array_with_filters(profiles, filters=filters)

    def upsert(
        self,
        profile: TranscodingProfileIn,
        if_exists: str = "retrieve",
    ) -> Tuple[TranscodingProfile | TranscodingProfileIn, int,]:  # type: ignore
        """Creates a transcoding profile with adaptable behaviour if it already exist.

        Args:
            profile (TranscodingProfileIn): The payload for the source to create
            if_exists (str): What action to take if it exists:
              `error` (default) returns an error;
              `retrieve` returns the existing object;
              `update` updates the existing object.
            unique_fields (List[str | Tuple], optional): List of the fields
            or combination of fields to check for unicity. Defaults to [].

        Returns:
            Tuple[TranscodingProfile | None, int]:
                The resource created or retrieved, with an indicator: 1 = created, 0 = retrieved, 2 = updated, -1 = failed

        """

        try:
            return (self.create(profile), 1)
        except ResourceExistsError as e:
            if if_exists == "error":
                return (profile, -1)

            unique_fields = list(set("name"))
            for fld in unique_fields:
                # single field
                if isinstance(fld, str):
                    fld = (fld,)

                # find duplicates
                dupes = find_duplicates_of(
                    obj=profile, in_list=self.list(), by_fields=fld
                )
                if dupes:
                    existing_resource = self.retrieve(dupes[0][1].id)

                    if if_exists == "retrieve":
                        return (existing_resource, 0)
                    elif if_exists == "update":
                        updated_resource = self.update(existing_resource.id, profile)
                        return (updated_resource, 2)
