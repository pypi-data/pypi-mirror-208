import logging
import time
from os import PathLike
from pathlib import Path
from typing import Optional, Union

import requests
import simplejson as json

logger = logging.getLogger(__name__)

PathLike = Union[str, PathLike, Path]


class AuthSerivceBase:
    @property
    def auth(self):
        raise NotImplementedError()


def make_request(
    url: str,
    body: dict = None,
    authorization: Optional[AuthSerivceBase] = None,
    retries: int = 3,
    method: str = "",
    **kwargs,
) -> dict:
    """

    Args:
        url: The url to send the request to.
        body: The body to send to the url. If not body is specified the GET method will
            be used. POST otherwise.
        authorization: Auth Service Object to handle Authentication.
        retries: Number of retries before aborting.
        method: HTTP Verb to use. Defaults to GET or POST (see body).
        **kwargs: Additional options which will be passed to requests call.

    Returns:
        The response as dictionary

    """
    auth = None
    if authorization:
        auth = authorization.auth
    exception = None
    ret = requests.Response()
    for i in range(retries):
        time.sleep(i**2)

        try:
            if not method:
                if body is None:
                    ret = requests.get(url, auth=auth, **kwargs)
                else:
                    ret = requests.post(url, json=body, auth=auth, **kwargs)
            else:
                if body:
                    kwargs["json"] = body
                ret = getattr(requests, method.lower())(url, auth=auth, **kwargs)
            ret.raise_for_status()

        except requests.RequestException as e:
            logger.warning("Failed to communicate with API:")
            logger.warning(e)
            logger.warning(ret.text)
            exception = e
            continue
        try:
            return ret.json()
        except json.JSONDecodeError as e:
            # Some APIs will return an empty response body which is also valid in this
            # case
            if ret.text == "":
                return {"success": True}
            exception = e
            continue
    raise ConnectionError(f"Failed to fetch data from {url}") from exception
