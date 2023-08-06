import mapping.action
from   unittest import TestCase
from   unittest.mock import MagicMock, call

from   config.base import BaseConfig
from   mapping.mapping import Mapping


class TestMap(Mapping):
    FIELD_TO_ACTION_MAPS = [{
        'key1': mapping.action.Required('Foo/Bar')
        },{
        'key2': mapping.action.Required(('Foo/Bar@foo', 'Foo/Bar/Boo')),
        'key3': mapping.action.Required('Foo/Bar/Oof'),
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

if __name__ == '__main__':
    import unittest
    unittest.main()