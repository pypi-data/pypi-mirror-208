import urllib.parse
from http import HTTPStatus
from typing import Dict, Union

import httpx
import requests


def url_with_params(url: str, params: Dict[str, Union[str, int, None]]) -> str:
    params_skipping_none = dict(
        (k, v) for k, v in params.items() if v is not None
    )
    url_parse = urllib.parse.urlparse(url)
    url_new_query = urllib.parse.urlencode(params_skipping_none)
    url_parse = url_parse._replace(query=url_new_query)

    new_url = urllib.parse.urlunparse(url_parse)
    return str(new_url)


def require_ok_response(
    response: Union[requests.Response, httpx.Response]
) -> None:
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise Exception(
            f"Received response {response.status_code}:\n{response.text}\n\nUser not authenticated; please run `autumn8-cli login` to authorize your CLI"
        )
    if response.status_code != HTTPStatus.OK:
        raise Exception(
            f"Received response {response.status_code}:\n{response.text}"
        )
