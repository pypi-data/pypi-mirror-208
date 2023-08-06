from   unittest import TestCase
from   unittest.mock import MagicMock, call

from   errors.errors import DocumentError, CXML_DTDError, LockedFileError, MapActionError

class TestErrors(TestCase):
    '''Error tests'''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_CXML_DTDError(self):
        e = CXML_DTDError('Bang!')
        self.assertEqual(str(e), 'Document Error: Bang!')

    def test_DocumentError(self):
        e = DocumentError('Bang!')
        self.assertEqual(str(e), 'Document Error: Bang!')

    def test_LockedFileError(self):
        e = LockedFileError('Bang!')
        self.assertEqual(str(e), 'Locked File Error: Bang!')
        
    def test_MapActionError(self):
        e = MapActionError('Bang!')
        self.assertEqual(str(e), 'Document Error: Bang!')


if __name__ == '__main__':
    import unittest
    unittest.main()