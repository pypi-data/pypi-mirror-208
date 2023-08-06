import cxmlinvbot.main
import glob
import logging
import os
import pathlib
import requests
from   encrypta import encrypta
from   unittest import TestCase
from   unittest.mock import MagicMock, call, DEFAULT

from   cxmlinvbot.config.base import BaseConfig
from   cxmlinvbot.errors.errors import CXML_DTDError, DocumentError, LockedFileError, MapActionError
from   cxmlinvbot.filing.filing import Archive
from   cxmlinvbot.mail.mail import Mail
from   cxmlinvbot.main import cleanseAll, createGrace, mailBatchComplete, mailFatal, mailLockedFile, main, openFile 
from   cxmlinvbot.main import pathExists, processInvoice, postCXML, starting, stopping, wait
from   cxmlinvbot.mapping import invoicedetailrequestmapping
from   cxmlinvbot.objects import cxmlobject
from   local.config.env import EnvConfig
from   local.config.mail import MailConfig


class TestMain(TestCase):
    '''main tests'''

    def setUp(self):
        self.origCLEANSE_ARCHIVES = EnvConfig.CLEANSE_ARCHIVES
        self.origCLEANSE_LOGS = EnvConfig.CLEANSE_LOGS
        cxmlinvbot.main.__dict__['csvArchive'] = self.mockCSVArchive = MagicMock(spec=Archive)
        cxmlinvbot.main.__dict__['cxmlArchive'] = self.mockCXMLArchive = MagicMock(spec=Archive)
        cxmlinvbot.main.__dict__['logArchive'] = self.mockLogArchive = MagicMock(spec=Archive)
        cxmlinvbot.main.__dict__['Mail'] = self.mockMail = MagicMock(spec=Mail)
        cxmlinvbot.main.__dict__['logger'] = self.mockLogger = MagicMock(spec=logging.Logger)
        cxmlinvbot.main.__dict__['CXMLObject'] = self.mockCXMLObject = MagicMock()
        cxmlinvbot.main.__dict__['InvoiceDetailRequestMapping'] = self.mockIDRM = MagicMock()
        cxmlinvbot.main.__dict__['Response'] = self.mockEPResponse = MagicMock()
        cxmlinvbot.main.__dict__['csv'] = self.mockCSV = MagicMock()
        glob.__dict__['glob'] = self.mockGlob = MagicMock()
        os.__dict__['remove'] = self.mockOSRemove = MagicMock()
        os.__dict__['getpid'] = lambda : 1234
        pathlib.__dict__['Path'] = self.mockPathLib = MagicMock()
        requests.__dict__['post'] = self.mockPost = MagicMock()

        self.origFns = {}
        self.mockFns = {}
        for fn in ['cleanseAll', 'createGrace', 'mailBatchComplete', 'mailFatal', 'mailLockedFile', 'main', 'openFile',\
                   'pathExists', 'processInvoice', 'postCXML', 'starting', 'stopping', 'wait']:
            self.origFns[fn] = cxmlinvbot.main.__dict__[fn]
            cxmlinvbot.main.__dict__[fn] = self.mockFns[fn] = MagicMock()

    def resetFn(self, fn):
        cxmlinvbot.main.__dict__[fn] = self.origFns[fn]

    def tearDown(self):
        EnvConfig.CLEANSE_ARCHIVES = self.origCLEANSE_ARCHIVES
        EnvConfig.CLEANSE_LOGS = self.origCLEANSE_LOGS

    def testCleanseAll(self):
        self.resetFn('cleanseAll')
        self.mockGlob.side_effect = lambda filename, root_dir : [1, 2, 3]
        cleanseAll()
        self.mockCSVArchive.cleanse.assert_called_once_with()
        self.mockCXMLArchive.cleanse.assert_called_once_with()
        self.mockLogArchive.cleanse.assert_called_once_with()
        self.mockGlob.assert_called_once_with('*.grace', root_dir=EnvConfig.PROJECT_FULLPATH)
        self.mockOSRemove.assert_has_calls([call(1), call(2), call(3)])

    def testCleanseArchivesOnly(self):
        self.resetFn('cleanseAll')
        EnvConfig.CLEANSE_LOGS = False
        self.mockGlob.side_effect = lambda filename, root_dir : [1, 2, 3]
        cleanseAll()
        self.mockCSVArchive.cleanse.assert_called_once_with()
        self.mockCXMLArchive.cleanse.assert_called_once_with()
        self.mockLogArchive.cleanse.assert_not_called()
        self.mockGlob.assert_called_once_with('*.grace', root_dir=EnvConfig.PROJECT_FULLPATH)
        self.mockOSRemove.assert_has_calls([call(1), call(2), call(3)])        

    def testCleanseLogsOnly(self):
        self.resetFn('cleanseAll')
        EnvConfig.CLEANSE_ARCHIVES = False
        self.mockGlob.side_effect = lambda filename, root_dir : [1, 2, 3]
        cleanseAll()
        self.mockCSVArchive.cleanse.assert_not_called()
        self.mockCXMLArchive.cleanse.assert_not_called()
        self.mockLogArchive.cleanse.assert_called_once_with()
        self.mockGlob.assert_called_once_with('*.grace', root_dir=EnvConfig.PROJECT_FULLPATH)
        self.mockOSRemove.assert_has_calls([call(1), call(2), call(3)])        

    def testMailFatal(self):
        self.resetFn('mailFatal')
        expected = 'a fatal message'
        mailFatal(expected)
        self.mockLogger.fatal.called_once_with(expected)
        self.mockMail.assert_called_once_with()
        self.mockMail().addSubject.assert_called_once_with('%sFATAL error' % BaseConfig.MAIL_PREAMBLE)
        self.mockMail().addContent.assert_has_calls([call('ERROR DETAILS\n'), call(expected)])
        self.mockMail().send.assert_called_once_with()

    def testMailBatchComplete(self):
        self.resetFn('mailBatchComplete')
        expectedFile = 'a_file'
        expectedMsgs = {
            '123' : 'a 123 msg',
            '234' : 'msg for 234'
        }
        expectedMail = [
            call.addSubject(BaseConfig.MAIL_PREAMBLE + expectedFile),
            call.addContent(MailConfig.BATCH_MAIL_TEMPLATE % (expectedFile, len(expectedMsgs))),
            call.addContent(MailConfig.ERROR_INTRO),
        ]
        for x, y in expectedMsgs.items():
            expectedMail.append(call.addContent(MailConfig.INVOICE_ERROR % (x, y)))
        expectedMail.append(call.send())

        mailBatchComplete(expectedFile, expectedMsgs)
        self.mockLogger.info.called_once_with(MailConfig.BATCH_MAIL_TEMPLATE % (expectedFile, len(expectedMsgs)))
        self.mockMail.assert_called_once_with()
        for c, exc in zip(self.mockMail().method_calls, expectedMail):
            self.assertEqual(c, exc)

    def testMailLockedFile(self):
        self.resetFn('mailLockedFile')
        expectedFile = 'a_file'
        expectedSubj = '%sLocked File Warning' % BaseConfig.MAIL_PREAMBLE
        expectedLine1 = 'The CSV file "%s" is locked by another user.\n' % expectedFile
        expectedLine2 = 'Possibly it is still open in Excel?\n'
        expectedLine3 = 'Please release the file ASAP.\n'
        expectedLine4 = 'Invoice Bot will continue trying to access it for another %s minutes.\n' % EnvConfig.LOCKED_FILE_RETRIES
        expectedLine5 = 'If still locked, the Bot will exit and need to be restarted.'
        expectedMail = [
            call.addSubject(expectedSubj),
            call.addContent(expectedLine1),
            call.addContent(expectedLine2),
            call.addContent(expectedLine3),
            call.addContent(expectedLine4),
            call.addContent(expectedLine5),
            call.send()
        ]
        mailLockedFile(expectedFile)
        self.mockMail.assert_called_once_with()
        for c, exc in zip(self.mockMail().method_calls, expectedMail):
            self.assertEqual(c, exc)

    def testStarting(self):
        self.resetFn('starting')
        testPID = 123
        expectedSubj = '%sStarting' % BaseConfig.MAIL_PREAMBLE 
        expectedBody = 'Running in %s deployment mode as PID %s.' % (EnvConfig.DEPLOYMENT_MODE, testPID)
        expectedLogs = [
            call.info(expectedSubj),
            call.info(expectedBody),
        ]
        expectedMail = [
            call.addSubject(expectedSubj),
            call.addContent(expectedBody),
            call.send()
        ]
        starting(testPID)
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.mockMail.assert_called_once_with()
        for c, exc in zip(self.mockMail().method_calls, expectedMail):
            self.assertEqual(c, exc)

    def testStopping(self):
        self.resetFn('stopping')
        testPID = 123
        expectedSubj = '%sStopping' % BaseConfig.MAIL_PREAMBLE 
        expectedBody = 'PID %s exiting gracefully.' % testPID
        expectedLogs = [
            call.info(expectedSubj),
            call.info(expectedBody),
        ]
        expectedMail = [
            call.addSubject(expectedSubj),
            call.addContent(expectedBody),
            call.send()
        ]
        stopping(testPID)
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.mockMail.assert_called_once_with()
        for c, exc in zip(self.mockMail().method_calls, expectedMail):
            self.assertEqual(c, exc)

    def testCreateGrace(self):
        self.resetFn('createGrace')
        testPID = 123
        expectedFile = '%s%s.grace' % (EnvConfig.PROJECT_FULLPATH, testPID)
        graceFile = createGrace(testPID)
        self.assertEqual(graceFile, expectedFile)
        self.mockPathLib.assert_called_once_with(graceFile)
        self.mockPathLib.return_value.touch.assert_called()

    def testProcessInvoice(self):
        self.resetFn('processInvoice')
        expectedInvoice = 'inv12345'
        row = {'InvoiceNumber':expectedInvoice}
        self.mockCXMLArchive.exists.side_effect = lambda i : False
        expectedLogs = [
            call.info('Processing invoice - %s' % expectedInvoice),
        ]
        self.mockFns['postCXML'].side_effect = lambda inv, cxml : True
        res = processInvoice(row)
        self.mockCXMLObject.assert_called()
        self.mockIDRM.assert_called()
        self.mockIDRM().perform.assert_called_once_with(row, catchAll=True)
        self.mockCXMLObject().fromPathValueMap.assert_called_once_with(self.mockIDRM().perform.return_value)
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.assertEqual(res, True)

    def testProcessInvoiceErrorInvoice(self):
        self.resetFn('processInvoice')
        expectedRes = {'UNKNOWN' : 'There are rows in the CSV file without an InvoiceNumber field.'}
        row = {'InvoiceNumber':''}
        self.assertEqual(processInvoice(row), expectedRes)
        row = {'InvoiceNumber':None}
        self.assertEqual(processInvoice(row), expectedRes)
        row = {}
        self.assertEqual(processInvoice(row), expectedRes)

    def testProcessInvoiceSeenBefore(self):
        self.resetFn('processInvoice')
        expectedInvoice = 'inv12345'
        row = {'InvoiceNumber':expectedInvoice}
        self.mockCXMLArchive.exists.side_effect = lambda i : True
        expectedLogs = [
            call.info('Processing invoice - %s' % expectedInvoice),
            call.info('Seen this invoice before, will not process again')
        ]
        res = processInvoice(row)
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.assertEqual(res, {})

    def testProcessInvoiceErrorMapping(self):
        self.resetFn('processInvoice')
        expectedInvoice = 'inv12345'
        expectedEx = MapActionError('BAD MAP')
        row = {'InvoiceNumber':expectedInvoice}
        self.mockCXMLArchive.exists.side_effect = lambda i : False
        expectedLogs = [
            call.info('Processing invoice - %s' % expectedInvoice),
            call.error('CSV mapping failed, please correct CSV for missing fields below...'),
            call.error(expectedEx)
        ]
        self.mockCXMLObject().fromPathValueMap.side_effect = expectedEx
        res = processInvoice(row)
        self.mockCXMLObject.assert_called()
        self.mockIDRM.assert_called()
        self.mockIDRM().perform.assert_called_once_with(row, catchAll=True)
        self.mockCXMLObject().fromPathValueMap.assert_called_once_with(self.mockIDRM().perform.return_value)
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.assertEqual(res, {expectedInvoice:expectedEx})

    def testProcessInvoiceErrorDTD(self):
        self.resetFn('processInvoice')
        expectedInvoice = 'inv12345'
        expectedEx = CXML_DTDError('BAD DTD')
        row = {'InvoiceNumber':expectedInvoice}
        self.mockCXMLArchive.exists.side_effect = lambda i : False
        expectedLogs = [
            call.info('Processing invoice - %s' % expectedInvoice),
            call.error('Invoice failed to validate against the DTD, this will need to be corrected...'),
            call.error(expectedEx)
        ]
        self.mockCXMLObject().validate.side_effect = expectedEx
        res = processInvoice(row)
        self.mockCXMLObject.assert_called()
        self.mockIDRM.assert_called()
        self.mockIDRM().perform.assert_called_once_with(row, catchAll=True)
        self.mockCXMLObject().fromPathValueMap.assert_called_once_with(self.mockIDRM().perform.return_value)
        self.mockCXMLObject().validate.assert_called_once_with(self.mockIDRM().getDTD_URL.return_value)
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.assertEqual(res, {expectedInvoice:expectedEx})
 
    def testPostCXML(self):
        self.resetFn('postCXML')        
        origEP = EnvConfig.TGT_ENDPOINT
        EnvConfig.TGT_ENDPOINT = 'test'
        expectedInvoice = 'inv12345'
        expectedRespCode = 200
        expectedRespText = '<xml %s>OK</xml>'
        expectedEPRespCode = 200
        expectedEPRespText = 'ALL GOOD'
        expectedEPRespData = 'SOME DATA'
        expectedHdrs = {'Content-Type':'text/xml'}
        expectedLogs = [
            call.info('Response for cxml from endpoint - %s : %s' % (expectedRespCode, expectedRespText%'encoding="UTF-8"'))
        ]
        expectedCXML = [
            call.asXMLString(),
            call.asXMLString(prettyPrint=True),
        ]
        mockCXML = MagicMock()
        mockResp = MagicMock()
        mockResp.status_code = expectedRespCode
        mockResp.text = expectedRespText%'encoding="UTF-8"'
        self.mockPost.side_effect = lambda e, **kwargs : mockResp
        self.mockEPResponse().status = MagicMock()
        self.mockEPResponse().status.code = expectedEPRespCode
        self.mockEPResponse().status.text = expectedEPRespText
        self.mockEPResponse().status.data = expectedEPRespData
        mockFile = MagicMock()
        self.mockCXMLArchive.createFile.side_effect = lambda inv : mockFile
        res = postCXML(expectedInvoice, mockCXML)
        EnvConfig.TGT_ENDPOINT = origEP
        self.mockEPResponse.assert_called()
        self.mockEPResponse().fromXMLString.assert_called_once_with(expectedRespText%'')
        self.mockPost.assert_called_once_with(BaseConfig.TEST_INVOICE_END_POINT, headers = expectedHdrs, data=mockCXML.asXMLString.return_value)
        self.mockCXMLArchive.createFile.assert_called_once_with(expectedInvoice)
        mockFile.__enter__().write.assert_called_once_with(mockCXML.asXMLString.return_value)
        for c, exc in zip(mockCXML.method_calls, expectedCXML):
            self.assertEqual(c, exc)
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.assertEqual(res, {})

    def testPostCXMLErrorHTTP(self):
        self.resetFn('postCXML')
        origEP = EnvConfig.TGT_ENDPOINT
        EnvConfig.TGT_ENDPOINT = 'production'
        expectedInvoice = 'inv12345'
        expectedEx = requests.HTTPError('BAD HTTP')
        expectedRespCode = 999
        expectedRespText = 'FAILED'
        expectedHdrs = {'Content-Type':'text/xml'}
        expectedLogs = [
            call.info('Response for cxml from endpoint - %s : %s' % (expectedRespCode, expectedRespText))
        ]
        mockCXML = MagicMock()
        mockResp = MagicMock()
        mockResp.status_code = expectedRespCode
        mockResp.text = expectedRespText
        mockResp.raise_for_status.side_effect = expectedEx
        self.mockPost.side_effect = lambda e, **kwargs : mockResp
        self.assertRaises(requests.HTTPError, postCXML, expectedInvoice, mockCXML)
        EnvConfig.TGT_ENDPOINT = origEP
        self.mockPost.assert_called_once_with(BaseConfig.PROD_INVOICE_END_POINT, headers = expectedHdrs, data=mockCXML.asXMLString.return_value)
        mockCXML.asXMLString.assert_called_once_with()
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)

    def testPostCXMLErrorDoc(self):
        self.resetFn('postCXML') 
        origEP = EnvConfig.TGT_ENDPOINT
        EnvConfig.TGT_ENDPOINT = 'test'
        expectedInvoice = 'inv12345'
        expectedRespCode = 200
        expectedRespText = '<xml %s>OK</xml>'
        expectedEPRespCode = 999
        expectedEPRespText = 'BAD DOC'
        expectedEPRespData = 'SOME DATA'
        expectedHdrs = {'Content-Type':'text/xml'}
        expectedLogs = [
            call.info('Response for cxml from endpoint - %s : %s' % (expectedRespCode, expectedRespText%'encoding="UTF-8"'))
        ]
        mockCXML = MagicMock()
        mockResp = MagicMock()
        mockResp.status_code = expectedRespCode
        mockResp.text = expectedRespText%'encoding="UTF-8"'
        self.mockPost.side_effect = lambda e, **kwargs : mockResp
        self.mockEPResponse().status = MagicMock()
        self.mockEPResponse().status.code = expectedEPRespCode
        self.mockEPResponse().status.text = expectedEPRespText
        self.mockEPResponse().status.data = expectedEPRespData
        res = postCXML(expectedInvoice, mockCXML)
        EnvConfig.TGT_ENDPOINT = origEP
        self.mockEPResponse.assert_called()
        self.mockEPResponse().fromXMLString.assert_called_once_with(expectedRespText%'')
        self.mockPost.assert_called_once_with(BaseConfig.TEST_INVOICE_END_POINT, headers = expectedHdrs, data=mockCXML.asXMLString.return_value)
        mockCXML.asXMLString.assert_called_once_with()
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)
        self.assertEqual(res, {expectedInvoice : '%s : %s : %s' % (expectedEPRespCode, expectedEPRespText, expectedEPRespData)})

    def testMain(self):
        self.resetFn('main')
        expectedFile = 'a_file'
        expectedLogs = [
            call.info('Processing CSV invoice file - %s' % expectedFile),
            call.info('HEARTBEAT...'),
        ]
        expectedBadInv = {'inv' : 'SOME ERR'}
        self.mockFns['pathExists'].side_effect = [True, False]
        self.mockGlob.return_value = [expectedFile]
        csvFile = MagicMock()
        self.mockFns['openFile'].return_value = csvFile
        self.mockCSV.DictReader.return_value = [{1:'a',2:'b',3:'c'},{1:'',2:'',3:''}]
        self.mockFns['processInvoice'].return_value = expectedBadInv
        res = main()
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)       
        self.mockFns['starting'].assert_called_once()
        self.mockFns['cleanseAll'].assert_called_once()
        self.mockFns['createGrace'].assert_called_once()
        csvFile.__enter__.assert_called_once()
        self.mockCSV.DictReader.assert_called_once_with(csvFile.__enter__(), delimiter=',') 
        self.mockFns['processInvoice'].assert_called_once()
        csvFile.__exit__.assert_called_once()
        self.mockCSVArchive.archive.assert_called_once_with(EnvConfig.NEW_CSV_PATH, expectedFile)
        self.mockFns['mailBatchComplete'].assert_called_once_with(expectedFile, expectedBadInv)
        self.mockFns['wait'].assert_called_once()
        self.mockFns['stopping'].assert_called_once()
        self.assertEqual(res, 0)   

    def testMainErrorLocked(self):
        self.resetFn('main')
        expectedRetries = 2
        origLFR = EnvConfig.LOCKED_FILE_RETRIES
        EnvConfig.LOCKED_FILE_RETRIES = expectedRetries
        expectedFile = 'a_file'
        expectedEx = LockedFileError('LOCKED')
        expectedLogs = [
            call.info('Processing CSV invoice file - %s' % expectedFile),
            call.warning('CSV is locked by another user, will retry.'),
            call.info('HEARTBEAT...')
        ] * EnvConfig.LOCKED_FILE_RETRIES
        expectedLogs += [
            call.info('Processing CSV invoice file - %s' % expectedFile),
        ]

        self.mockFns['pathExists'].return_value = True
        self.mockGlob.return_value = [expectedFile]
        self.mockFns['openFile'].side_effect = PermissionError('LOCKED')
        res = main()
        EnvConfig.LOCKED_FILE_RETRIES = origLFR        
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)       
        self.mockFns['starting'].assert_called_once()
        self.mockFns['cleanseAll'].assert_called_once()
        self.mockFns['createGrace'].assert_called_once()
        self.mockFns['mailLockedFile'].assert_called_once()
        self.mockFns['wait'].assert_called()
        self.mockFns['mailFatal'].assert_called_once()
        self.assertTrue(all([x in self.mockFns['mailFatal'].call_args[0][0] for x in ['Locked File Error', expectedFile]]))
        self.assertEqual(res, 100)

    def testMainErrorConn(self):
        self.resetFn('main')
        expectedFile = 'a_file'
        expectedEx = ConnectionError('BAD CONN')
        expectedLogs = [
            call.info('Processing CSV invoice file - %s' % expectedFile),
        ]
        self.mockFns['pathExists'].return_value = True
        self.mockGlob.return_value = [expectedFile]
        csvFile = MagicMock()
        self.mockFns['openFile'].return_value = csvFile
        self.mockCSV.DictReader.return_value = [{1:'a',2:'b',3:'c'},{1:'',2:'',3:''}]
        self.mockFns['processInvoice'].side_effect = expectedEx
        res = main()
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)       
        self.mockFns['starting'].assert_called_once()
        self.mockFns['cleanseAll'].assert_called_once()
        self.mockFns['createGrace'].assert_called_once()
        csvFile.__enter__.assert_called_once()
        self.mockCSV.DictReader.assert_called_once_with(csvFile.__enter__(), delimiter=',')
        self.mockFns['processInvoice'].assert_called_once()
        csvFile.__exit__.assert_called_once()
        self.mockFns['mailFatal'].assert_called_once()
        self.assertTrue(all([x in self.mockFns['mailFatal'].call_args[0][0] for x in ['Connection Error', str(expectedEx)]]))
        self.assertEqual(res, 100)        

    def testMainErrorUnex(self):
        self.resetFn('main')
        expectedFile = 'a_file'
        expectedEx = KeyError('BAD INDEX')
        expectedLogs = [
            call.info('Processing CSV invoice file - %s' % expectedFile),
        ]
        self.mockFns['pathExists'].return_value = True
        self.mockGlob.return_value = [expectedFile]
        csvFile = MagicMock()
        self.mockFns['openFile'].return_value = csvFile
        self.mockCSV.DictReader.return_value = [{1:'a',2:'b',3:'c'},{1:'',2:'',3:''}]
        self.mockFns['processInvoice'].side_effect = expectedEx
        res = main()
        for c, exc in zip(self.mockLogger.method_calls, expectedLogs):
            self.assertEqual(c, exc)       
        self.mockFns['starting'].assert_called_once()
        self.mockFns['cleanseAll'].assert_called_once()
        self.mockFns['createGrace'].assert_called_once()
        csvFile.__enter__.assert_called_once()
        self.mockCSV.DictReader.assert_called_once_with(csvFile.__enter__(), delimiter=',') 
        self.mockFns['processInvoice'].assert_called_once()
        csvFile.__exit__.assert_called_once()
        self.mockFns['mailFatal'].assert_called_once()
        self.assertTrue(all([x in self.mockFns['mailFatal'].call_args[0][0] for x in ['Fatal Error', str(expectedEx)]]))
        self.assertEqual(res, 999)   


if __name__ == '__main__':
    import unittest
    unittest.main()