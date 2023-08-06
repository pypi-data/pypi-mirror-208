import datetime
import cxmlinvbot.mapping.action

from   cxmlinvbot.config.base import BaseConfig
from   cxmlinvbot.mapping.headermapping import HeaderMapping
from   cxmlinvbot.mapping.mapping import Mapping

class ProfileRequestMapping(Mapping):
  
    DTD_URL = BaseConfig.CXML_DTD_URL

    STRUCTURE = HeaderMapping.STRUCTURE + [
        'Request/ProfileRequest'
    ]

    FIELD_TO_ACTION_MAPS = HeaderMapping.FIELD_TO_ACTION_MAPS
        
 
