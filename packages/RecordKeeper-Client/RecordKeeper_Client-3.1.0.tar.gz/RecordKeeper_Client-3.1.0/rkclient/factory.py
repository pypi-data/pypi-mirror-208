import os
import time
import datetime
import logging
from uuid import UUID, uuid1
from typing import Dict, Optional, Tuple
from importlib.metadata import version

from rkclient.client import RKClient
from rkclient.entities import PEM, Artifact

log = logging.getLogger("rkclient")

RK_VERSION = version('RecordKeeper_Client')
MOCK_ENV_VAR = "RK_MOCK"


class RKClientMock(RKClient):
    def __init__(self, receiver_url: str, emitter_id: str, timeout_sec: int = 5, user_auth: str = ''): # noqa
        log.info(f"ver {RK_VERSION} - using MOCK client")
        self.emitter_id = emitter_id

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def prepare_pem(self,
                    pem_type: str,
                    predecessor_id: Optional[UUID] = None,
                    properties: Optional[Dict] = None,
                    tag_name: str = 'latest',
                    tag_namespace: Optional[str] = None) -> PEM:
        now = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        pem = PEM(uuid1(), pem_type, predecessor_id, 'mock-client', now)
        if properties is not None:
            pem.Properties = properties
        return pem

    def prepare_artifact(self,
                         name: str,
                         properties: Dict[str, str]) -> Artifact:
        return Artifact(name, properties, False)

    def send_pem(self, pem: PEM) -> Tuple[str, bool]:
        log.debug("send pem - mocked")
        return "", True

    def get_info(self) -> Tuple[str, bool]:
        log.debug("get info - mocked")
        return "{'pem_size_limit': 10000, 'version':" + RK_VERSION + "} ", True

    def get_tag(self, namespace: str, tag_name: str) -> Tuple[str, bool]:
        log.debug("get tag - mocked")
        return "", True

    def set_tag(self, namespace: str, tag_name: str, pem: PEM) -> Tuple[str, bool]:
        log.debug("set tag - mocked")
        return "", True


class RKClientFactory:

    @staticmethod
    def get(*args, **kwargs) -> RKClient:
        rk_mock = os.environ.get(MOCK_ENV_VAR)
        if rk_mock is not None and rk_mock.lower() == 'true':
            return RKClientMock(*args, **kwargs)
        else:
            return RKClient(*args, **kwargs)
