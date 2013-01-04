# $Id: image_util.py 339 2006-01-25 21:52:26Z quarl $

## Copyright (C) 2005, 2006 Karl Chen

## This file is part of QuickyPix.

## QuickyPix is free software; you can redistribute it and/or modify it under
## the terms of the GNU General Public License as published by the Free
## Softfixed;ware Foundation; either version 2, or (at your option) any later
## version.

## QuickyPix is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.

## You should have received a copy of the GNU General Public License along
## with QuickyPix; see the file COPYING.  If not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
## USA.

import time
import config
import os
import re
import commands
import exif
import util
import config

# TODO: exif.py doesn't seem to get the EXIF ImageDescription field. Why?

# use PIL if available
try:
    if config.USE_PIL:
        import image_pil as image_ops
    else:
        raise ImportError
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
        self.frame_rate = None
        self.duration = None
        self.aperture = None
        self.iso = None
        self.exposure = None
        self.description = None
        if util.path_ext(fpath).lower() in ['jpg', 'jpeg']:
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
            self.aperture = d.get('EXIF ApertureValue')
            self.iso = d.get('EXIF ISOSpeedRatings')
            self.exposure = d.get('EXIF ExposureTime')
            self.description = d.get('EXIF ImageDescription')

    def process_tcprobe(self, fpath):
        cmd = config.PATH_TCPROBE + ' -i' + commands.mkarg(fpath)
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

    def describe(self, what):
        func = getattr(self, 'describe_'+what)
        assert(func)
        return func()

    def describe_time_str(self):
        if self.time_str:
            return 'Picture taken', self.time_str
    def describe_dimensions(self):
        if self.dimensions:
            return 'Dimensions', '%dx%d'%self.dimensions
    def describe_original_dimensions(self):
        if self.original_dimensions and not dimensions_equal(self.dimensions, self.original_dimensions):
            return 'Original Dimensions', '%dx%d'%self.original_dimensions
    def describe_frame_rate(self):
        if self.frame_rate:
            return 'Frame Rate', self.frame_rate
    def describe_duration(self):
        if self.duration:
            return 'Duration', '%.1f sec'%self.duration
    def describe_video_codec(self):
        if self.video_codec:
            return 'Video codec', self.video_codec
    def describe_file_size(self):
        if self.file_size:
            return 'File size', '%s bytes'%util.commify(self.file_size)
    def describe_aperture(self):
        if self.aperture:
            try:
                aperture = util.frac_to_dec(self.aperture)
            except ValueError:
                # malformed fraction
                aperture = self.aperture
            return 'Aperture', aperture
    def describe_exposure(self):
        if self.exposure:
            return 'Exposure', self.exposure
    def describe_description(self):
        if self.description:
            return 'Description', self.description
    def describe_iso(self):
        if self.iso:
            return 'ISO', self.iso

def do_convert_to_image(source_file, target_file):
    # TODO: add filmstrip border or something to show it's a movie
    # if os.spawnlp(os.P_WAIT, 'convert', 'convert', source_file, target_file):
    #     raise "Couldn't convert %s"%source_file
    if os.spawnlp(os.P_WAIT, config.PATH_MOVIE2JPG, 'movie2jpg', source_file, target_file):
        raise "Couldn't convert %s"%source_file

def convert_to_image(movie_file, image_file):
    util.ensure_dir(image_file)
    if not os.path.exists(image_file) or util.newer_than(movie_file,image_file):
        do_convert_to_image(movie_file, image_file)


def reencode(file):
    # re-encode a file (hopefully using a better codec and/or encoder - for
    # avi files the mencoder DivX4 encoder shrinks the file by more than 50%)
    if util.path_ext(file) in config.MOVIE_TYPES:
        cmd = [ config.PATH_MENCODER, '-quiet', '-oac', 'copy', file, '-ovc', 'lavc',
               '-lavcopts', 'vcodec=mpeg4', '-o', tmp]
    else:
        cmd = [ config.PATH_CONVERT, file, tmp]

def rotate_image(file, degrees):
    tmp = file+'.tmp'
    ext = util.path_ext(file)
    if ext.lower() in config.MOVIE_TYPES:
        cmd = [ config.PATH_MOVIE_ROTATE, file, tmp, str(degrees)]
    elif ext.lower() in config.IMAGE_TYPES:
        cmd = [ config.PATH_CONVERT, '-rotate', str(degrees), file, tmp]
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
