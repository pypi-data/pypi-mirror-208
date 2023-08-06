import ssl
import logging
import urllib.parse
import urllib.request
from _socket import timeout
from typing import Optional, Dict, Any, Tuple
from urllib.error import HTTPError, URLError

from rkclient.auth import RK_USER_AUTH_HEADER, RK_PUC_AUTH_HEADER

log = logging.getLogger("rkclient")


class RequestHelper:

    def __init__(self, url: str, timeout_sec: int = 5, insecure: bool = True, user_auth: str = '', puc_auth: str = '', user_agent: str = ''):
        self.url = url
        self.timeout_sec = timeout_sec
        self.user_auth = user_auth
        self.puc_auth = puc_auth
        self.insecure = insecure
        self.user_agent = user_agent

    def get(self, url_postfix: str, query_params: Optional[Dict[str, Any]] = None) -> Tuple[str, bool]:
        url = self.url + url_postfix + _encode_query_params(query_params)
        req = urllib.request.Request(url=url)
        if self.user_auth:
            req.add_header(RK_USER_AUTH_HEADER, self.user_auth)
        elif self.puc_auth:
            req.add_header(RK_PUC_AUTH_HEADER, self.puc_auth)
        return self._make_request(req)

    def post(self, url_postfix: str, payload: str, query_params: Optional[Dict[str, Any]] = None) -> Tuple[str, bool]:
        url = self.url + url_postfix + _encode_query_params(query_params)
        req = urllib.request.Request(url=url, data=payload.encode())
        req.add_header('Content-Type', 'application/json')
        if self.user_auth:
            req.add_header(RK_USER_AUTH_HEADER, self.user_auth)
        elif self.puc_auth:
            req.add_header(RK_PUC_AUTH_HEADER, self.puc_auth)
        return self._make_request(req)

    def _make_request(self, request: urllib.request.Request):
        try:
            if not request.has_header('User-Agent'):
                request.add_header('User-Agent', self.user_agent)
            resp = urllib.request.urlopen(request, timeout=self.timeout_sec, context=self._get_ssl_context())
        except HTTPError as e:
            return f"error for {request.full_url}: {e} {e.read().decode()}", False
        except URLError as e:
            return f"connection error for {request.full_url}: {e}", False
        except timeout as e:
            return f"socket timed out in {self.timeout_sec}s for {request.full_url}: {e}", False
        else:
            return resp.read().decode(), True

    def _get_ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        if self.insecure:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx


def _encode_query_params(query_params: Optional[Dict[str, Any]]) -> str:
    if query_params is None or len(query_params) == 0:
        return ''
    encoded_params = urllib.parse.urlencode(query_params)
    return '?' + encoded_params


def _parse_sorting_filtering_params(
        page_index: int = -1,
        page_size: int = -1,
        sort_field: str = '',
        sort_order: str = '',
        filters: Optional[Dict] = None) -> Dict[str, Any]:

    if filters is None:
        filters = {}
    params: Dict[str, Any] = {}
    if page_index != -1:
        params['pageIndex'] = page_index
    if page_size != -1:
        params['pageSize'] = page_size
    if sort_field != '':
        params['sortField'] = sort_field
    if sort_order != '':
        params['sortOrder'] = sort_order

    for key, value in filters.items():
        params[key] = value
    return params

