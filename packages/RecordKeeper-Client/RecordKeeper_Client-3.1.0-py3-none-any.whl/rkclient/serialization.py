import base64
import json
from json import JSONDecodeError

from uuid import UUID
from typing import Dict, Optional
from dataclasses import dataclass

from rkclient.entities import Artifact, PEM


class ArtifactSerialization:

    @staticmethod
    def from_json(txt: str) -> Artifact:
        obj = json.loads(txt)
        return ArtifactSerialization.from_dict(obj)

    @staticmethod
    def to_dict(artifact: Artifact) -> Dict:
        obj = {
            "Name": artifact.Name,
            "Properties": artifact.Properties,
            "CreatedAt": artifact.CreatedAt,
            "TaxonomyFiles": None,
        }
        if artifact.TaxonomyFiles is not None:
            obj["TaxonomyFiles"] = {tkey: _encode_as_base64(tval) for tkey, tval in artifact.TaxonomyFiles.items()}
        return obj

    @staticmethod
    def from_dict(d: Dict) -> Artifact:
        artifact = Artifact(
            name=d['Name'],
            properties=d['Properties'],
        )
        artifact.CreatedAt = d['CreatedAt']
        artifact.TaxonomyFiles = None
        if d['TaxonomyFiles'] is not None:
            artifact.TaxonomyFiles = {tkey: _decode_from_base64(tval) for tkey, tval in d['TaxonomyFiles'].items()}
        return artifact


class PEMSerialization:

    @staticmethod
    def to_json(pem: PEM) -> str:
        pred_id = None
        if pem.Predecessor is not None:
            pred_id = pem.Predecessor.hex
        obj = {
            "ID": pem.ID.hex,
            "Type": pem.Type,
            "Predecessor": pred_id,
            "Emitter": pem.Emitter,
            "TimestampClient": pem.TimestampClient,
            "TimestampReceived": pem.TimestampReceived,
            "Properties": pem.Properties,
            "Version": pem.Version,
            "Tag": pem.Tag,
            "TagNamespace": pem.TagNamespace,
            "UsesArtifacts": [ArtifactSerialization.to_dict(a) for a in pem.UsesArtifacts],
            "ProducesArtifacts": [ArtifactSerialization.to_dict(a) for a in pem.ProducesArtifacts],
        }
        return json.dumps(obj)

    @staticmethod
    def from_json(txt: str) -> PEM:
        obj = json.loads(txt)
        return PEMSerialization.from_dict(obj)

    @staticmethod
    def from_dict(obj: Dict, art_solely_id: bool = False) -> PEM:
        pred = None
        if obj["Predecessor"] is not None:
            pred = UUID(hex=obj["Predecessor"])

        pem = PEM(UUID(hex=obj["ID"]),
                  obj["Type"],
                  pred,
                  obj["Emitter"],
                  obj["TimestampClient"])
        pem.Properties = obj["Properties"]
        pem.Tag = obj["Tag"]
        pem.TagNamespace = obj["TagNamespace"]

        if art_solely_id:
            pem.UsesArtifacts = [Artifact(name, {}, True) for name in obj["UsesArtifacts"]]
            pem.ProducesArtifacts = [Artifact(name, {}, True) for name in obj["ProducesArtifacts"]]
        else:
            pem.UsesArtifacts = [ArtifactSerialization.from_dict(a) for a in obj["UsesArtifacts"]]
            pem.ProducesArtifacts = [ArtifactSerialization.from_dict(a) for a in obj["ProducesArtifacts"]]
        return pem


def _encode_as_base64(content: str) -> str:
    content_bytes = content.encode()
    content_base64_bytes = base64.b64encode(content_bytes)
    content_base64 = content_base64_bytes.decode()
    return content_base64


def _decode_from_base64(content_base64: str) -> str:
    content_base64_bytes = content_base64.encode()
    content_bytes = base64.b64decode(content_base64_bytes)
    content = content_bytes.decode()
    return content


@dataclass
class Info:
    version: str
    pem_version: str
    pem_size_limit: int
    auth_required: bool
    pem_auth_required: bool


def deserialize_info(s: str) -> Optional[Info]:
    try:
        json_obj = json.loads(s)
        return Info(**json_obj)
    except JSONDecodeError:
        return None


@dataclass
class GraphBuilderInfo:
    version: str
    pg_pems_count: int
    pg_artifacts_count: int
    neo4j_pems_count: int
    neo4j_artifacts_count: int
    pems_sync_pct: str
    artifacts_sync_pct: str
    loop_iteration_interval: int
    loop_state_should_rebuild: str  # 'False', 'True', or error message
    loop_state_should_flush: str    # 'False', 'True', or error message


def deserialize_graph_builder_info(s: str) -> Optional[GraphBuilderInfo]:
    try:
        json_obj = json.loads(s)
        return GraphBuilderInfo(**json_obj)
    except JSONDecodeError:
        return None

