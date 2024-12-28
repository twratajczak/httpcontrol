from aiohttp import BasicAuth
from requests import Session
from xml.etree import ElementTree

class HttpcontrolAuthError(Exception):
    pass

DEFAULT_TIMEOUT = 3

async def async_get(
    path: str,
    host: str,
    username: str,
    password: str,
    session: Session,
):
    auth = BasicAuth(username, password) if username else None
    async with session.request(
        "GET",
        f"http://{host}/{path}",
        auth=auth,
        timeout=DEFAULT_TIMEOUT
    ) as response:
        if response.status == 401:
            raise HttpcontrolAuthError()
        response.raise_for_status()
        if response.headers["content-type"] == "text/xml":
            return { item.tag: item.text for item in ElementTree.fromstring(await response.text()) }
        elif response.headers["content-type"] == "application/json":
            return await response.json()
        else:
            return await response.text()
