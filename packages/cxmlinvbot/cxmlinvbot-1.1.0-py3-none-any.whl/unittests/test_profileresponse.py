from lxml import etree
from unittest import TestCase
from unittest.mock import MagicMock, call

from objects.cxmlobject import CXML_DTDError
from objects.profileresponse import ProfileResponse
from config.base import BaseConfig

class TestProfileResponse(TestCase):
    '''ProfileResponse tests'''

    def setUp(self):
        self.xml_sample = BaseConfig.XML_SAMPLES['ProfileResponse']

    def tearDown(self):
        pass
  
    def test_ProfileResponseAsString(self):
        pr = ProfileResponse()
        pr.fromXMLFile(self.xml_sample)
        self.assertTrue('</ProfileResponse>' in pr.asXMLString())

    def test_ProfileResponseOptions(self):
        expectedRes = (
            ('CredentialMac.type', 'FromSenderCredentials'),
            ('CredentialMac.algorithm', 'HMAC-SHA1-96'),
            ('CredentialMac.creationDate', '2003-01-15T08:42:46-0800'),
            ('CredentialMac.expirationDate', '2003-01-15T11:42:46-0800'),
            ('CredentialMac.value', 'cR6Jpz58nriXERDN'),
        )
        pr = ProfileResponse()
        pr.fromXMLFile(self.xml_sample)
        for n, o in enumerate(pr.options):
            self.assertTrue(o.attrs['name'] == expectedRes[n][0] and o.data == expectedRes[n][1])

    def test_ProfileResponseTransactions(self):
        expectedRes = (
            ('OrderRequest', 'https://service.hub.com/ANCXMLDispatcher.aw/ad/cxml', []),
            ('PunchOutSetupRequest', 'https://service.hub.com/AN/cxml', [
                ('Direct.URL', 'https://bigsupplier.com/punchout'),
                ('Direct.AuthenticationMethod.CredentialMac', 'Yes'),
                ('Direct.AuthenticationMethod.Certificate', 'Yes'),
                ]
            ),
        )
        pr = ProfileResponse()
        pr.fromXMLFile(self.xml_sample)
        for n, t in enumerate(pr.transactions):
            self.assertTrue(t.attrs['requestName'] == expectedRes[n][0] and t.URL == expectedRes[n][1])
            for m, o in enumerate(t.options):
                self.assertTrue(o.attrs['name'] == expectedRes[n][2][m][0] and o.data == expectedRes[n][2][m][1])

if __name__ == '__main__':
    import unittest
    unittest.main()