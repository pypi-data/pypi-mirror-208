class MailConfig(object):

    BATCH_MAIL_TEMPLATE = '''\
Batch %s sent from Pro Door (UK) Limited to CBRE Managed Services Limited contains %d errors.

'''
    ERROR_INTRO         = '''\
The following documents have been Rejected.

'''
    INVOICE_ERROR       = '''\
Invoice %s

DOCUMENT ERRORS

%s

'''
    FROM                = 'invoicebot@prodoor.com'
    PORT                = 587
    RECIPIENTS          = ['stuartmckone@gmail.com'] # ['creditcontrol@prodoor.com']
    PWD                 = ''
    SVR                 = 'localhost'
