from .config import BASE_URL, API_VERSION
from .Session import session
from typing import Union, Any


class Domain:

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    @property
    def endpoint_url(self):
        return f"{BASE_URL}/{self.__class__.__name__.lower()}"

    @classmethod
    def convert_to_dict(cls, json) -> Union[list[Any], Any]:
        results = []
        for record in json:
            record = record.items()
            results.append(record)

        return results

    @classmethod
    def get(cls, id=None, quote=False, limit=10, page=1, offset=0):

        url = f"{BASE_URL}/{API_VERSION}/{cls.__name__.lower()}"
        url = f"{url}/{id}" if id else url
        url = f"{url}/quote" if quote and id else url
        url = f"{url}?limit={limit}"
        url = f"{url}&page={page}"
        url = f"{url}&offset={offset}"
        resp = session.get(url)

        return cls.convert_to_dict(resp.json()["docs"])

    @classmethod
    def get_quotes(self, id=None):
        self.get(id = id, quote=True)
