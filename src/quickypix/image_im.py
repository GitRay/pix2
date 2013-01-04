# $Id: image_im.py 258 2005-12-07 21:06:57Z quarl $

# Support for image operations using ImageMagick, when PIL is not available
# (and for things PIL can't handle).

## Copyright (C) 2005 Hollis Blanchard
## Copyright (C) 2005 Karl Chen

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

import os
import re
import commands
import config

def resize(fpath, resized_fpath, (new_width, new_height), movie):
    if config.USE_IMAGEMAGICK_THUMBNAIL_OPTION:
        param = '-thumbnail'
    else:
        param = '-resize'
    cmd = [ config.PATH_CONVERT, param, '%dx%d' %(new_width, new_height)]

    # if it was originally a movie, then add a label saying so
    if movie:
        if new_width > 80:
            pointsize = 12
        else:
            pointsize = 8
        cmd += [ '-fill', 'white', '-box', '#00000080',
                 '-gravity', 'NorthEast',
                 '-draw', 'text 5,5 " movie "',
                 '-pointsize', str(pointsize) ]
    cmd += [fpath, resized_fpath]

    if os.spawnlp(os.P_WAIT, cmd[0], *cmd):
        raise "Couldn't resize picture"

def get_size(fpath):
    cmd = config.PATH_IDENTIFY + commands.mkarg(fpath)
    m = re.search(' (?:PNG|JPEG|GIF) ([0-9]+)x([0-9]+) ', commands.getoutput(cmd))
    if m:
        return int(m.group(1)), int(m.group(2))
    else:
        raise "Couldn't get image size of %s"%fpath
