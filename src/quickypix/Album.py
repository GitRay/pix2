# $Id: Album.py 141 2005-10-10 00:35:05Z quarl $

import sys, os, string
from Pic import Pic, findPic
import config
import util

def sorted(l):
    l = l[:]
    l.sort()
    return l

class Album(object):
    def __init__(self, path):
        # path should start with / and be relative to config.ALBUMS_DIR
        assert(path.startswith('/'))
        self.path = os.path.join(path,'')
        self._albums = None
        if not self.title:
            try:
                self.title = '(%s)' %os.path.basename(os.path.dirname(self.path))
            except util.AccessError, e:
                #print >>sys.stderr, "QuickyPix: warning: AccessError while setting title"
                pass
        if not self.highlight_name:
            try:
                self.highlight_name = self.default_highlight_name()
            except util.AccessError, e:
                #print >>sys.stderr, "QuickyPix: warning: AccessError while setting highlight"
                pass

    def _get_rel_path(self):
        return os.path.basename(os.path.dirname(self.path))
    rel_path = property(_get_rel_path)

    def _get_fullpath(self):
        return self.path
    fullpath = property(_get_fullpath)

    highlight_name = util.metadata_property('.highlight')

    def _get_highlight(self):
        h = self.highlight_name
        if not h:
            return None

        return findPic(os.path.join(self.path, h),dir_ok=True)

    def _set_highlight(self, h):
        self.highlight_name = h.rel_path
    highlight = property(_get_highlight, _set_highlight)

    title = util.metadata_property('.title')
    comment = util.metadata_property('.comment')

    def _get_breadcrumb(self):
        return '<a href="%s%s">%s</a>' %(config.root, self.path, self.title)
    breadcrumb = property(_get_breadcrumb)

    def default_highlight_name(self):
        try:
            return self.img_listdir().next()
        except:
            return ''

    def img_listdir(self):
        for entry in sorted(os.listdir(config.ALBUMS_DIR + self.path)):
            if entry.startswith('.'): continue
            if entry == 'lost+found': continue
            yield entry

    def _contents(self):
        if self._albums is not None: return
        self._albums = []
        self._pics = []
        assert(self.path.startswith('/'))
        for entry in self.img_listdir():
            path = os.path.join(self.path, entry)
            fpath = config.ALBUMS_DIR + path
            if os.path.isfile(fpath) and util.is_media(fpath):
                self._pics.append(Pic(path))
            elif os.path.isdir(fpath):
                self._albums.append(Album(path))

    def _get_albums(self):
        self._contents()
        return self._albums
    albums = property(_get_albums)

    def _get_pics(self):
        self._contents()
        return self._pics
    pics = property(_get_pics)
