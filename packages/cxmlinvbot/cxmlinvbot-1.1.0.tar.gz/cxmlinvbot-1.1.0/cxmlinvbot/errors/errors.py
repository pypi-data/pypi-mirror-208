class DocumentError(Exception):
    def __init__(self, msg, preamble=True):
        super(DocumentError, self).__init__(str(msg) if not preamble else 'Document Error: ' + str(msg))


class CXML_DTDError(DocumentError):
    pass


class LockedFileError(Exception):
    def __init__(self, msg):
        super(LockedFileError, self).__init__('Locked File Error: ' + str(msg))
    pass


class MapActionError(DocumentError):
    pass