import os, sys

seperator  = '|'
pixVersion = '1.4.0'

# Absolute path to the CGI directory on your webserver
pathToCGI = os.path.abspath(os.path.dirname(sys.argv[0]))

# Absolute path to the photo album on the webserver
albumLoc = os.path.join(pathToCGI,'..','test_album')

# Absolute path to the other web resources (including template.html)
pathToTemplate = os.path.join(pathToCGI,'..')

# Absolute path to the web root - the base web server directory
pathToWebRoot = os.path.join(pathToCGI,'..')

# if this is false we try to use ImageMagick
# if you set it to true we try to import and use PIL
USE_PIL = True

# Path to the imageMagick "indentify" and "convert" utilities
pathToIdentify = '/opt/local/bin/identify'
pathToConvert = '/opt/local/bin/convert'
