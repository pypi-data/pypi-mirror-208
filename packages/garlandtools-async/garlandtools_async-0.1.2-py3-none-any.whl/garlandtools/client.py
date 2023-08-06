from typing import Any

from aiohttp import ClientSession

from garlandtools.models.lang import Lang
from garlandtools.models.records.base_record import BaseRecord
from garlandtools.models.records.factory import partial_factory, record_factory
from garlandtools.models.type import Type


class Client:
    base_url = "https://garlandtools.org/api/"

    def __init__(
        self,
        session: ClientSession | None = None,
        lang: Lang = Lang.EN,
    ):
        self._session = session
        self.lang = lang

    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession()
        return self._session

    async def search(
        self, query: str, type: Type | None = None, exact: bool = False
    ) -> list[BaseRecord]:
        """Search Garland Tools for the given query.

        Filters are not yet implemented.

        :param query: The query to search for.
        :param type: The record type you want to search for.
        :param exact: If the query should be an exact match.
        """
        params = {"text": query}
        if type is not None:
            params["type"] = type.value
        if exact:
            params["exact"] = "true"
        result = await self._get("search.php", params=params)

        return [partial_factory(r, client=self) for r in result]

    async def _get_by_id(self, id: int, type: Type):
        params = {
            "id": id,
            "type": type.value,
            "lang": self.lang.value,
            "version": 3 if type == type.LEVE or type == type.ITEM else 2,
        }
        return await self._get("get.php", params=params)

    async def get_by_id(self, id: int, type: Type):
        """Get a record by its ID.

        :param id: The ID of the record.
        :param type: The type of the record.
        :param lang: The language of the record.
        """
        result = await self._get_by_id(id, type)
        return record_factory(type, result, self)

    async def _get(self, path: str, params: dict | None = None) -> Any:
        url = self.base_url + path
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Received status code {response.status} from {url}")
