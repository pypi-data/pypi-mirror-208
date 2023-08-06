import datetime
import os
import pathlib
from   unittest import TestCase
from   unittest.mock import MagicMock, call

from   filing.filing import Archive, ArchiveException

class TestFiling(TestCase):
    '''Filing tests'''

    ARCH_PATH = 'c:\\temp\\test\\archive\\'
    TEST_PATH = 'c:\\temp\\test\\'
    TEST_FILE = 'afile.log'
    TEST_FILE_FP = '%s%s' % (TEST_PATH, TEST_FILE)
    ARCH_FILE_FP = '%s%s.%s' % (ARCH_PATH, datetime.date.today().strftime('%Y%m%d'), TEST_FILE)

    def setUp(self):
        os.makedirs(self.TEST_PATH, exist_ok=True)
        pathlib.Path(self.TEST_FILE_FP).touch()

    def tearDown(self):
        if os.path.exists(self.ARCH_FILE_FP):
            os.remove(self.ARCH_FILE_FP)
        os.rmdir(self.ARCH_PATH)

    def testArchiveCreation(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        self.assertTrue(os.path.exists(self.ARCH_PATH))

    def testArchiveCreationOnExistingArchive(self):
        os.makedirs(self.ARCH_PATH)
        a = Archive(self.ARCH_PATH, 'log', 10)
        self.assertTrue(os.path.exists(self.ARCH_PATH))

    def testArchiveFile(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        self.assertTrue(os.path.exists(self.TEST_FILE_FP))
        archFP = a.archive(self.TEST_PATH, self.TEST_FILE)
        self.assertFalse(os.path.exists(self.TEST_FILE_FP))
        self.assertTrue(os.path.exists(self.ARCH_FILE_FP))
        self.assertEqual(self.ARCH_FILE_FP, archFP)

    def testArchiveCleanse(self):
        a = Archive(self.ARCH_PATH, 'log', 1)
        a.archive(self.TEST_PATH, self.TEST_FILE)
        pathlib.Path(self.ARCH_PATH + '20230430.afile.log').touch()
        pathlib.Path(self.ARCH_PATH + '20230429.afile.log').touch()
        self.assertTrue(os.path.exists(self.ARCH_PATH + '20230430.afile.log'))
        self.assertTrue(os.path.exists(self.ARCH_PATH + '20230429.afile.log'))
        a.cleanse()
        self.assertTrue(os.path.exists(self.ARCH_FILE_FP))
        self.assertFalse(os.path.exists(self.ARCH_PATH + '20230430.afile.log'))
        self.assertFalse(os.path.exists(self.ARCH_PATH + '20230429.afile.log'))
        
    def testArchiveExtUnknown(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        self.assertRaises(ArchiveException, a.archive, self.TEST_PATH, 'afile.csv')

    def testArchiveCreateFile(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        f = a.createFile('myfile')
        f.close()
        newFile = '%s%s.myfile.log' % (self.ARCH_PATH, datetime.date.today().strftime('%Y%m%d'))
        self.assertTrue(os.path.exists(newFile))
        os.remove(newFile)

    def testArchiveExists(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        a.archive(self.TEST_PATH, self.TEST_FILE)
        self.assertTrue(a.exists(self.TEST_FILE))
        self.assertTrue(a.exists(self.TEST_FILE.split('.')[0]))
        self.assertFalse(a.exists('any old file'))


if __name__ == '__main__':
    import unittest
    unittest.main()