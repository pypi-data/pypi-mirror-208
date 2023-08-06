import datetime
import cxmlinvbot.mapping.action

from   cxmlinvbot.config.base import BaseConfig
from   cxmlinvbot.mapping.mapping import Mapping
from   local.config.env import EnvConfig


class HeaderMapping(Mapping):
  
    DTD_URL = BaseConfig.CXML_DTD_URL

    STRUCTURE = [
        'Header/From/Credential/Identity',
        'Header/From/Correspondent/Contact/Name',
        'Header/From/Correspondent/Contact/PostalAddress',
        'Header/From/Correspondent/Contact/Email',
        'Header/To/Credential/Identity',
        'Header/To/Correspondent/Contact/Name',
        'Header/To/Correspondent/Contact/PostalAddress',
        'Header/Sender/Credential/Identity',
        'Header/Sender/UserAgent',
    ]

    FIELD_TO_ACTION_MAPS = [dict(
        BuyerDomain=cxmlinvbot.mapping.action.Default('Header/To/Credential@domain', 'DUNS'), # Should really be in the CSV, not a problem if we only have 1 buyer
        BuyerID=cxmlinvbot.mapping.action.Default('Header/To/Credential/Identity', 'CBREUK'), # Should really be in the CSV, not a problem if we only have 1 buyer
        DeploymentMode=cxmlinvbot.mapping.action.Default('Request@deploymentMode', EnvConfig.DEPLOYMENT_MODE), # 'production' or 'test'
        ContactName=cxmlinvbot.mapping.action.Default(('Header/To/Correspondent/Contact/Name',
                                            'Header/To/Correspondent/Contact/PostalAddress/DeliverTo'),
                                            'CBRE MANAGED SERVICES LIMITED'),
        EmailAddress=cxmlinvbot.mapping.action.Default('Header/From/Correspondent/Contact/Email', 'creditcontrol@prodoor.co.uk'),
        POAddressLine1=cxmlinvbot.mapping.action.Default('Header/To/Correspondent/Contact/PostalAddress/Street', '61 SOUTHWARK STREET'),
        POCity=cxmlinvbot.mapping.action.Default('Header/To/Correspondent/Contact/PostalAddress/City', 'London'),
        POPostalCode=cxmlinvbot.mapping.action.Default('Header/To/Correspondent/Contact/PostalAddress/PostalCode', 'SE1 0HL'),
        POCountry=cxmlinvbot.mapping.action.Default('Header/To/Correspondent/Contact/PostalAddress/Country@isoCountryCode', 'GB'),
        SAAddressName=cxmlinvbot.mapping.action.Default(('Header/From/Correspondent/Contact/Name',
                                            'Header/From/Correspondent/Contact/PostalAddress/DeliverTo'),
                                            'Pro Door (UK) Limited'),
        SAAddressLine1=cxmlinvbot.mapping.action.Default('Header/From/Correspondent/Contact/PostalAddress/Street', 'Academy House'),
        SAAddressLine2=cxmlinvbot.mapping.action.Default('Header/From/Correspondent/Contact/PostalAddress/Street', '241 Chertsey Road'),
        SAAddressLine3=cxmlinvbot.mapping.action.Default('Header/From/Correspondent/Contact/PostalAddress/City', 'Addlestone'),
        SAAddressLine4=cxmlinvbot.mapping.action.Default('Header/From/Correspondent/Contact/PostalAddress/State','Surrey'),
        SAPostalCode=cxmlinvbot.mapping.action.Default('Header/From/Correspondent/Contact/PostalAddress/PostalCode', 'KT15 2EW'),
        SACountry=cxmlinvbot.mapping.action.Default('Header/From/Correspondent/Contact/PostalAddress/Country@isoCountryCode', 'GB'),
        SharedSecret=cxmlinvbot.mapping.action.Default('Header/Sender/Credential/SharedSecret', 'none'),
        SupplierDomain=cxmlinvbot.mapping.action.Default(('Header/From/Credential@domain',
                                                'Header/Sender/Credential@domain'),
                                                'DUNS'), 
        SupplierID=cxmlinvbot.mapping.action.Default(('Header/From/Credential/Identity',
                                            'Header/Sender/Credential/Identity'),
                                            'PRODOORMA'), # Default to 'PRODOORMA' as there are so few invoices for the 'PRODOORGWS' entity that they can be entered manually
        Version=cxmlinvbot.mapping.action.Default('@version', BaseConfig.DTD_VERSION),
        PayloadID=cxmlinvbot.mapping.action.Lambda('@payloadID', lambda : '%s@prodoor.com'%int(datetime.datetime.now().timestamp()), ()),
        TimeStamp=cxmlinvbot.mapping.action.Lambda('@timestamp', lambda : datetime.datetime.now().isoformat(), ()),
        Language=cxmlinvbot.mapping.action.Default(('Header/From/Correspondent/Contact/Name@xml:lang',
                                         'Header/To/Correspondent/Contact/Name@xml:lang',
                                         '@xml:lang'),
                                         'en'),
        UserAgent=cxmlinvbot.mapping.action.Default('Header/Sender/UserAgent', 'Pro Door Invoice Bot %s' % BaseConfig.VERSION),
        
    )]