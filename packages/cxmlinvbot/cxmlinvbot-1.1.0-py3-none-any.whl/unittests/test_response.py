from unittest import TestCase
from unittest.mock import MagicMock, call

from objects.cxmlobject import CXML_DTDError
from objects.response import Response
from config.base import BaseConfig

class TestResponse(TestCase):
    '''Response tests'''

    def setUp(self):
        self.xml_sample = BaseConfig.XML_SAMPLES['Response']

    def tearDown(self):
        pass
  
    def test_ResponseAsString(self):
        r = Response()
        r.fromXMLFile(self.xml_sample)
        self.assertTrue('</Response>' in r.asXMLString())

    def test_ResponseStatus(self):
        r = Response()
        r.fromXMLFile(self.xml_sample)
        self.assertEqual(r.status.code, 200)
        self.assertEqual(r.status.text, 'OK')

    def test_ResponseStatusWithData(self):
        self.xml_sample = BaseConfig.XML_SAMPLES['ResponseWithData']
        r = Response()
        r.fromXMLFile(self.xml_sample)
        self.assertEqual(r.status.code, 200)
        self.assertEqual(r.status.text, 'OK')
        self.assertEqual(r.status.data, 'Some Data')

 

if __name__ == '__main__':
    import unittest
    unittest.main()