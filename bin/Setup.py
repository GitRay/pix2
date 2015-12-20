## This file is part of Pix2.
## While Pix2 is licensed under the GNU General Public License, 
## this particular file is released into the public domain by its
## sole author, Ray Cathcart.

# You will need to change these entries to reflect your local setup. The default
# values support running the tests and starting a test wsgi server via the
# "start_wsgi_server.py" script in the top level directory.

import os, sys

seperator  = '&raquo;'
pixVersion = '2.1.0'

# Set to False if you don't want the wsgi application to serve static files.
# A properly configured server will serve the static files separately and only
# request dynamic files from the wsgi application. The test server serves both,
# but makes a note in the log. It's almost certainly a security issue.
serveStaticFiles = True

# Absolute path to the bin directory on your webserver
pathToCGI,_ = os.path.split(os.path.realpath(__file__))
#pathToCGI = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),'bin')

# Absolute path to the photo album on the webserver
albumLoc = os.path.join(pathToCGI,os.pardir,'test_album')

# Absolute path to template.html
pathToTemplate = os.path.join(pathToCGI,'template.html')

# Absolute path to static web files (layout.css, style.css, etc.)
pathToStatic = os.path.join(pathToCGI,os.pardir,'static')
webPathToStatic = '/'

# Path that appears in url when at your webserver's root location
pathToWebRoot = '/'

# Absolute path to the picture cache folder. This folder contains the resized
# pictures, which need to be accessable as static images by the web server.
#pathToPicCache = '/usr/local/www/apache22/data/pic_cache'
pathToPicCache = os.path.join(pathToStatic,'pic_cache')
webPathToPicCache = '/pic_cache'

# PIL or pillow are the Python Image Library. Performance will be better with
# one of these installed. ImageMagick is also supported, but each operation
# spawns a new process, so performance is worse in most cases.
# if this is false we try to use ImageMagick
# if you set it to true we try to import and use PIL
USE_PIL = True

# Path to the imageMagick "identify" and "convert" utilities
if os.path.isfile('/opt/local/bin/identify'):
    pathToIdentify = '/opt/local/bin/identify' # Mac using ports
    pathToConvert = '/opt/local/bin/convert'
elif os.path.isfile('/usr/local/bin/identify'):
    pathToIdentify = '/usr/local/bin/identify'  # FreeBSD using ports
    pathToConvert = '/usr/local/bin/convert'
elif os.path.isfile('/usr/bin/identify'):
    pathToIdentify = '/usr/bin/identify'  # Debian
    pathToConvert = '/usr/bin/convert'
elif os.path.isfile(r"C:\Program Files\ImageMagick-6.9.2-Q16\identify.exe"):
    pathToIdentify = r"C:\Program Files\ImageMagick-6.9.2-Q16\identify.exe"     # Windows
    pathToConvert = r"C:\Program Files\ImageMagick-6.9.2-Q16\convert.exe"
    
# list the image formats you want to include in the album
image_formats = ['JPG', 'JPEG', 'TIF', 'TIFF', 'PICT', 'GIF', 'BMP', 'PSD', 'PNG', 'PCT']
video_formats = ['MP4', 'M4A', 'M4P', 'M4B', 'M4R', 'M4V', 'MPG', 'MPEG', 'M2P', 'PS', 'TS', 'MOV', 'QT', 'AVI', '3GP', '3P2', 'SWF']

# Maximum filename length
f_namemax = os.statvfs(pathToPicCache).f_namemax
