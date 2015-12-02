## This file is part of Pix2.
## While Pix2 is licensed under the GNU General Public License, 
## this particular file is released into the public domain by its
## sole author, Ray Cathcart.
import os, sys

seperator  = '&raquo;'
pixVersion = '2.0.0'

# Absolute path to the CGI directory on your webserver
pathToCGI = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),'cgi-bin')
#pathToCGI = '/usr/local/www/apache22/cgi-bin'
webPathToCGI = '/cgi-bin'

# Absolute path to the photo album on the webserver
albumLoc = os.path.join(pathToCGI,os.pardir,'test_album')

# Absolute path to the other web resources (including template.html)
pathToTemplate = os.path.join(pathToCGI,os.pardir)
#pathToTemplate = '/usr/local/www/apache22/data'
webPathToTemplate = '/'

# Path that appears in url when at your webserver's root location
pathToWebRoot = '/'

# Absolute path to the picture cache folder
#pathToPicCache = '/usr/local/www/apache22/data/pic_cache'
pathToPicCache = os.path.join(pathToCGI,os.pardir,'pic_cache')
webPathToPicCache = '/pic_cache'

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
