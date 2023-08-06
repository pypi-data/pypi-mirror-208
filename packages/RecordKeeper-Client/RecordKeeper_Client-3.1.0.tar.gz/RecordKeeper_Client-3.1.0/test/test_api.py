import os
import unittest
from uuid import UUID
from mock import patch

from rkclient import RKClient, RKClientFactory


class TestAPIUnit(unittest.TestCase):

    def test_rk_factory(self):
        os.environ['RK_MOCK'] = 'true'
        rk = RKClientFactory.get('', 'emitter-name')
        del os.environ['RK_MOCK']

        pred = rk.prepare_pem('', None)
        self.assertIsNotNone(pred)

        pem = rk.prepare_pem('some_type_name', pred.ID, { "value_int": -123 })
        self.assertIsNotNone(pem)

        _, ok = rk.send_pem(pred)
        self.assertTrue(ok)

        _, ok = rk.get_info()
        self.assertTrue(ok)

        _, ok = rk.get_tag('test-namespace-unique-name', 'foo')
        self.assertTrue(ok)

        _, ok = rk.set_tag('test-namespace-unique-name', 'bar', pem)
        self.assertTrue(ok)

        _, ok = rk.get_info()
        self.assertTrue(ok)

    def test_rk_factory_default(self):
        rk = RKClientFactory.get('http://localhost', 'emitter-name')
        pem = rk.prepare_pem('', None)
        self.assertIsNotNone(pem)

        _, ok = rk.send_pem(pem)
        self.assertFalse(ok)

    def test_prepare_pem(self):
        rk = RKClient('', 'emitter-name')
        pred = rk.prepare_pem('', None)
        pem = rk.prepare_pem('some_type_name', pred.ID, { "value_int": -123 })

        self.assertIs(type(pem.ID), UUID)
        self.assertEqual(pem.Predecessor, pred.ID)
        self.assertEqual(pem.Type, 'some_type_name')
        self.assertEqual(pem.Emitter, 'emitter-name')
        self.assertEqual(pem.Properties["value_int"], -123)


class TestAPIWithMockingUnit(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('urllib.request.urlopen')
        self.urlopen_mock = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_send_pem_ok(self):
        self.urlopen_mock.return_value = MockResponse(b'Ack getting some_type_name')

        rk = RKClient('http://localhost/', 'some_emitter_id')

        pem = rk.prepare_pem('some_type_name', None)
        msg, ok = rk.send_pem(pem)
        self.assertEqual(ok, True, msg=msg)

    def test_send_pem_error(self):
        self.urlopen_mock.return_value = MockResponse(b'PEM is not valid: Type is empty', code=400)
        from urllib.error import URLError
        self.urlopen_mock.side_effect = URLError("error")

        rk = RKClient('http://localhost/', 'some_emitter_id')

        pem = rk.prepare_pem('', None)
        msg, ok = rk.send_pem(pem)
        self.assertEqual(ok, False, msg=msg)


class MockResponse(object):

    def __init__(self, resp_data, code=200, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'text/plain; charset=utf-8'}

    def read(self):
        return self.resp_data

    def getcode(self):
        return self.code
