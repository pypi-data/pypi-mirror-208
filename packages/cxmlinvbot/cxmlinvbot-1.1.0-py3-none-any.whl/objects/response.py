import logging

from   objects.cxmlobject import CXMLObject

logger = logging.getLogger(__name__)


class Status(object):
    def __init__(self, attrs = {}, data = None):
        self.code = int(attrs['code'])
        self.text = attrs['text']
        self.data = data


class Response(CXMLObject):     

    def __init__(self):
        super(Response, self).__init__()
        self.attrs = {}
        self.status = None

    def parserElemCB(self, ancestor, elem, attrs):
        if elem == 'Response':
            self.attrs = attrs
        elif elem == 'Status':
            if ancestor == 'Response':
                self.status = Status(attrs)

    def parserDataCB(self, ancestor, data):
        if ancestor == 'Status':
            self.status.data = data