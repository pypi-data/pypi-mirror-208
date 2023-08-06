import datetime
import os
import pathlib
from   unittest import TestCase
from   unittest.mock import MagicMock, call

from   cxmlinvbot.filing.filing import Archive, ArchiveException


class TestFiling(TestCase):
    '''Filing tests'''

    ARCH_PATH = 'c:\\temp\\test\\archive\\'
    TEST_PATH = 'c:\\temp\\test\\'
    TEST_FILE = 'afile.log'
    TEST_FILE_FP = '%s%s' % (TEST_PATH, TEST_FILE)
    ARCH_DATE = '2023051201101211'
    ARCH_FILE_FP = '%s%s.%s' % (ARCH_PATH, ARCH_DATE, TEST_FILE)

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
        f = a.archive(self.TEST_PATH, self.TEST_FILE)
        self.assertFalse(os.path.exists(self.TEST_FILE_FP))
        self.assertTrue(os.path.exists(f))
        os.remove(f)

    def testArchiveCleanse(self):
        a = Archive(self.ARCH_PATH, 'log', 1)
        f = a.archive(self.TEST_PATH, self.TEST_FILE)
        af1 = '20220430101243.%s' % self.TEST_FILE
        af2 = '20210429112234.%s' % self.TEST_FILE
        pathlib.Path(self.ARCH_PATH + af1).touch()
        pathlib.Path(self.ARCH_PATH + af2).touch()
        self.assertTrue(os.path.exists(self.ARCH_PATH + af1))
        self.assertTrue(os.path.exists(self.ARCH_PATH + af2))
        a.cleanse()
        self.assertTrue(os.path.exists(f))
        self.assertFalse(os.path.exists(self.ARCH_PATH + af1))
        self.assertFalse(os.path.exists(self.ARCH_PATH + af2))
        os.remove(f)
        
    def testArchiveExtUnknown(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        self.assertRaises(ArchiveException, a.archive, self.TEST_PATH, 'another_file')

    def testArchiveCreateFile(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        f = a.createFile(self.TEST_FILE)
        f.close()
        self.assertTrue(os.path.exists(f.name))
        os.remove(f.name)

    def testArchiveExists(self):
        a = Archive(self.ARCH_PATH, 'log', 10)
        f = a.archive(self.TEST_PATH, self.TEST_FILE)
        self.assertTrue(a.exists(self.TEST_FILE))
        self.assertTrue(a.exists(self.TEST_FILE.split('.')[0]))
        self.assertFalse(a.exists('any old file'))
        os.remove(f)


if __name__ == '__main__':
    import unittest
    unittest.main()