# $Id$

# Support for image operations using ImageMagick, when PIL is not available
# (and for things PIL can't handle).

import os
import re
import commands

def resize(fpath, resized_fpath, (new_width, new_height), movie):
    cmd = ['convert', '-thumbnail', '%dx%d' %(new_width, new_height)]
    # print >>open('/tmp/pix.log','a'), cmd
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
    cmd = 'identify' + commands.mkarg(fpath)
    m = re.search(' (?:PNG|JPEG|GIF) ([0-9]+)x([0-9]+) ', commands.getoutput(cmd))
    if m:
        return int(m.group(1)), int(m.group(2))
    else:
        raise "Couldn't get image size of %s"%fpath
