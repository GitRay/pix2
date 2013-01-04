# $Id: config.py 262 2005-12-07 21:29:43Z quarl $

import sys, os
def prog_dir(*p):
    return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), *p)

# This file was placed in the public domain by Karl Chen, 2005.

## Directory tree containing pictures
ALBUMS_DIR = '/srv/albums'

## Directory to write cache files, must be writable by Apache CGI/SCGI user
##   Example of how to do this as root:
##      mkdir /var/cache/quickypix && chown www-data /var/cache/quickypix
CACHE_DIR = '/var/cache/quickypix'

## File to write log data, must be writable by Apache CGI/SCGI user
##   Example of how to do this as root:
##      touch /var/log/quickypix.log && chown www-data /var/log/quickypix.log
LOG_PATH = '/var/log/quickypix.log'

## An example is in html/template.html
# TEMPLATES_FILE = '/home/quarl/proj/quickypix/src/html/template.html'

## An example is in html/style.css
# STYLE_FILE = '/home/quarl/proj/quickypix/src/html/style.css'

TEMPLATES_FILE = '/home/quarl/proj/quickypix/src/html/photo.quarl.org/template.html'
STYLE_FILE = '/home/quarl/proj/quickypix/src/html/photo.quarl.org/style.css'

## Which stats to display
DISPLAY_INFO = ['time_str', 'dimensions', 'original_dimensions',
                'duration', 'video_codec', 'file_size']

## Available stats:
DISPLAY_INFO = ['time_str', 'dimensions', 'original_dimensions',
                'frame_rate', 'duration', 'video_codec', 'file_size',
                'aperture', 'exposure', 'iso']

## Default title to use when none specified by .title file
DEFAULT_TITLE = '%(basename)s'

## When using edit mode, you have two separate websites that link to each
## other.  EDIT_ROOT is used by the public site to link to the admin site, and
## PUBLIC_ROOT vice versa.
EDIT_ROOT = 'https://quarl.org/pix'
PUBLIC_ROOT = 'http://photo.quarl.org'

WEB_SIZE = 500,400
THUMB_SIZE = 80,60
ALBUM_THUMB_SIZE = 100,75

IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
MOVIE_TYPES = ['avi', 'mpg']
MEDIA_TYPES = IMAGE_TYPES + MOVIE_TYPES

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# how many seconds have to pass before something is no longer
# 'recently-modified'
RECENT_THRESHOLD = 120

## Path for helper programs.
##
## They are distributed with QuickyPix at quickypix/src/helpers/bin
##
## The authoritative source is http://svn.quarl.org/repos/quarl/trunk/bin or
## http://www.quarl.org/~quarl/kc-bin/
HELPER_PATH = prog_dir('../helpers/bin') # '/home/quarl/proj/quickypix/src/helpers/bin/'

## This is the program invoked to perform deletions; you can use /bin/rm if
## you want, or disable deletions with e.g. /bin/false.
PATH_TDEL = os.path.join(HELPER_PATH, 'tdel')

## Program for making thumbnails of movies
PATH_MOVIE2JPG = os.path.join(HELPER_PATH, 'movie2jpg')

## Program for rotating movies
PATH_MOVIE_ROTATE = os.path.join(HELPER_PATH, 'movie-rotate')


## Path for ImageMagick components.  Can be '' if they are installed system-wide
## (/usr/bin, etc.)
IMAGEMAGICK_PATH = ''

PATH_CONVERT = os.path.join(IMAGEMAGICK_PATH, 'convert')

PATH_IDENTIFY = os.path.join(IMAGEMAGICK_PATH, 'identify')

## If you have ImageMagick version 6 or later, you can use 'convert
## -thumbnail', else you have to set this to False to use 'convert -resize'.
##
## '-thumbnail' results in smaller thumbnail files by deleting unneeded
## profile data; no other difference.
USE_IMAGEMAGICK_THUMBNAIL_OPTION = True

## Path for Mplayer components.  Can be '' if they are installed system-wide
## (/usr/bin, etc.)
MPLAYER_PATH = ''

PATH_MENCODER = os.path.join(MPLAYER_PATH, 'mencoder')

## Path for Transcode components.  Can be '' if they are installed system-wide
## (/usr/bin, etc.)
TRANSCODE_PATH = ''

PATH_TCPROBE = os.path.join(TRANSCODE_PATH, 'tcprobe')

## Use PIL, if available.
##
## It can be faster to use PIL than ImageMagick because it doesn't require
## forking another process.  Some operations are not supported by PIL.  The
## JPEG quality of PIL resizing must be hard-coded, whereas ImageMagick can
## adaptively use the estimated quality of the input image.
USE_PIL = False

## The document root to use for URLs.  If it is None, the default is
## os.environ['SCRIPT_NAME'].
##
## Since some web servers do not send the right string, you may want to
## hardcode it, or look at other environment variables.
ROOT = None
