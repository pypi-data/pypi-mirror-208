import copy
import logging
from uuid import UUID
from typing import Dict, Optional, List

log = logging.getLogger("rkclient")

"""
PEM and Artifact

Both are used by objects constructed by RKClient in memory,
and for objects constructed from http responses from Receiver.

ADR 2 - naming of member variables using PascalCase

"""


class Artifact:

    def __init__(self,
                 name: str,
                 properties: Dict[str, str],
                 solely_id: bool = False
                 ):
        self.Name = name
        self.Properties = properties
        self.CreatedAt: Optional[str] = None
        self.TaxonomyFiles: Optional[Dict] = None
        self.SolelyID = solely_id

    def add_taxonomy_file(self, file_id: UUID, content: str):
        if self.TaxonomyFiles is None:
            self.TaxonomyFiles = {}
        self.TaxonomyFiles[file_id.hex] = content

    def __str__(self):
        if self.SolelyID:
            return self.Name
        return f"Artifact({self.Name}, {self.Properties}, {self.CreatedAt})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: object):
        if isinstance(other, Artifact):
            return self.Name == other.Name and \
                self.Properties == other.Properties
        return False


class PEM:

    def __init__(self,
                 id: UUID,
                 pem_type: str,
                 predecessor_id: Optional[UUID],
                 emitter_id: str,
                 timestamp_client: str):
        self.ID = id
        self.Type = pem_type
        self.Predecessor = predecessor_id
        self.Emitter = emitter_id
        self.TimestampClient = timestamp_client  # UTC time in format YYYY-MM-DD HH:MM:SS
        self.UsesArtifacts: List[Artifact] = []
        self.ProducesArtifacts: List[Artifact] = []
        self.TimestampReceived = ''
        self.Properties: dict = {}
        self.Version = '2.0.0'
        self.Tag = ''
        self.TagNamespace = ''

    def uses_artifact(self, artifact: Artifact):
        """
        Add artifact as used by PEM.
        Avoids adding to "uses artifacts" list already stored there artifact.
        :param artifact: to add
        """
        for art in self.UsesArtifacts:
            # Todo this protection should be also checked on backend.
            if art.Name == artifact.Name:
                log.warning(f"Not adding \"uses artifact\" with name {artifact.Name} to PEM {self.ID},"
                            f" because one with such Name already exists in list.")
                return

        duplicated_artifact = copy.deepcopy(artifact)
        duplicated_artifact.Properties = {}
        self.UsesArtifacts.append(duplicated_artifact)

    def produces_artifact(self, artifact: Artifact):
        self.ProducesArtifacts.append(artifact)

    def __str__(self):
        return f"PEM({self.ID.hex}, {self.Type}, {self.Predecessor}, {self.Properties}, {self.TimestampClient}, " \
               f"uses: {self.UsesArtifacts}, produces: {self.ProducesArtifacts})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.ID == other.ID and \
            self.Type == other.Type and \
            self.Properties == other.Properties
