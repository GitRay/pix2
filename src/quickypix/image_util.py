# $Id: image_util.py 174 2005-10-15 08:58:42Z quarl $

import time
import config
import os
import re
import commands
import exif
import util

# use PIL if available
try:
    import image_pil as image_ops
except ImportError:
    #util.log("Python Imaging Library (http://www.pythonware.com/products/pil/) not available\n")
    import image_im as image_ops

def reformat_exif_time(time_str):
    if not time_str or str(time_str) == '0000:00:00 00:00:00':
        return None
    t = time.strptime(str(time_str), '%Y:%m:%d %H:%M:%S')
    return time.strftime(config.TIME_FORMAT, t)

def dimensions_equal(d1, d2):
    # returns True if d1==d2 or == with swapped order (i.e. picture was
    # rotated)
    if d1 == None: return d1 == d2
    return d1 == d2 or d1 == (d2[1],d2[0])

class image_info:
    def __init__(self, fpath):
        self.time_str = None
        self.original_dimensions = None
        self.dimensions = None
        self.file_size = os.stat(fpath).st_size
        self.video_codec = None
        self.duration = None
        if util.path_ext(fpath) in ['jpg', 'jpeg']:
            self.process_exif(fpath)
        else:
            self.process_tcprobe(fpath)

    def process_exif(self, fpath):
        d = exif.process_file(open(fpath,'rb'))
        self.dimensions = image_ops.get_size(fpath)
        if d:
            self.time_str = reformat_exif_time(d.get('EXIF DateTimeOriginal'))
            l = d.get('EXIF ExifImageLength')
            w = d.get('EXIF ExifImageWidth')
            if l and w:
                self.original_dimensions = (int(str(w)),int(str(l)))

    def process_tcprobe(self, fpath):
        cmd = 'tcprobe -i' + commands.mkarg(fpath)
        output = commands.getoutput(cmd)
        m = re.search('frame size: -g ([0-9]+)x([0-9]+) ', output)
        if m:
            self.dimensions = int(m.group(1)), int(m.group(2))
        m = re.search('frame rate: -f ([0-9]+[.][0-9]*) ', output)
        if m:
            self.frame_rate = float(m.group(1))
        m = re.search('length: .*duration=([0-9]+):([0-9]+):([0-9]+[.][0-9]*)', output)
        if m:
            self.duration = (int(m.group(1))*60 + int(m.group(2)))*60 + float(m.group(3))
        m = re.search('V:.*codec=([A-Za-z0-9]+)', output)
        if m:
            self.video_codec = m.group(1)

def do_convert_to_image(source_file, target_file):
    # TODO: add filmstrip border or something to show it's a movie
    # if os.spawnlp(os.P_WAIT, 'convert', 'convert', source_file, target_file):
    #     raise "Couldn't convert %s"%source_file
    if os.spawnlp(os.P_WAIT, '/home/quarl/bin/movie2jpg', 'movie2jpg', source_file, target_file):
        raise "Couldn't convert %s"%source_file

def convert_to_image(movie_file, image_file):
    util.ensure_dir(image_file)
    if not os.path.exists(image_file) or util.newer_than(movie_file,image_file):
        do_convert_to_image(movie_file, image_file)


def reencode(file):
    # re-encode a file (hopefully using a better codec and/or encoder - for
    # avi files the mencoder DivX4 encoder shrinks the file by more than 50%)
    if util.path_ext(file) in config.MOVIE_TYPES:
        cmd = ['mencoder', '-quiet', '-oac', 'copy', file, '-ovc', 'lavc',
               '-lavcopts', 'vcodec=mpeg4', '-o', tmp]
    else:
        cmd = ['convert', file, tmp]

def rotate_image(file, degrees):
    tmp = file+'.tmp'
    ext = util.path_ext(file)
    if ext in config.MOVIE_TYPES:
        cmd = ['/home/quarl/bin/movie-rotate', file, tmp, str(degrees)]
    elif ext in config.IMAGE_TYPES:
        cmd = ['convert', '-rotate', str(degrees), file, tmp]
    else:
        raise Exception("Invalid file type - not movie or image: '%s'"%file)
    if os.spawnlp(os.P_WAIT, cmd[0], *cmd):
        raise Exception("Couldn't rotate '%s'"%file)
    util.tdel(file)
    os.rename(tmp, file)

def resize_image(fpath, resized_fpath, (new_width, new_height), movie):
    # Resize an image and cache it as resized_fpath.  Returns the filename
    # which could be resized_fpath or fpath; it could be fpath if fpath is
    # bigger than the requested size.
    if os.path.exists(resized_fpath):
        # if cache exists and it's newer than the original...
        if util.newer_than(resized_fpath, fpath):
            return resized_fpath
    util.ensure_dir(resized_fpath)
    original_width, original_height = image_ops.get_size(fpath)
    if original_width < new_width and original_height < new_height:
        # original picture already smaller
        if movie:
            # still need to add label
            pass
        else:
            # don't need to do anything - use original
            return fpath
    else:
        original_aspect = float(original_width)/original_height
        if (float(new_width)/new_height) < original_aspect:
            new_height = int(new_width / original_aspect)
        else:
            new_width = int(new_height * original_aspect)

    image_ops.resize(fpath, resized_fpath, (new_width, new_height), movie)
    return resized_fpath
