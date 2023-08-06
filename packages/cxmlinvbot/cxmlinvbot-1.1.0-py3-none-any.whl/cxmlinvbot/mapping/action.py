import datetime
import logging

from   cxmlinvbot.errors.errors import MapActionError

logger = logging.getLogger(__name__)


class MapAction(object):
    
    def __init__(self, paths=None):
        self._paths = paths if type(paths) == type(()) or type(paths) == list else [paths]

    def perform(self, key, nvPairs):
        return {}


class Default(MapAction):

    def __init__(self, paths, defVal):
        super(Default, self).__init__(paths)
        self._defVal = defVal

    def perform(self, key, nvPairs):
        m = {}
        for p in self._paths:
            tmp = nvPairs.get(key, '')
            m[p] = tmp if len(tmp) else self._defVal
        return m
            

class Ignore(MapAction):
    pass


class Lambda(MapAction):
    
    def __init__(self, paths, op, keys):
        super(Lambda, self).__init__(paths)
        self._op = op
        self._keys = keys
    
    def perform(self, _, nvPairs):
        m = {}
        for p in self._paths:

            args = []
            for k in self._keys:
                arg = nvPairs.get(k, '')
                if not len(arg):
                    raise MapActionError('Lambda field %s is missing from invoice CSV.' % k)
                if '.' in arg:
                    arg = float(arg)
                elif '/' in arg:
                    arg = datetime.datetime.strptime(arg, '%d/%m/%Y')
                else:
                    arg = int(arg)
                args.append(arg)
            m[p] = str(self._op(*args))
        return m 


class Required(MapAction):
    
    def perform(self, key, nvPairs):
        m = {}
        for p in self._paths:
            m[p] = nvPairs.get(key, '')
            if not len(m[p]):
                raise MapActionError('Required field %s is missing from invoice CSV.' % key)

        return m 


class TBD(MapAction):
    pass


