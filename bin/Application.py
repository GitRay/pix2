from __future__ import print_function
import cgi, os, sys, traceback, posixpath, mimetypes, wsgiref, random
# python3 has different urllib paths
try:
    from urllib import unquote_plus
except:
    from urllib.parse import unquote_plus
from Presenter import Presenter
from Pic import Pic
from Album import Album
import Setup

class Application():
    # This is the class that is called by the wsgi server. Optionally it can be
    # called by a cgi script instead to simplify deployment.
    def __init__(self):
        # Make sure that either Imagemagick or PIL is installed
        try:
            from PIL import Image
            pil_installed = True
        except ImportError:
            pil_installed = False
            
        if Setup.USE_PIL and not pil_installed:
            print("You specify PIL in Setup.py, but you do not have PIL installed.\nGet PIL at http://www.pythonware.com/products/pil",file=sys.stderr)
            Setup.USE_PIL = False
            
        if not (os.path.isfile(Setup.pathToIdentify) and os.path.isfile(Setup.pathToConvert)):
            print("You do not have ImageMagick installed or the path to identify and convert is wrong in Setup.py.",file=sys.stderr)
            if not Setup.USE_PIL:
                print("Neither PIL nor ImageMagick is found. No picture functions will work at all.",file=sys.stderr)

    def __call__(self, environ, start_response):
        # this is the function called by the wsgi server
#        for x in environ:
#            if 'css' in str(environ[x]):
#                print('{}: {}'.format(x,environ[x]))
        try:
            iForm = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ.copy())
            
            album       = self._getArg(iForm, 'album')
            pic         = self._getArg(iForm, 'pic')
            control     = self._getArg(iForm, 'control')
            adminAction = self._getArg(iForm, 'admin')
            random_pic  = self._getArg(iForm, 'random')
            
            pict_creator = self._getArg(iForm, 'pict_creator')
            download = self._getArg(iForm, 'download')
            # assume that the application is invoked with either a blank path "/"
            # or something that starts with "index." (html, cgi, etc...)
            if not environ['PATH_INFO'][:7] == '/index.' and not environ['PATH_INFO'] == '/':
                if not Setup.serveStaticFiles:
                    # throw a 404 page
                    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
                    return [b'Not Configured to Serve Static Pages']
                    
                # Assume this is a static file. This should really be handled by
                # the web server, but we'll handle it here gracefully for poorly
                # configured servers or for testing with wsgiref
                print('Warning! Static file was served: {}'.format(os.path.normpath(environ['PATH_INFO'])),file=sys.stderr)
                # get path to file
                requested = os.path.join(
                    os.path.normpath(Setup.pathToStatic),
                    os.path.normpath(os.path.relpath(environ['PATH_INFO'],Setup.webPathToStatic))
                )
                print('File served: {}'.format(requested),file=sys.stderr)
                if not os.path.isfile(requested):
                    # throw a 404 page
                    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
                    return [b'Not Found']
                # get file extension
                _,ext = posixpath.splitext(environ['PATH_INFO'])
                if ext in self.extensions_map:
                    mime_txt = self.extensions_map[ext]
                elif ext.lower() in self.extensions_map:
                    mime_txt = self.extensions_map[ext]
                else:
                    mime_txt = self.extensions_map['']
                writer = start_response('200 OK', [('Content-Type',mime_txt)])
                f = open(requested,'rb')
                return wsgiref.util.FileWrapper(f, blksize=131072)
            if pict_creator != '':
                # make a picture
                pict_path = self._getArg(iForm, 'pict_path')
                pic_obj = Pic(start_response, os.path.join(Setup.albumLoc, pict_path))
                return pic_obj.spitOutResizedImage(pict_creator)
            elif download == 'jpeg':
                # download the picture, converted to jpeg if necessary
                pict_path = self._getArg(iForm, 'pict_path')
                pic_obj = Pic(start_response,os.path.join(Setup.albumLoc, pict_path))
                return pic_obj.downloadImage(download)
            elif random_pic != '':
                # send a single randomized photo
                # Using a recursion limit of 10 just for safety. Increase if necessary.
                if album == '':
                    currDir = Setup.albumLoc
                else:
                    currDir = os.path.join(Setup.albumLoc,album)
                album_obj = Album(currDir,start_response,recurse=10)
                # each album is recursively filled, and each contains pictures
                def get_albums(album):
                    album_list = [album]
                    for x in album.albums:
                        album_list.extend(get_albums(x))
                    return album_list
                all_albums = get_albums(album_obj)
                all_pics = []
                for x in all_albums:
                    all_pics.extend(x.pics)
                if len(all_pics) < 1:
                    # empty album
                    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
                    return [b'Empty Album']
                for x in range(1000000): # limit to a million tries so there is no infinite loop
                    random_pic = random.choice(all_pics)
                    if random_pic.isPic:
                        break
                [
                    pic_fname_safe, pic_relpic_safe, pic_name_safe, 
                    pic_relweb_safe, pic_width, pic_height
                ] = random_pic.getResizedLink('web') 
                start_response('200 OK', [('Content-Type','text/html')])
                output = '<img alt="{}" title="{}" src="{}" width="{}" height="{}" />'.format(
                    pic_fname_safe, pic_name_safe, pic_relweb_safe,pic_width, pic_height
                )
                return [output.encode('utf-8')]

            else:
                # make the web page
                #print('Content-type: text/html; charset=utf-8\n') 
                #print '<!-- path     : %s -->' % os.path.abspath(os.curdir)
                #print '<!-- argv[0]  : %s -->' % os.path.dirname(sys.argv[0])
                presenter = Presenter(album, pic, control, start_response)
                return [presenter.content]
        except:
            print('''
                <pre><h1>pix broke, you get to keep both pieces</h1>
                Traceback has been logged.</pre>
            ''',file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        return []
        
    def _getArg(self, aForm, aKey):
        if aKey in aForm: 
            #print '<!-- %s: %s -->' % (aKey, aForm[aKey].value)
            return unquote_plus(aForm[aKey].value) 
        return ''
    
    # setup known mimetypes for serving static files
    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })
