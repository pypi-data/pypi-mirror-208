import cxmlinvbot.mapping.action
from   unittest import TestCase
from   unittest.mock import MagicMock, call

from   cxmlinvbot.mapping.mapping import Mapping
from   cxmlinvbot.errors.errors import MapActionError


class TestMap(Mapping):
    FIELD_TO_ACTION_MAPS = [{
        'key1': cxmlinvbot.mapping.action.Required('Foo/Bar')
        },{
        'key2': cxmlinvbot.mapping.action.Required(('Foo/Bar@foo', 'Foo/Bar/Boo')),
        'key3': cxmlinvbot.mapping.action.Required('Foo/Bar/Oof'),
    }]


class TestMapping(TestCase):
    '''Mapping tests'''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_MappingPerform(self):
        nvPairs = {
            'key1': 'some data',
            'key2': '123',
            'key3': 'more data'
        }

        expectedRes = {
            'Foo/Bar': 'some data',
            'Foo/Bar@foo': '123',
            'Foo/Bar/Boo': '123',
            'Foo/Bar/Oof': 'more data'
        }

        res = TestMap().perform(nvPairs)
        self.assertEqual(res, expectedRes)

    def test_MappingFails(self):
        nvPairs = {
            'key1': 'some data',
            'key3': 'more data'
        }

        expectedRes = {
            'Foo/Bar': 'some data',
            'Foo/Bar@foo': '123',
            'Foo/Bar/Boo': '123',
            'Foo/Bar/Oof': 'more data'
        }
        with self.assertRaises(MapActionError) as cm:
            TestMap().perform(nvPairs)
        self.assertTrue('key2 is missing' in str(cm.exception))

    def test_MultiMappingFails(self):
        nvPairs = {
            'key1': 'some data'
        }

        expectedRes = {
            'Foo/Bar': 'some data',
            'Foo/Bar@foo': '123',
            'Foo/Bar/Boo': '123',
            'Foo/Bar/Oof': 'more data'
        }
        with self.assertRaises(MapActionError) as cm:
            TestMap().perform(nvPairs, catchAll=True)
        self.assertTrue('key2 is missing' in str(cm.exception))
        self.assertTrue('key3 is missing' in str(cm.exception))        


if __name__ == '__main__':
    import unittest
    unittest.main()