import csv
import glob
import logging
import os
import pathlib
import requests
import time
import traceback

from   cxmlinvbot.config.base import BaseConfig
from   cxmlinvbot.errors.errors import LockedFileError, MapActionError
from   cxmlinvbot.filing.filing import Archive
from   cxmlinvbot.mail.mail import Mail
from   cxmlinvbot.mapping.action import MapActionError
from   cxmlinvbot.mapping.invoicedetailrequestmapping import InvoiceDetailRequestMapping
from   cxmlinvbot.objects.cxmlobject import CXMLObject, CXML_DTDError
from   cxmlinvbot.objects.response import Response
from   local.config.env import EnvConfig
from   local.config.mail import MailConfig


def cleanseAll():
    if EnvConfig.CLEANSE_ARCHIVES:
        csvArchive.cleanse()
        cxmlArchive.cleanse()
    if EnvConfig.CLEANSE_LOGS:
        logArchive.cleanse()
    graceFiles = glob.glob('*.grace', root_dir=EnvConfig.PROJECT_FULLPATH)
    for gf in graceFiles:
        os.remove(gf)

def postCXML(invoice, cxml):
    endPoint = BaseConfig.PROD_INVOICE_END_POINT \
        if EnvConfig.TGT_ENDPOINT == 'production' else BaseConfig.TEST_INVOICE_END_POINT
    
    # Can raise ConnectionError
    headers = {'Content-Type':'text/xml'}
    r = requests.post(endPoint, headers=headers, data=cxml.asXMLString())

    logger.info('Response for cxml from endpoint - %s : %s' % (r.status_code, r.text))
    if r.status_code == 200:
        cxmlResp = Response()
        # lxml etree doesn't like the encoding to be resent in the xml header
        cxmlResp.fromXMLString(r.text.replace('encoding="UTF-8"', ''))
        if cxmlResp.status.code == 200:
            with cxmlArchive.createFile(invoice) as cxmlFile:
                cxmlFile.write(cxml.asXMLString(prettyPrint=True))
        else:
            return {invoice : '%s : %s : %s' % (cxmlResp.status.code, cxmlResp.status.text, cxmlResp.status.data)}
    else:
       # Raise as HTTPError
       r.raise_for_status()
    return {}

def processInvoice(row):
    invoice = row.get('InvoiceNumber', '')
    if not (type(invoice) == str and len(invoice)):
        return {'UNKNOWN' : 'There are rows in the CSV file without an InvoiceNumber field.'}
    
    logger.info('Processing invoice - %s' % invoice)
    if not cxmlArchive.exists(invoice):
        cxml = CXMLObject()
        req = InvoiceDetailRequestMapping()
        try:
            cxml.fromPathValueMap(req.perform(row, catchAll=True))
            cxml.validate(req.getDTD_URL())
        except MapActionError as e1:
            logger.error('CSV mapping failed, please correct CSV for missing fields below...')
            logger.error(e1)
            return {invoice : e1}
        except CXML_DTDError as e2:
            logger.error('Invoice failed to validate against the DTD, this will need to be corrected...')
            logger.error(e2)  
            return {invoice : e2}
        return postCXML(invoice, cxml)
    else:
        logger.info('Seen this invoice before, will not process again')
    return {}

def mailBatchComplete(f, badInvoices):
    logger.info(MailConfig.BATCH_MAIL_TEMPLATE % (f, len(badInvoices)))
    mail = Mail()
    mail.addSubject(BaseConfig.MAIL_PREAMBLE + f)
    mail.addContent(MailConfig.BATCH_MAIL_TEMPLATE % (f, len(badInvoices)))
    for n, (i, e) in enumerate(badInvoices.items()):
        if n == 0:
            mail.addContent(MailConfig.ERROR_INTRO)
        mail.addContent(MailConfig.INVOICE_ERROR % (i, e))
    mail.send()

def mailFatal(message):
    logger.fatal(message)
    mail = Mail()
    mail.addSubject(BaseConfig.MAIL_PREAMBLE + 'FATAL error')
    mail.addContent('ERROR DETAILS\n')
    mail.addContent(message)
    mail.send()

def mailLockedFile(f):
    mail = Mail()
    mail.addSubject(BaseConfig.MAIL_PREAMBLE + 'Locked File Warning')
    mail.addContent('The CSV file "%s" is locked by another user.\n' % f)
    mail.addContent('Possibly it is still open in Excel?\n')
    mail.addContent('Please release the file ASAP.\n')
    mail.addContent('Invoice Bot will continue trying to access it for another %s minutes.\n' % EnvConfig.LOCKED_FILE_RETRIES)
    mail.addContent('If still locked, the Bot will exit and need to be restarted.')
    mail.send()

