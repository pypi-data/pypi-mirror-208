import logging

from   objects.cxmlobject import CXMLObject

logger = logging.getLogger(__name__)


class Option(object):
    def __init__(self, attrs = {}, data = None):
        self.attrs = attrs
        self.data = data


class Transaction(object):
    def __init__(self, attrs = {}, URL = None, options = None):
        self.attrs = attrs
        self.URL = URL
        self.options = options if options else []


class ProfileResponse(CXMLObject):     

    def __init__(self):
        super(ProfileResponse, self).__init__()
        self.attrs = {}
        self.options = []
        self.transactions = []

    def parserElemCB(self, ancestor, elem, attrs):
        if elem == 'ProfileResponse':
            self.attrs = attrs
        elif elem == 'Option':
            self._lastOption = Option(attrs, None)
            if ancestor == 'ProfileResponse':
                self.options.append(self._lastOption)
            else:
                self.transactions[-1].options.append(self._lastOption)
        elif elem == 'Transaction':
            self.transactions.append(Transaction(attrs, None, None))

    def parserDataCB(self, ancestor, data):
        if ancestor == 'URL':
            self.transactions[-1].URL = data
        elif ancestor == 'Option':
            self._lastOption.data = data