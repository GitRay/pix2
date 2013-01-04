# $Id: config.py 157 2005-10-15 07:05:15Z quarl $

ALBUMS_DIR = '/srv/albums'

CACHE_DIR = '/var/cache/pix'
LOG_PATH = '/var/log/pix.log'

# TEMPLATES_FILE = '/home/quarl/proj/quickypix/src/html/template.html'
# STYLE_FILE = '/home/quarl/proj/quickypix/src/html/style.css'
TEMPLATES_FILE = '/home/quarl/proj/quickypix/src/html/photo.quarl.org/template.html'
STYLE_FILE = '/home/quarl/proj/quickypix/src/html/photo.quarl.org/style.css'

EDIT_ROOT = 'https://quarl.org/pix'
PUBLIC_ROOT = 'http://photo.quarl.org'

WEB_SIZE = 500,400
THUMB_SIZE = 80,60
ALBUM_THUMB_SIZE = 100,75

IMAGE_TYPES = ['jpg', 'png', 'bmp', 'gif']
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
