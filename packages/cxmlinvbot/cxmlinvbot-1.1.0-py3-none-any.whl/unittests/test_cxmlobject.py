from lxml import etree
from unittest import TestCase
from unittest.mock import MagicMock, call

from objects.cxmlobject import CXML_DTDError, CXMLObject
from config.base import BaseConfig

class TestCXMLObject(TestCase):
    '''CXMLObject tests'''

    def setUp(self):
        self.xml_sample = BaseConfig.XML_SAMPLES['ProfileResponse']

    def tearDown(self):
        pass
    
    def test_CXMLObjectMissingFile(self):
        obj = CXMLObject()
        self.assertRaises(FileNotFoundError, obj.fromXMLFile, 'hgfgfhgfhgf')

    def test_CXMLObjectValidateFailsDueToXML(self):
        obj = CXMLObject()
        self.assertRaises(etree.XMLSyntaxError, obj.fromXMLFile, BaseConfig.XML_SAMPLES['ProfileResponseInvalidXML'])

    def test_CXMLObjectValidateFailsDueToDTD(self):
        obj = CXMLObject()
        obj.fromXMLFile(BaseConfig.XML_SAMPLES['ProfileResponseInvalidDTD'])
        self.assertRaises(CXML_DTDError, obj.validate)
        
    def test_CXMLObjectFromFileName(self):
        obj = CXMLObject()
        obj.fromXMLFile(self.xml_sample)
        self.assertTrue(obj.asXMLString())
        self.assertTrue(obj.getDTD())
        self.assertTrue(obj.validate())

    def test_CXMLObjectFromFile(self):
        obj = CXMLObject()
        f = open(self.xml_sample, 'rb')
        obj.fromXMLFile(f)
        f.close()
        self.assertTrue(obj.asXMLString())

    def test_CXMLObjectFromString(self):
        obj = CXMLObject()
        f = open(self.xml_sample, 'rb')
        s = f.read()
        f.close()
        obj.fromXMLString(s)
        self.assertTrue(obj.asXMLString())

    def test_CXMLObjectAsString(self):
        expectedRes = '<?xml version="1.0" encoding="UTF-8"?>%s' % etree.tostring(etree.ElementTree(etree.XML('''\
<!DOCTYPE cXML SYSTEM "%s">\
<cXML></cXML>''' % BaseConfig.CXML_DTD_URL))).decode('UTF-8')
        
        obj = CXMLObject()
        self.assertEqual(expectedRes, obj.asXMLString())

    def test_CXMLObjectUpdateDTD(self):
        expectedRes = '<?xml version="1.0" encoding="UTF-8"?>%s' % etree.tostring(etree.ElementTree(etree.XML('''\
<!DOCTYPE cXML SYSTEM "%s">\
<cXML></cXML>''' % BaseConfig.INVOICE_DETAIL_DTD_URL))).decode('UTF-8')
        
        obj = CXMLObject()
        obj.updateDTD(BaseConfig.INVOICE_DETAIL_DTD_URL)
        self.assertEqual(expectedRes, obj.asXMLString())

    def test_CXMLObjectFromPathValueMap(self):
        test = {
            'Foo/Bar': 'Hello',
            'Foo/Bar/Baa': 'World',
            'Foo/Bar@foo': 'bar',
            'Foo/Bah': '!!'
        }

        expectedRes = '<cXML><Foo><Bar foo="bar">Hello<Baa>World</Baa></Bar><Bah>!!</Bah></Foo></cXML>'

        obj = CXMLObject()
        obj.fromPathValueMap(test)
        self.assertTrue(expectedRes in obj.asXMLString())


if __name__ == '__main__':
    import unittest
    unittest.main()