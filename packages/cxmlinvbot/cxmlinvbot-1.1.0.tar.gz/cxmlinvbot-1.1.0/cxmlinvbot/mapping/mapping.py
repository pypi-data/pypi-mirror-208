import logging

from   cxmlinvbot.config.base import BaseConfig
from   cxmlinvbot.errors.errors import MapActionError

logger = logging.getLogger(__name__)


class Mapping(object):

    DTD_URL = BaseConfig.CXML_DTD_URL
    STRUCTURE = []
    FIELD_TO_ACTION_MAP = {}

    def getDTD_URL(self):
        return self.DTD_URL
    
    def getMap(self) -> dict:
        return self.FIELD_TO_ACTION_MAP
    
    def perform(self, nvPairs, catchAll=False):
        m = {}
        for e in self.STRUCTURE:
            m[e] = None
        errors = []
        for fam in self.FIELD_TO_ACTION_MAPS:
            for key, action in fam.items():
                try:
                    m.update(action.perform(key, nvPairs))
                except MapActionError as e:
                    if catchAll:
                        errors.append(str(e))
                    else:
                        raise e
        if catchAll and errors:
            raise MapActionError('\n'.join(errors), preamble=False)
        return m