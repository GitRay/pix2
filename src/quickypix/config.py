# $Id: config.py 190 2005-10-21 08:57:34Z quarl $

# This file was placed in the public domain by Karl Chen, 2005.

ALBUMS_DIR = '/srv/albums'

CACHE_DIR = '/var/cache/pix'
LOG_PATH = '/var/log/pix.log'

# TEMPLATES_FILE = '/home/quarl/proj/quickypix/src/html/template.html'
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

# this is the program invoked to perform deletions; you can use /bin/rm if you
# want, or disable deletions with e.g. /bin/false.
#
# You can get tdel at http://www.quarl.org/~quarl/kc-bin/tdel
TDEL_PATH = '/home/quarl/bin/tdel'

import os
# This is the normal root of the URL to use in referring to self.
# The default, $SCRIPT_NAME, works for Apache.
root = os.environ.get('SCRIPT_NAME','')

# Not all web servers set SCRIPT_NAME to the virtual (pre-redirected) script
# path.  An alternative is to derive our virtual script name by subtracting
# PATH_INFO from REQUEST_URI. (Note, however, that REQUEST_URI is escaped, and
# PATH_INFO is not.)
#     escaped_path_info = util.escUrl(os.environ.get('PATH_INFO'))
#     root = os.environ.get('REQUEST_URI')[:-len(escaped_path_info)]

# Another alternative is to simply hardcode the path you want.
