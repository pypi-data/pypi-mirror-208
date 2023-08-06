import ast
import json
import logging
import time
from typing import Tuple, List, Optional, Any, Callable, Dict
from uuid import UUID

from rkclient.client import RKClient
from rkclient.entities import Artifact, PEM
from rkclient.request import _parse_sorting_filtering_params, RequestHelper
from rkclient.serialization import ArtifactSerialization, PEMSerialization, _decode_from_base64

log = logging.getLogger("rkclient")


class RKAdmin:
    """
    This class is not supposed to be used by normal RK user, but by RK administrator or in tests.
    """

    def __init__(self,
                 receiver_url: str,
                 graph_builder_url: str,
                 timeout_sec: int = 5,
                 insecure: bool = True,
                 user_auth: str = '',
                 puc_auth: str = ''):
        self.receiver_client = RKClient(receiver_url, emitter_id='admin', timeout_sec=timeout_sec, insecure=insecure,
                                        user_auth=user_auth, puc_auth=puc_auth)
        graph_builder_url = graph_builder_url.rstrip('/')
        log.info(f"Connecting to Graph Builder: {graph_builder_url}")
        self.graph_builder_client = RequestHelper(graph_builder_url, timeout_sec=timeout_sec, insecure=insecure,
                                                  user_auth=user_auth, puc_auth=puc_auth,
                                                  user_agent=f'recordkeeper-client-{self.receiver_client.get_version()}')

    def check_connections(self) -> Tuple[str, bool]:
        msg, ok = self.graph_builder_client.get("/info")
        if not ok:
            return f"Graph Builder connection error: {msg}", False
        msg, ok = self.receiver_client.get_info()
        if not ok:
            return f"Receiver connection error: {msg}", False
        return 'OK', True

    def graph_rebuild(self) -> Tuple[str, bool]:
        """
        :return: first element: error message or 'OK'
                 second element: True for success, False for error
        """
        text, ok = self.graph_builder_client.post("/rebuild", "{}")
        if not ok:
            return f"Starting rebuilding process failed: {text}", False
        return 'OK', True

    def graph_flush(self) -> Tuple[str, bool]:
        """
        Waits till all PEMs from queue have been added to graph.
        :return: first element: error message or 'OK'
                 second element: True for success, False for error
        """
        start_time = time.time()
        text, ok = self.graph_builder_client.post("/flush", "{}")
        total_flush_time = time.time() - start_time
        if not ok:
            return f"flushing queue failed: {text}", False
        return f"flushing queue finished, in {total_flush_time:.2f}s", True

    def graph_verify(self) -> Tuple[str, bool]:
        """
        Starts sql vs graph comparison, and returns result as string with newlines.
        :return: first element: error message or 'OK'
                 second element: True for success, False for error
        """
        text, ok = self.graph_builder_client.post("/verify", "{}")
        if not ok:
            return f"Verifying integrity failed: {text}", False
        return text, True

    def get_graph_info(self) -> Tuple[str, bool]:
        """
        Returns json with fields as in GraphBuilderInfo class - the GB state. Use `deserialize_graph_builder_info` for easy parsing.
        :return: check class description
        """
        text, ok = self.graph_builder_client.get("/info")
        return text, ok

    def clean_dbs(self) -> Tuple[str, bool]:
        """
        :return: first element: error message or 'OK'
                 second element: True for success, False for error
        """
        text, ok = self.receiver_client.receiver_request.post("/clean", "{}")
        if not ok:
            return f"Cleaning db failed: {text}", False
        return 'OK', True

    def get_pem(self, pem_id: str) -> Tuple[Optional[PEM], str, bool]:
        """
        Returns pem from sql db.
        :param pem_id: UUID, should be in hex format.
        :return: PEM or None
        """
        def _get_pem() -> Tuple[Optional[PEM], str, bool]:
            text, ok = self.receiver_client.receiver_request.get(f"/pem/{pem_id}")
            if not ok:
                return None, text, False
            pem_json = json.loads(text)
            pem = PEMSerialization.from_dict(pem_json, True)
            return pem, 'OK', True

        return _handle_request(_get_pem, "Getting pem")

    def get_pems(self,
                 page_index: int = -1,
                 page_size: int = -1,
                 sort_field: str = '',
                 sort_order: str = '',
                 filters: Optional[Dict] = None) -> Tuple[List[PEM], str, bool]:
        """
        Returns pems from sql db.
        :param page_index:
        :param page_size:
        :param sort_field:
        :param sort_order:
        :param filters: contains dict of key:value pairs, which all have to be contained in PEM fields to be returned.
                ID, Predecessor should be hex values of UUID (without dashes).
        :return: first element: list of pems (as json string) or error message
                 The artifacts lists in PEM will contain only artifact ID
                 second element: True for success, False for error
        """

        def _get_pems() -> Tuple[List[Any], str, bool]:
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(page_index, page_size,
                                                                           sort_field, sort_order, filters)
            text, ok = self.receiver_client.receiver_request.get("/pems", query_params)
            if not ok:
                return [], text, False
            pems = []
            pems_json = json.loads(text)
            for p in pems_json:
                pems.append(PEMSerialization.from_dict(p, True))
            return pems, 'OK', True

        return _handle_request(_get_pems, "Getting pems")

    def get_pems_count(self,
                       page_index: int = -1,
                       page_size: int = -1,
                       sort_field: str = '',
                       sort_order: str = '',
                       filters: Optional[Dict] = None) -> Tuple[int, str, bool]:
        """
        Returns amount of PEMs which match the filters. See `get_pems` for more info.
        """

        def _get_pems() -> Tuple[int, str, bool]:
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(page_index, page_size,
                                                                           sort_field, sort_order, filters)
            text, ok = self.receiver_client.receiver_request.get("/pems_count", query_params)
            if not ok:
                return -1, text, False
            obj = json.loads(text)
            return int(obj['pems_count']), 'OK', True

        return _handle_request(_get_pems, "Getting pems count")

    def get_artifact(self, artifact_name: str, source: str = 'sqldb') -> Tuple[Optional[Artifact], bool]:
        # todo this could be improved by using different endpoint
        res, text, ok = self.get_artifacts(source)
        if not ok:
            log.error(f"Getting artifact failed: {text}")
            return None, False

        artifacts: List[Artifact] = res
        for a in artifacts:
            if a.Name == artifact_name:
                return a, True

        return None, True

    def get_artifacts(self,
                      source: str = 'sqldb',
                      page_index: int = -1,
                      page_size: int = -1,
                      sort_field: str = '',
                      sort_order: str = '',
                      filters: Optional[Dict] = None) -> Tuple[List[Artifact], str, bool]:
        """
        :param source: from which db to return artifacts, 'sqldb' or 'graphdb'.
        :param page_index:
        :param page_size:
        :param sort_field:
        :param sort_order:
        :param filters: contains dict of key:value pairs, which all has to be contained in artifact to be returned
        :return: first element: list of artifact objs. Artifacts contain also the taxonomies ids and xml content.
                 second element: optional str error message
                 third element: True for success, False for error
        """
        if source == 'sqldb':
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(page_index, page_size,
                                                                           sort_field, sort_order, filters)
            return self._get_artifacts_from_sql(query_params)
        elif source == 'graphdb':
            return self._get_artifacts_from_graph()
        else:
            return [], f"Getting artifacts: didn't recognize source: {source}", False

    def get_artifacts_count(self,
                            source: str = 'sqldb',
                            filters: Optional[Dict] = None) -> Tuple[int, str, bool]:
        """
        :param source: from which db to return artifacts, 'sqldb' or 'graphdb'.
        :param filters: contains dict of key:value pairs, which all has to be contained in artifact to be counted
        :return: first element: count of artifact objs
                 second element: optional str error message
                 third element: True for success, False for error
        """

        def _get_artifacts_count_from_sql() -> Tuple[int, str, bool]:
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(-1, -1, "", "", filters)
            text, ok = self.receiver_client.receiver_request.get("/artifacts_count", query_params)
            if not ok:
                return -1, text, False
            objs = json.loads(text)
            return int(objs['artifacts_count']), "", True

        def _get_artifacts_count_from_graph() -> Tuple[int, str, bool]:
            text, ok = self.query_graph('MATCH (a:Artifact) RETURN count(a);', 'r')
            if not ok:
                return -1, text, False
            result = ast.literal_eval(text)
            return int(result[0][0]), "", True

        if source == 'sqldb':
            return _handle_request(_get_artifacts_count_from_sql, 'Getting artifacts count')
        elif source == 'graphdb':
            return _handle_request(_get_artifacts_count_from_graph, 'Getting artifacts count')
        else:
            return -1, f"Getting artifacts count: didn't recognize source: {source}", False

    def get_taxonomy_file(self, taxonomy_id: UUID) -> Tuple[str, bool]:
        text, ok = self.receiver_client.receiver_request.get(f"/taxonomy/{taxonomy_id.hex}")
        if not ok:
            return f"Getting taxonomy file failed: {text}", False
        return _decode_from_base64(text), True

    def get_tags(self) -> Tuple[List[Dict], str, bool]:
        """
        :return: first element: list of metadata (as Dict), with fields: NamespaceID, Tag, EventID, UpdatedAt
                 second element: error message
                 third element: True for success, False for error
        """

        def _get_tags() -> Tuple[List[Any], str, bool]:
            text, ok = self.receiver_client.receiver_request.get("/tags")
            if not ok:
                return [], text, False
            tags = json.loads(text)
            return tags, 'OK', True

        return _handle_request(_get_tags, "Getting tags")

    def get_tags_count(self) -> Tuple[int, str, bool]:
        """
        Returns amount of tags.
        """

        def _get_tags() -> Tuple[int, str, bool]:
            text, ok = self.receiver_client.receiver_request.get("/tags_count")
            if not ok:
                return -1, text, False
            obj = json.loads(text)
            return int(obj['tags_count']), 'OK', True

        return _handle_request(_get_tags, "Getting tags count")

    def query_graph(self, query: str, query_type='rw') -> Tuple[str, bool]:
        """
        :return: first element: returned result (as str with format corresponding to what query requests) or error message
                 second element: True for success, False for error
        """
        query_fmt = f'"query": "{query}", "type": "{query_type}"'
        payload = '{' + query_fmt + '}'
        return self.receiver_client.receiver_request.post("/query", payload)

    def _get_artifacts_from_sql(self, query_params: Dict[str, Any]) -> Tuple[List[Artifact], str, bool]:
        text, ok = self.receiver_client.receiver_request.get("/artifacts", query_params)
        if not ok:
            return [], f"Querying SQL failed: {text}", False

        objs = json.loads(text)
        artifacts: List[Artifact] = [ArtifactSerialization.from_dict(o) for o in objs]
        return artifacts, "", True

    def _get_artifacts_from_graph(self) -> Tuple[List[Artifact], str, bool]:
        text, ok = self.query_graph('MATCH (a:Artifact) RETURN a.rk_id AS rk_id, a.properties as properties, a.created_at as created_at')
        if not ok:
            return [], text, False

        # the text contains python like list [['<name>','<properties-as-json>'], ['<name>', ... ] ]
        objs = ast.literal_eval(text)
        artifacts: List[Artifact] = [
            create_artifact_from_neo4j(o)
            for o in objs
        ]
        return artifacts, "", True


def create_artifact_from_neo4j(result: tuple) -> Artifact:
    art = ArtifactSerialization.from_dict(
        {'Name': result[0],
         'Properties': json.loads(result[1]) if result[1] else {},
         'CreatedAt': result[2],
         'TaxonomyFiles': None}
    )
    return art


def _handle_request(func: Callable, name: str) -> Tuple[Any, str, bool]:
    """
    Wraps the error, logging and exception handling.
    """
    obj, text, ok = func()
    if not ok:
        text = f"{name} failed: {text}"
        log.error(text)
        return "", text, False
    return obj, 'OK', True
