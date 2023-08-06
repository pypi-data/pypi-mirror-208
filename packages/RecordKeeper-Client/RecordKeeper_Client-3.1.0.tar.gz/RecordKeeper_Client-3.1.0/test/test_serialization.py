import json
import unittest
from uuid import UUID

from rkclient import PEM, Artifact, PEMSerialization, ArtifactSerialization

tax_id = UUID("a606c8ea-39a1-11eb-8ad6-0a9a235141b0")
tax_content = '<xml>El Niño</xml>'
tax_content_base64 = 'PHhtbD5FbCBOacOxbzwveG1sPg=='

sample_art = '{"Name": "Foobar", "Properties": {"foo": "baz"},' \
             ' "CreatedAt": "2020-12-08 22:06:40", "TaxonomyFiles": null}'

sample_uses_art = '{"Name": "Foobar", "Properties": {},' \
                  ' "CreatedAt": "2020-12-08 22:06:40", "TaxonomyFiles": null}'

sample_art_tax = '{"Name": "Foobar", "Properties": {"foo": "baz"},' \
                 ' "CreatedAt": "2020-12-08 22:06:40", ' \
                 '"TaxonomyFiles": {"' + tax_id.hex + '": "' + tax_content_base64 + '"}}'

sample_uses_art_tax = '{"Name": "Foobar", "Properties": {},' \
                      ' "CreatedAt": "2020-12-08 22:06:40", ' \
                      '"TaxonomyFiles": {"' + tax_id.hex + '": "' + tax_content_base64 + '"}}'

sample_pem = '{"ID": "a606c8ea39a111eb8ad60a9a235141b0", "Type": "ingest", "Predecessor": null,' \
             ' "Emitter": "serialization_test_1", "TimestampClient": "2020-12-08 22:06:40",' \
             ' "TimestampReceived": "", "Properties": {"filename": "data.csv"}, "Version": "2.0.0",' \
             ' "Tag": "", "TagNamespace": "", "UsesArtifacts": [], "ProducesArtifacts": []}'


def get_sample_pem(uses_artifact: str, produces_artifact: str = ''):
    return '{"ID": "a606c8ea39a111eb8ad60a9a235141b0", "Type": "ingest", "Predecessor": null,' \
           ' "Emitter": "serialization_test_2", "TimestampClient": "2020-12-08 22:06:40",' \
           ' "TimestampReceived": "", "Properties": {"filename": "data.csv"},' \
           ' "Version": "2.0.0", "Tag": "", "TagNamespace": "", "UsesArtifacts": [' + uses_artifact + '],' \
           ' "ProducesArtifacts": [' + produces_artifact + ']}'


class TestPEMSerializationUnit(unittest.TestCase):

    def test_serialize(self):
        self.maxDiff = None
        pem = PEM(UUID("a606c8ea-39a1-11eb-8ad6-0a9a235141b0"), "ingest", None,
                  "serialization_test_1", "2020-12-08 22:06:40")
        pem.Properties = {'filename': 'data.csv'}
        pem_json = PEMSerialization.to_json(pem)

        self.assertEqual(sample_pem, pem_json)

    def test_deserialize(self):
        pem = PEMSerialization.from_json(sample_pem)

        self.assertEqual(str(pem.ID), 'a606c8ea-39a1-11eb-8ad6-0a9a235141b0')
        self.assertEqual(pem.Predecessor, None)
        self.assertEqual(str(pem.Emitter), 'serialization_test_1')
        self.assertEqual(pem.Type, 'ingest')
        self.assertEqual(pem.TimestampClient, '2020-12-08 22:06:40')
        self.assertEqual(pem.TimestampReceived, '')
        self.assertEqual(pem.Properties, {'filename': 'data.csv'})
        self.assertEqual(pem.Version, '2.0.0')
        self.assertEqual(pem.Tag, '')
        self.assertEqual(pem.TagNamespace, '')