def starting(pid):
    title = BaseConfig.MAIL_PREAMBLE + 'Starting'
    body  = 'Running in %s deployment mode as PID %s.' % (EnvConfig.DEPLOYMENT_MODE, pid)
    logger.info(title)
    logger.info(body)
    mail = Mail()
    mail.addSubject(title)
    mail.addContent(body)
    mail.send()

def stopping(pid):
    title = BaseConfig.MAIL_PREAMBLE + 'Stopping'
    body  = 'PID %s exiting gracefully.' % pid
    logger.info(title)
    logger.info(body)
    mail = Mail()
    mail.addSubject(title)
    mail.addContent(body)
    mail.send()

def createGrace(pid):
    # Deleting the grace file will cause the bot to exit gracefully
    graceFile = '%s%s.grace' % (EnvConfig.PROJECT_FULLPATH, pid)
    pathlib.Path(graceFile).touch()
    return graceFile

def pathExists(f):
    # Wrapper method to simplify unittesting    
    return os.path.exists(f)

def openFile(f, newline='', encoding='utf-8-sig', mode='r+'):
    # Wrapper method to simplify unittesting
    return open(f, newline=newline, encoding=encoding, mode=mode)

def wait():
    # Wrapper method to simplify unittesting
    time.sleep(EnvConfig.HEARTBEAT_TIME)

def main():
    pid = os.getpid()
    starting(pid)
    # cleanseAll must be called before createGrace otherwise the bot will never startup
    cleanseAll()
    graceFile = createGrace(pid)

    lockedFileCountMap = {}
    try:
        while(pathExists(graceFile)):
            # List available csv files
            files = glob.glob('*.csv', root_dir=EnvConfig.NEW_CSV_PATH)
            for f in files:
                logger.info('Processing CSV invoice file - %s' % f)
                # TODO: may not need to do this locked file handling if the windows scheduling works as anticpiated
                lockedFileCount = lockedFileCountMap.get(f, 0)
                try:
                    with openFile(EnvConfig.NEW_CSV_PATH + f) as csvFile:
                        badInvoices = {}
                        reader = csv.DictReader(csvFile, delimiter=',')
                        for row in reader:
                            # Don't process empty rows
                            if ''.join(row.values()).strip():
                                badInvoices.update(processInvoice(row))
                    csvArchive.archive(EnvConfig.NEW_CSV_PATH, f)
                    mailBatchComplete(f, badInvoices)
                except PermissionError as e:
                    # The file is locked let's go round the loop and see if it becomes unlocked
                    lockedFileCountMap[f] = lockedFileCount + 1
                    if lockedFileCount + 1 > EnvConfig.LOCKED_FILE_RETRIES:
                        raise LockedFileError('CSV file locked for over %d minutes - %s' % (EnvConfig.LOCKED_FILE_RETRIES, f))
                    elif lockedFileCount == 0:
                        # Send out mail on the first lock to give users an opportunity to release the file before
                        # we exit
                        mailLockedFile(f)
                    logger.warning('CSV is locked by another user, will retry.')
            wait()
            logger.info('HEARTBEAT...')            
        stopping(pid)
        return 0
    except LockedFileError as lfe:
        message = str(lfe) + '\n'
        message += 'Please close the CSV file ASAP and restart the Bot.'
        errorCode = 100
    except (ConnectionError, requests.HTTPError):
        message = 'Connection Error: An error occurred either connecting to or sending data to the Coupa endpoint.\n'
        message += traceback.format_exc() + '\n'
        message += 'If this error does not clear on restart pleace contact IT and/or Coupa support.'
        errorCode = 100
    except BaseException:
        message = 'Fatal Error: An unexpected error condition occured...\n'
        message += traceback.format_exc() + '\n'
        message += 'Please contact IT to address the above error and restart the Bot.'
        errorCode = 999
    mailFatal(message)

    return errorCode


if __name__ == '__main__':
    '''
    # For debugging HTTP requests
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1
    '''
    
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s : %(levelname)s : %(module)s : %(message)s')
    logger = logging.getLogger(__name__)

    csvArchive = Archive(EnvConfig.ACRHIVE_CSV_PATH, 'csv', EnvConfig.CLEANSE_PERIOD)
    cxmlArchive = Archive(EnvConfig.ACRHIVE_CXML_PATH, 'cxml', EnvConfig.CLEANSE_PERIOD)
    logArchive = Archive(EnvConfig.LOG_PATH, 'log', EnvConfig.CLEANSE_PERIOD)

    main()
