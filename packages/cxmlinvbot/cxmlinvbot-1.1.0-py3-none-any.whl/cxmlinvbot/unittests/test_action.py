import cxmlinvbot.mapping.action
import operator
from   unittest import TestCase
from   unittest.mock import MagicMock, call


class TestMapAction(TestCase):
    '''MapAction tests'''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_Default(self):
        expectedRes1 = {
            'a path': '666',
            'another path': '666'
        }

        expectedRes2 = {
            'a path': '999',
            'another path': '999'
        }

        expectedRes3 = {
            'a path': '666'
        }

        expectedRes4 = {
            'a path': '999'
        }
        
        t = cxmlinvbot.mapping.action.Default(['a path', 'another path'], '999')
        res = t.perform('a key', {'a key' : '666'})
        self.assertEqual(res, expectedRes1)

        res = t.perform('a key', {'no key': '666'})
        self.assertEqual(res, expectedRes2)

        t = cxmlinvbot.mapping.action.Default('a path', '999')
        res = t.perform('a key', {'a key' : '666'})
        self.assertEqual(res, expectedRes3)

        t = cxmlinvbot.mapping.action.Default('a path', '999')
        res = t.perform('a key', {'a key' : ''})
        self.assertEqual(res, expectedRes4)

    def test_Lambda(self):
        expectedRes1 = {
            'a path': '25',
            'another path': '25'
        }

        t = cxmlinvbot.mapping.action.Lambda(['a path', 'another path'], operator.add, ('this key', 'that key'))
        res = t.perform('', {'this key': '12', 'that key': '13'})
        self.assertEqual(res, expectedRes1)

        self.assertRaises(cxmlinvbot.mapping.action.MapActionError, t.perform, '', {'no key': '12', 'that key': '13'})

    def test_Required(self):
        expectedRes1 = {
            'a path': '666',
            'another path': '666'
        }

        t = cxmlinvbot.mapping.action.Required(['a path', 'another path'])
        res = t.perform('a key', {'a key' : '666'})
        self.assertEqual(res, expectedRes1)

        self.assertRaises(cxmlinvbot.mapping.action.MapActionError, t.perform, 'a key', {'no key': '666'})


if __name__ == '__main__':
    import unittest
    unittest.main()