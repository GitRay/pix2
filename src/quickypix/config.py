# $Id: config.py 113 2005-09-27 23:28:33Z quarl $

ALBUMS_DIR = '/srv/albums'

CACHE_DIR = '/var/cache/pix'
LOG_PATH = '/var/log/pix.log'

TEMPLATES_FILE = '/home/quarl/proj/quickypix/src/html/template.html'
STYLE_FILE = '/home/quarl/proj/quickypix/src/html/style.css'

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

TDEL_PATH = '/home/quarl/bin/tdel'
