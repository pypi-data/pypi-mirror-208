import datetime
import glob
import logging
import re
import os

logger = logging.getLogger(__name__)


class ArchiveException(Exception):
    pass


class Archive(object):

    FMT = '%Y%m%d%H%M%S'
    
    def __init__(self, path, ext, period):
        logger.info('Creating Archive @%s for files of type %s for a period of %d days' % (path, ext, period))
        os.makedirs(path, exist_ok=True)
        self._path = path
        self._period = period
        self._ext = ext
        self._pattern = re.compile('(?P<datetime>[0-9]{14})\..*\.%s' % ext)
        
    def archive(self, path, name):
        new = '%s.%s' % (datetime.datetime.now().strftime(self.FMT), name)
        if self._pattern.fullmatch(new):
            newFP = '%s%s' % (self._path, new)
            os.rename('%s%s' %  (path, name), newFP)
            return newFP
        else:
            raise(ArchiveException('File to be archived (%s) does not match Arhive pattern (%s)' % (new, self._pattern.pattern)))

    def _hasArchiveExt(self, name):
        return name.split('.')[-1] == self._ext
    
    def createFile(self, name):
        if self._hasArchiveExt(name):
            new = '%s.%s' % (datetime.datetime.now().strftime(self.FMT), name)
        else:
            new = '%s.%s.%s' % (datetime.datetime.now().strftime(self.FMT), name, self._ext)
        if self._pattern.fullmatch(new):
            return open('%s%s' % (self._path, new), 'w')
        else:
            raise(ArchiveException('File to be archived (%s) does not match Arhive pattern (%s)' % (new, self._pattern.pattern)))

    def exists(self, name):
        tgt = name if self._hasArchiveExt(name) else '%s.%s' % (name, self._ext)
        return len(glob.glob('%s*.%s' % (self._path, tgt))) > 0
                      
    def cleanse(self):
        logger.info('Cleansing archive @%s' % self._path)
        files = glob.glob('*.%s' % self._ext, root_dir=self._path)
        for f in files:
            m = self._pattern.fullmatch(f)
            if m:
                d = datetime.datetime.strptime(m.group('datetime'), self.FMT).date()
                if (datetime.date.today() - d).days >= self._period:
                    logger.info('Deleting - %s%s' % (self._path, f))
                    os.remove('%s%s' % (self._path, f))




