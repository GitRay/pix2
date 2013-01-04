
# config file for PRAT (see http://www.quarl.org/projects/prat/)

PROJ_NAME = 'quickypix'

REPO_BASE = 'https://svn.quarl.org/repos/%(PROJ_NAME)s'%locals()

REPO_TRUNK = '%(REPO_BASE)s/trunk/%(PROJ_NAME)s'%locals()
REPO_TAG_DIR = '%(REPO_BASE)s/tags'%locals()

RELEASES_DIR = '/home/quarl/proj/%(PROJ_NAME)s/www/releases'%locals()

DOC_OUTPUT = '/home/quarl/proj/%(PROJ_NAME)s/www/releases.htxt'%locals()
DOC_URL_DOWNLOAD_PREFIX = 'releases/'
