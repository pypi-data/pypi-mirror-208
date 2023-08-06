import logging
import urllib.request
from   lxml import etree

from   config.base import BaseConfig
from   errors.errors import CXML_DTDError

logger = logging.getLogger(__name__)


class CXMLParser(etree.TreeBuilder):

    def __init__(self, parent):
        super(CXMLParser, self).__init__()
        self._parent = parent
        self._ancestors = ['root']
    
    def doctype(self, name, pubid, system):
        if name == 'cXML':
            self._parent._dtdURL = system

    def start(self, tag, attrs):
        super(CXMLParser, self).start(tag, attrs)
        self._parent.parserElemCB(self._ancestors[-1], tag, attrs)
        self._ancestors.append(tag)

    def end(self, tag):
        super(CXMLParser, self).end(tag)
        self._ancestors.pop()        

    def data(self, data):
        super(CXMLParser, self).data(data)
        if data.strip('\n '):        
            self._parent.parserDataCB(self._ancestors[-1], data.strip('\n '))            

    def close(self):
        '''
        Try catch here is to ensure that XMLSyntaxError exceptions are raised correctly, seems little point in
        attempting to close if there is another exception waiting to happen
        '''
        try:
            return super(CXMLParser, self).close()
        except:
            return


class CXMLObject(object):
    def __init__(self):
        self._dtd = None
        self._dtdURL = BaseConfig.CXML_DTD_URL
        self._xmlNS = '{%s}' % BaseConfig.XML_NS
        self._parser = CXMLParser(self)  
        self._xml = etree.ElementTree(etree.XML('''\
<?xml version="1.0"?>\
<!DOCTYPE cXML SYSTEM "%s">\
<cXML></cXML>''' % BaseConfig.CXML_DTD_URL))

    def parserElemCB(self, ancestor: str, elem: str, attrs: dict):
        '''
        ancestor: a string representing the last element processed
        elem: a string representing the current element to be processed
        attrs: a dict representing the attributes associated with this elem

        To be overridden in sub class
        '''
        pass

    def parserDataCB(self, ancestor: str, data: str):
        '''
        ancestor: a string representing the last element processed
        data: a string representing the text of the ancestor elem
        
        To be overridden in sub class
        '''        
        pass

    def _generateTree(self, pvMap: dict):
        '''
        fv: a dictionary of fields->values to be mapped
        m: a cxml mapping description
        '''

        for p, v in pvMap.items():
            curEl = self._xml.getroot()
            els, attr = p.split('@')[:] if '@' in p else (p, None) 
            els = els.split('/')
            for e in els:
                if e:
                    found = curEl.find(e)
                    if found is None:
                        newEl = curEl.makeelement(e)
                        curEl.append(newEl)
                        curEl = newEl
                    else:
                        curEl = found
            if attr:
                if ':' in attr:
                    curEl.set(self._xmlNS + attr.split(':')[1], v)
                else:
                    curEl.set(attr, v)
            else:
                curEl.text = v
            
    def fromPathValueMap(self, pvMap: dict):
        '''
        pvMap: a dictionary of xml paths->values to be mapped to cxml
        '''
        self._generateTree(pvMap)

    def fromXMLString(self, s):
        self._xml = etree.fromstring(s, parser=etree.XMLParser(target=self._parser))

    def fromXMLFile(self, f):
        '''
        f: filename or a file type object
        '''
        if type(f) == str:
                fp = open(f, 'rb')
                self._xml = etree.parse(fp, parser=etree.XMLParser(target=self._parser))
                fp.close()
        else:
            self._xml = etree.parse(f, parser=etree.XMLParser(target=self._parser))
 
    def getDTD(self):
        if self._dtdURL and not self._dtd:
            resp = urllib.request.urlopen(self._dtdURL)
            self._dtd = etree.DTD(resp)    
        return(self._dtd)

    def updateDTD(self, dtdURL):
        if dtdURL:
            self._dtdURL = dtdURL
            self.getDTD()
            if self._xml and self._xml.docinfo:
                self._xml.docinfo.system_url = self._dtdURL
                
    def validate(self, dtdURL=None):
        self.updateDTD(dtdURL)
        if self.getDTD():
            if self.getDTD().validate(self._xml):
                return True
            else:
                raise(CXML_DTDError(self._dtd.error_log))
        # If we have xml but no DTD then it is already parsed and therefore is valid xml
        return self._xml is not None
        
    def asXMLString(self, prettyPrint=False):
        s = etree.tostring(self._xml, pretty_print=prettyPrint).decode('UTF-8')
        if '<?xml version="1.0"' not in s:
            s = '<?xml version="1.0" encoding="UTF-8"?>%s%s' % ('\n' if prettyPrint else '', s)
        return s
