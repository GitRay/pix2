# $Id: Album.py 304 2006-01-20 23:40:32Z quarl $

## Copyright (C) 2005, 2006 Karl Chen
## Copyright (C) 2005 Demian Neidetcher

## This file is part of QuickyPix.

## QuickyPix is free software; you can redistribute it and/or modify it under
## the terms of the GNU General Public License as published by the Free
## Software Foundation; either version 2, or (at your option) any later
## version.

## QuickyPix is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.

## You should have received a copy of the GNU General Public License along
## with QuickyPix; see the file COPYING.  If not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
## USA.

# Add support for 'yield' in Python2.2
# (in Python2.3, this statement is not needed.  Python < 2.2 is not
# supported.)
from __future__ import generators

import sys, os, string
from Pic import Pic, findPic
import config
import util

def sorted(l):
    l = l[:]
    l.sort()
    return l

def reverse_sorted(l):
    l = l[:]
    l.sort()
    l.reverse()
    return l

album_sort = {
    'sorted': sorted,
    'reverse_sorted': reverse_sorted,
    'None': None
    }

class Album(object):
    def __init__(self, path):
        # path should start with / and be relative to config.ALBUMS_DIR
        assert(path.startswith('/'))
        self.path = os.path.join(path,'')
        self._albums = None

    def _get_rel_path(self):
        return os.path.basename(os.path.dirname(self.path))
    rel_path = property(_get_rel_path)

    def _get_fullpath(self):
        return self.path
    fullpath = property(_get_fullpath)

    def default_highlight_name(self):
        return self.pics and self.pics[0].rel_path or ''

    highlight_name = util.metadata_property('.highlight', default_highlight_name)

    def _get_highlight(self):
        h = self.highlight_name
        if not h:
            return None

        return findPic(os.path.join(self.path, h),dir_ok=True)

    def _set_highlight(self, h):
        self.highlight_name = h.rel_path
    highlight = property(_get_highlight, _set_highlight)

    def default_title(self):
        basename = os.path.basename(os.path.dirname(self.path))
        return config.DEFAULT_TITLE %locals()

    title = util.metadata_property('.title', default_title)
    comment = util.metadata_property('.comment')

    def m_rel_path(self):
        if config.authenticated and config.ALWAYS_USE_PUBLIC_FOR_PHOTOS:
            return config.PUBLIC_ROOT + self.path
        else:
            return self.rel_path

    def _get_breadcrumb(self):
        return '<a href="%s%s">%s</a>' %(config.root, self.path, self.title)
    breadcrumb = property(_get_breadcrumb)

    def img_listdir(self):
        paths = os.listdir(config.ALBUMS_DIR + self.path)
        if self.path == '/':
            paths = album_sort[config.SORT_ROOT] (paths)
        else:
            paths = album_sort[config.SORT_NONROOT] (paths)

        for entry in paths:
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
