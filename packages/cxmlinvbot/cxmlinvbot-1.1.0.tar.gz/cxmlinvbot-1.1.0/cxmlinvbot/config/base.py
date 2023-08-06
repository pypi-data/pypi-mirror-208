from local.config.env import EnvConfig


class BaseConfig(object):

    # XML/cXML config...
    DTD_VERSION             = '1.2.020'
    DTD_ROOT_PATH           = 'http://xml.cxml.org/schemas/cXML/%s/' % DTD_VERSION
    XML_NS                  = 'http://www.w3.org/XML/1998/namespace'
    CXML_DTD_URL            = '%scXML.dtd' % DTD_ROOT_PATH
    INVOICE_DETAIL_DTD_URL  = '%sInvoiceDetail.dtd' % DTD_ROOT_PATH
    
    # COUPA config...
    PROD_COUPA_END_POINT    = 'https://cbre.coupahost.com/cxml/'
    TEST_COUPA_END_POINT    = 'https://cbre-test.coupahost.com/cxml/'
    PROD_INVOICE_END_POINT  = '%sinvoices/' % PROD_COUPA_END_POINT
    TEST_INVOICE_END_POINT  = '%sinvoices/' % TEST_COUPA_END_POINT

    # Miscellania...
    MAIL_PREAMBLE           = 'Pro Door Invoice Bot - '
    VERSION                 = '1.1.0'

    # Testing widgets...
    SAMPLE_PATH             = '%sResources\\cXML\\1.2.057\\Samples\\' % EnvConfig.PROJECT_ROOT
    XML_SAMPLES             = {
        'ProfileResponse'           : '%sprofileresponse.xml' % SAMPLE_PATH,
        'ProfileResponseNoDTD'      : '%sprofileresponsenodtd.xml' % SAMPLE_PATH,
        'ProfileResponseInvalidXML' : '%sprofileresponseinvalidxml.xml' % SAMPLE_PATH,
        'ProfileResponseInvalidDTD' : '%sprofileresponseinvaliddtd.xml' % SAMPLE_PATH,
        'Response'                  : '%sresponse.xml' % SAMPLE_PATH,
        'ResponseWithData'          : '%sresponsewithdata.xml' % SAMPLE_PATH,
    }
    
    CSV_SAMPLE              = '%sCXML Site - Documents\\CSV Invoices\\%s' % (EnvConfig.PROJECT_ROOT, 'CSV 25th to 31st March 2023.csv')

