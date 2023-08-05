from typing import Any, Dict, List, Optional

from aiohttp import ClientSession

from garlandtools.models import Lang, Type


class Client:
    base_url = "https://garlandtools.org/api/"

    def __init__(self, session: Optional[ClientSession] = None):
        self._session = session

    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession()
        return self._session

    async def search(
        self, query: str, type: Optional[Type], exact: Optional[bool] = False
    ) -> List[Dict]:
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

        return result

    def get_by_id(self, id: int, type: Type, lang: Lang):
        """Get a record by its ID.

        :param id: The ID of the record.
        :param type: The type of the record.
        :param lang: The language of the record.
        """

    async def _get(self, path: str, params: Optional[dict] = None) -> Any:
        url = self.base_url + path
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Received status code {response.status} from {url}")
