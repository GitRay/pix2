# $Id: util.py 165 2005-10-15 08:41:42Z quarl $

import sys
import os
import re
import time
import urllib
import mimetypes
import config

FULLSIZE = 'fullsize'

# returns tuple (x,y) for requested size.  (-1,-1) means fullsize.
def parse_size(arg):
    if arg == FULLSIZE:
        return -1, -1
    m = re.match('^([0-9]+)x([0-9]+)$', arg)
    if not m: not_found()
    return tuple(map(int, m.groups()))

def sized(size):
    if size == (-1,-1):
        return FULLSIZE
    else:
        return "%dx%d" %size

def get_mime_type(path):
    m = mimetypes.guess_type(path)[0]
    if not m:
        raise "Don't know mime type for %s!"%path
    return m

def rfc1123time(unixtime=None):
    """Returns time format preferred for Internet standards.

    Leeched from rfc822.formatdate().

    Sun, 06 Nov 1994 08:49:37 GMT  ; RFC 822, updated by RFC 1123

    According to RFC 1123, day and month names must always be in
    English.  If not for that, this code could use strftime().  It
    can't because strftime() honors the locale and could generate
    non-English names.

    """
    timeval = time.gmtime(unixtime or time.time())
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][timeval[6]],
            timeval[2],
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][timeval[1]-1],
                                timeval[0], timeval[3], timeval[4], timeval[5])

def cat(path, save_filename=None):
    '''Write a file to an HTTP client on stdout.

    save_filename, if specified, is the filename to suggest to the browser
    to save the file as.

    if save_filename == 1, then it is basename(path) iff config.download_flag.
    '''

    stat = os.stat(path)
    print "Content-Type: %s" %get_mime_type(path)
    print "Content-Length: %s" %stat.st_size
    if save_filename == 1:
        save_filename = config.download_flag and os.path.basename(path)
    if save_filename:
        print 'Content-Disposition: attachment; filename="%s"'%save_filename
    print "Last-Modified: %s" %rfc1123time(stat.st_mtime)
    print

    # sys.stdout.write(open(path,'rb').read())
    f = open(path,'rb')
    while True:
        d = f.read(4096)
        if not d: break
        sys.stdout.write(d)


def error_forbidden():
    print 'Status: 403 Forbidden'
    print 'Content-type: text/html\n'
    print '<h1>Forbidden :(</h1>'
    raise SystemExit

def not_found():
    print 'Status: 404 Not found'
    print 'Content-type: text/html\n'
    print '<h1>File not found :(</h1>'
    print 'I couldn\'t find <code>%s</code>.'%config.request_uri
    raise SystemExit

def redirect(url):
    print "Status: 302 Moved Temporarily"
    print 'Location: %s' %url
    print
    raise SystemExit

def relative_url(url):
    return "%s/%s"%(
        os.path.dirname(reconstruct_current_url()), url)

def redirect_rel(url):
    redirect(relative_url(url))

def reconstruct_root_url():
    if os.environ.get('HTTPS') == 'on':
        proto = 'https'
    else:
        proto = 'http'
    return '%s://%s%s' %(proto, os.environ.get('HTTP_HOST'), config.root)

def reconstruct_current_url():
    return reconstruct_root_url() + config.input_path

def escHtml(st):
    """Return an escaped version of an HTML string.
    """
    if not st: return st
    st = st.replace("&", "&amp;")
    st = st.replace("<", "&lt;")
    st = st.replace(">", "&gt;")
    st = st.replace('"', "&quot;")
    return st

escUrl = urllib.quote

def str2paragraphs(st):
    if not st: return st
    return '<p>%s</p>' % st.replace('\n\n','</p><p>')

def commify(number):
    return commify_('%d'%number)

def commify_(str):
    if len(str) <= 3:
        return str
    return commify_(str[:-3]) + ',' + str[-3:]


def xstat(filename):
    try:
        return os.stat(filename)
    except OSError:
        return None

def recent(stat):
    return stat and (time.time()-stat.st_mtime < config.RECENT_THRESHOLD)

def read_file(filename):
    try:
        return open(filename).read().strip()
    except:
        return ''

class AccessError(Exception):
    def __init__(self, filename):
        self.filename = filename

    def print_exit(self):
        print "Status: 401 access denied"
        print "Content-Type: text/html"
        print
        print "<h1>Forbidden: %s</h1>" %self.filename
        raise SystemExit

def write_file(filename, data):
    try:
        open(filename,'w').write(data)
    except:
        raise AccessError(filename)


def log(stuff):
    print >>open(config.LOG_PATH,'a'), time.strftime('[%Y-%m-%d %H:%M:%S]'), stuff

class StrWithStat(str):
    pass

class MetadataProperty:
    def __init__(self, filename, cname):
        self.filename = filename
        self.cname = cname
        self.cache = None

    def get(self, obj):
        if self.cname in obj.__dict__:
            return obj.__dict__[self.cname]

        fn = config.ALBUMS_DIR + obj.path + self.filename
        v = StrWithStat(read_file(fn))
        v.stat = xstat(fn)
        v.recent = recent(v.stat)
        obj.__dict__[self.cname] = v
        return v

    def set(self, obj, value):
        value = value and value.strip() or ''
        old_value = self.get(obj)
        if old_value == value: return
        fn = config.ALBUMS_DIR + obj.path + self.filename
        if not obj.path.startswith('/') or '/' in self.filename or '../' in fn:
            raise ValueError
        #del obj.__dict__[self.cname]
        value.recent = True
        obj.__dict__[self.cname] = value
        write_file(fn, value)
        log("Modifying %s: from %s to %s"%(fn, repr(old_value), repr(value)))

def metadata_property(filename):
    # Returns a property with getter and setter for reading and writing file.
    # Memoized.  Automatic strip()ing.  Value returned by getter also has a
    # 'recent' subproperty.
    cname = 'cache|%s'%filename
    mp = MetadataProperty(filename, cname)
    return property(mp.get, mp.set)


badchars = re.compile('[/\\*?\n\r|~;&$^]')
def name_validate(rel_name):
    if (not rel_name or
        re.search(badchars,rel_name) or
        rel_name.startswith('.')):
        error_forbidden()

def ensure_dir(fpath):
    dir = os.path.dirname(fpath)
    if not os.path.exists(dir):
        os.makedirs(dir)

def newer_than(f1, f2):
    # print >>sys.stderr, "## %s=%d, %s=%d" %(f1,os.stat(f1).st_mtime , f2,os.stat(f2).st_mtime)
    return os.stat(f1).st_mtime > os.stat(f2).st_mtime

def tdel(fpath):
    if os.spawnlp(os.P_WAIT, config.TDEL_PATH, 'tdel', '-d',
                  fpath):
        raise "Couldn't tdel %s"%fpath

def path_ext(path):
    if '.' in path:
        return path.split('.')[-1]
    else:
        return ''

def path_nonext(path):
    if '.' in path:
        return path[:path.rfind('.')]
    else:
        return path

def is_media(path):
    return (path_ext(path) in config.MEDIA_TYPES)