# todo test serialize/deserialize PEM in format returned from Postgres, which contains only Artifact ID
class TestPEMArtifactSerializationUnit(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.pem = PEM(UUID("a606c8ea-39a1-11eb-8ad6-0a9a235141b0"), "ingest", None,
                       "serialization_test_2", "2020-12-08 22:06:40")

        self.art1 = Artifact('Foobar', {'foo': 'baz'})
        self.art1.CreatedAt = "2020-12-08 22:06:40"

    def test_serialize_uses(self):
        self.pem.Properties = {'filename': 'data.csv'}
        self.pem.uses_artifact(self.art1)
        pem_json = PEMSerialization.to_json(self.pem)
        self.assertEqual(get_sample_pem(sample_uses_art), pem_json)

    def test_serialize_produces(self):
        self.pem.Properties = {'filename': 'data.csv'}
        self.pem.produces_artifact(self.art1)
        pem_json = PEMSerialization.to_json(self.pem)
        self.assertEqual(get_sample_pem('', sample_art), pem_json)

    def test_serialize_taxonomy(self):
        self.pem.Properties = {'filename': 'data.csv'}
        self.art1.add_taxonomy_file(tax_id, tax_content)
        self.pem.uses_artifact(self.art1)
        pem_json = PEMSerialization.to_json(self.pem)
        self.assertEqual(get_sample_pem(sample_uses_art_tax), pem_json)

    def test_deserialize(self):
        pem = PEMSerialization.from_json(get_sample_pem(sample_art))

        self.assertEqual(str(pem.ID), 'a606c8ea-39a1-11eb-8ad6-0a9a235141b0')
        self.assertEqual(pem.Predecessor, None)
        self.assertEqual(str(pem.Emitter), 'serialization_test_2')
        self.assertEqual(pem.Type, 'ingest')
        self.assertEqual(pem.TimestampClient, '2020-12-08 22:06:40')
        self.assertEqual(pem.TimestampReceived, '')
        self.assertEqual(pem.Version, '2.0.0')
        self.assertEqual(pem.Properties['filename'], 'data.csv')
        self.assertEqual(len(pem.UsesArtifacts), 1)
        self.assertEqual(pem.UsesArtifacts[0].Name, 'Foobar')
        self.assertEqual(pem.UsesArtifacts[0].Properties, {'foo': 'baz'})
        self.assertEqual(pem.UsesArtifacts[0].TaxonomyFiles, None)

    def test_deserialize_tax(self):
        pem = PEMSerialization.from_json(get_sample_pem(sample_art_tax))

        self.assertEqual(str(pem.ID), 'a606c8ea-39a1-11eb-8ad6-0a9a235141b0')
        self.assertEqual(pem.Predecessor, None)
        self.assertEqual(str(pem.Emitter), 'serialization_test_2')
        self.assertEqual(pem.Type, 'ingest')
        self.assertEqual(pem.TimestampClient, '2020-12-08 22:06:40')
        self.assertEqual(pem.TimestampReceived, '')
        self.assertEqual(pem.Version, '2.0.0')
        self.assertEqual(pem.Properties['filename'], 'data.csv')
        self.assertEqual(len(pem.UsesArtifacts), 1)
        self.assertEqual(pem.UsesArtifacts[0].Name, 'Foobar')
        self.assertEqual(pem.UsesArtifacts[0].Properties, {'foo': 'baz'})
        self.assertEqual(pem.UsesArtifacts[0].TaxonomyFiles, {tax_id.hex: tax_content})


class TestArtifactSerializationUnit(unittest.TestCase):

    def test_serialize(self):
        art1 = Artifact('Foobar', {'foo': 'baz'})
        art1.CreatedAt = "2020-12-08 22:06:40"
        art_json = json.dumps(ArtifactSerialization.to_dict(art1))
        self.assertEqual(sample_art, art_json)
        self.assertEqual("Artifact(Foobar, {'foo': 'baz'}, 2020-12-08 22:06:40)", str(art1))

    def test_deserialize(self):
        d = json.loads(sample_art)
        art = ArtifactSerialization.from_dict(d)
        self.assertEqual(art.Name, "Foobar")
        self.assertEqual(art.Properties, {"foo": "baz"})
        self.assertEqual(art.CreatedAt, "2020-12-08 22:06:40")
