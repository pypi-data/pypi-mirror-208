class EnvConfig(object):
    PROJECT_ROOT            = 'C:\\Users\\Mach1\\OneDrive\\Documents\\Projects\\Pro Door\\'
    PROJECT_NAME            = 'Invoice Bot'
    PROJECT_FULLPATH        = '%sApps\\%s\\' % (PROJECT_ROOT, PROJECT_NAME)

    ACRHIVE_CSV_PATH        = '%sCXML Site - Documents\\CSV Invoices\\Archive\\' % PROJECT_ROOT
    ACRHIVE_CXML_PATH       = '%sCXML Site - Documents\\CXML Archive\\' % PROJECT_ROOT
    CLEANSE_LOGS            = True
    CLEANSE_ARCHIVES        = True
    CLEANSE_PERIOD          = 14 # days
    DEPLOYMENT_MODE         = 'production'
    TGT_ENDPOINT            = 'test'
    LOCKED_FILE_RETRIES     = 10
    LOG_PATH                = '%sApps\\%s\\Logs\\' % (PROJECT_ROOT, PROJECT_NAME)
    NEW_CSV_PATH            = '%sCXML Site - Documents\\CSV Invoices\\' % PROJECT_ROOT
    HEARTBEAT_TIME          = 60 # seconds


