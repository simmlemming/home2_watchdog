import im.myhome.storage as storage
import unittest
import im.myhome.utils as utils


class StorageTest(unittest.TestCase):

    def setUp(self):
        storage.DATABASE_FILE_NAME = 'tmp.db'
        utils.rm('tmp.db')

    def test_token_update(self):
        device_1 = dict(name='d1', token='t1')
        device_2 = dict(name='d2', token='t2')

        storage.add_device(device_1)
        devices = storage.get_all_devices()
        self.assertEqual(1, len(devices))

        storage.add_device(device_2)
        devices = storage.get_all_devices()
        self.assertEqual(2, len(devices))

        device_1['token'] = 't_updated'
        storage.add_device(device_1)
        devices = storage.get_all_devices()
        self.assertEqual(2, len(devices))

        self.assertTrue(('d1', 't_updated') in devices)

    def tearDown(self):
        utils.rm('tmp.db')
