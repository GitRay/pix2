#!/usr/bin/python2.3

# $Id: quickypix.py 164 2005-10-15 08:34:36Z quarl $

import cgi
import cgitb; cgitb.enable()
import os
import sys
import re
from Album import Album
from Pic   import Pic, findPic
import config
import util
import Cookie

# TODO: javascript to confirm exit without commit

# TODO: run non-authenticated mode read-only some how (different user maybe)

def canonicalize_path(url):
    if config.input_path != url:
        print "Status: 301 Moved Permanently"
        print 'Location: %s' %config.root + url
        print
        raise SystemExit

def tobool(s):
    try:
        return s and bool(int(s))
    except:
        return False

def cls_recent(obj):
    if obj.recent:
        return ' class="recently-modified"'
    else:
        return ''

class Presenter:
    def __init__(self, environ):
        config.input_path = input_path = environ.get('PATH_INFO') or '/'
        # see config.py for setting of config.root, which is by default
        # $SCRIPT_NAME
        config.request_uri = environ.get('REQUEST_URI')
        config.authenticated = False
        config.editing = False
        self.remote_user = environ.get('REMOTE_USER')
        self.form = cgi.FieldStorage()
        config.cookie = Cookie.SimpleCookie()
        config.cookie.load(environ.get('HTTP_COOKIE',''))
        new_cookie = Cookie.SimpleCookie()
        if self.remote_user:
            config.authenticated = True
            config.editing = (('editing' in config.cookie or
                               bool(self.form.getfirst('edit'))) and
                              not self.form.getfirst('commit')=='Exit')
            if config.editing:
                new_cookie['editing'] = '1'
                new_cookie['editing']['path'] = '/'
            else:
                new_cookie['editing'] = ''
                new_cookie['editing']['path'] = '/'
                new_cookie['editing']['expires'] = -86400*14

        if config.editing:
            config.admin = True
        else:
            # does user want the "login" button? (this only redirects to the
            # secure page, which does authentication)
            str_admin = self.form.getfirst('admin')
            if str_admin:
                config.admin = tobool(str_admin)
            else:
                config.admin = 'admin' in config.cookie

            if config.admin:
                new_cookie['admin'] = '1'
                new_cookie['admin']['path'] = os.path.join('/',config.root)
                new_cookie['admin']['expires'] = 86400*14
            elif str_admin:
                # user specified '?admin=0' => logout
                new_cookie['admin'] = ''
                new_cookie['admin']['path'] = os.path.join('/',config.root)
                new_cookie['admin']['expires'] = -86400*14
        if new_cookie:
            print new_cookie

        if config.request_uri.endswith('?'):
            print 'Cache-Control: max-age=5'

        # ?dl=1 adds the content-disposition header
        config.download_flag = bool(self.form.getfirst('dl'))

        if input_path == '/style.css':
            util.cat(config.STYLE_FILE)
            raise SystemExit
        if not input_path.startswith('/'):
            raise SystemExit
        input_path = input_path[1:].split('/')
        if '..' in input_path:
            util.error_forbidden()
        if '' in input_path:
            input_path.remove('')

        if not os.path.isdir(config.ALBUMS_DIR):
            raise "Configuration error: %s is not a directory"%config.ALBUMS_DIR

        path = '/'
        self.album_path = [Album('/')]
        self.pic = None
        while input_path:
            part = input_path.pop(0)
            util.name_validate(part)
            ppath = path
            path = os.path.join(ppath, part)
            if os.path.isdir(config.ALBUMS_DIR+path):
                self.album_path.append(Album(path))
                continue

            ext = util.path_ext(part)
            if not input_path and ext:
                # If we have "IMAGE.jpg" (as the last component), treat it the
                # same as "IMAGE/fullsize"
                path = os.path.join(ppath, util.path_nonext(part))
            else:
                ext = ''
            self.pic = findPic(path)
            if self.pic:
                if ext:
                    if self.pic.pathext != ext:
                        util.not_found()
                    assert(not input_path)
                    input_path = [util.FULLSIZE]
                break

            util.not_found()

        self.album = self.album_path[-1]
        self.pic_path = self.album_path[:]
        if self.pic:
            self.pic_path.append(self.pic)

        # if user specified /path/pic.jpg/123x234 then return a (resized) jpg
        if input_path:
            assert (self.pic)
            if len(input_path) > 1: util.not_found()
            requested_size = util.parse_size(input_path[0])
            canonicalize_path(self.pic.img_path(requested_size))
            self.pic.show(requested_size)

        if config.authenticated:
            config.commit_redirect_rel = None
            config.pending_redirect = None
            if 'commit' in self.form:
                self.commit()
            elif 'commit.redirect' in self.form:
                config.commit_redirect_rel = self.form.getfirst('commit.redirect')
                config.pending_redirect = util.relative_url(
                    config.commit_redirect_rel)
                self.commit()
            if config.pending_redirect:
                util.redirect(config.pending_redirect)

        canonicalize_path(self.pic_path[-1].path)

        self.present()

    def present(self):
        print 'Content-type:text/html\n'

        data = open(config.TEMPLATES_FILE).read()

        data = re.compile('<!-- --\\s.*?\\s-- -->\\s*', re.DOTALL).\
            sub('', data)
        data = data.replace('@root@', config.root)
        data = data.replace('@bodyclass@', self.formatBodyClass())
        data = data.replace('@login@', self.formatLogin())
        data = data.replace('@endlogin@', self.formatEndLogin())
        data = data.replace('@breadcrumb@',  self.formatBreadCrumb())
        data = data.replace('@title@',       self.formatTitle())
        data = data.replace('@comment@',     self.formatComment())
        data = data.replace('@albums@',      self.formatAlbums())
        data = data.replace('@pics@',        self.formatPicsThumb())
        if self.pic:
            data = data.replace('@pic@',         self.formatPic())
            data = data.replace('@pic-comment@', self.formatPicComment())
            data = data.replace('@pic-info@',    self.formatPicInfo())
            data = data.replace('@pic-dl@',      self.formatPicDl())
        else:
            data = re.compile('<!-- @BEGINPIC@ -->.*?<!-- @ENDPIC@ -->',
                              re.DOTALL).\
                              sub('', data)
        print data,

    def formatBreadCrumb(self):
        return ' &raquo; '.join([obj.breadcrumb for obj in self.pic_path])

    def formatTitle(self):
        return ' | '.join([obj.title for obj in self.pic_path])

    def formatAlbums(self):
        albums = self.album.albums

        if len(albums) == 0:
            return ''

        ret = []
        ret.append('<h2>Albums (%d)</h2>'%len(albums))

        # top level album has reversed order
        if self.album.path == '/':
            albums.reverse()

        for album in albums:
            highlight = album.highlight
            if highlight:
                if isinstance(highlight,Pic):
                    href = os.path.join(album.rel_path, highlight.rel_path)
                else:
                    # "highlight" is really an album
                    href = os.path.join(album.rel_path, '')
                img_url = [album.rel_path]
                while not isinstance(highlight,Pic):
                    img_url.append(highlight.rel_path)
                    highlight = highlight.highlight
                img_url.append(highlight.img_rel_path(config.ALBUM_THUMB_SIZE))
                img_url = os.path.join(*img_url)
                ret.append(''.join(
                        [
                            '<dl>',
                            '<dt><a href="%s" title="%s">' %(
                                href,
                                album.title),
                            '<img alt="%s" src="%s" />' %(
                                highlight.title,
                                img_url
                                ),
                            '</a></dt>',
                            '<dd>%s</dd>' %(album.title),
                            '</dl>'
                         ]))
            else:
                # TODO: use a dummy thumbpic
                ret.append(''.join(
                        [
                            '<a href="%s" title="%s">%s</a>' %(
                                os.path.join(album.rel_path,''),
                                album.title,
                                album.title)
                            ]))

        return '\n'.join(ret)

    def image_link(self, target_url, img_src, img_alt,
                   selected=False, img_title=None ):
        if selected:
            imgid = ' id="selected-pic"'
        else:
            imgid = ''
        if config.editing:
            return ('<input%s type="image" src="%s" '
                    'name="commit.redirect" value="%s" title="%s"/>' %(
                    imgid,
                    img_src,
                    target_url,
                    "Save and view %s" %(target_url)))
        else:
            if img_title:
                title = ' title="%s"'%img_title
            else:
                title = ''
            return '<a href="%s"><img%s src="%s" alt="%s"%s /></a>' %(
                target_url, imgid, img_src, img_alt%target_url, title)


    def formatPicsThumb(self):
        pics = self.album.pics

        if len(pics) == 0:
            return ''

        ret = ['<h2>Pictures (%d)</h2>\n' %len(pics) ]

        for pic in pics:
            ret.append('<dl>')
            if config.editing:
                ret.append('<table><tr><td style="">')

            ret.append('<dt>')
            ret.append(
                self.image_link(target_url = pic.rel_path,
                                img_src    = pic.img_rel_path(config.THUMB_SIZE),
                                img_alt    = "thumbnail for %s",
                                img_title  = util.escHtml(pic.comment),
                                selected   = (pic == self.pic)))
            ret.append('</dt>')
            if config.editing:
                ret.append('<dd>')
                ret.append('<textarea%s rows="1" cols="7" name="%s.comment">'%
                           (cls_recent(pic.comment), pic.rel_path))
                ret.append(util.escHtml(pic.comment))
                ret.append('</textarea>')
                ret.append('</dd>')

                ret.append('</td><td>')
                ret.append('<label>del')
                ret.append('<input type="checkbox" name="rm" value="%s" />'%
                           pic.rel_path)
                ret.append('</label>')

                ret.append('<label>r90')
                ret.append('<input type="checkbox" name="rot90" value="%s" />'%
                           pic.rel_path)
                ret.append('</label>')

                ret.append('<label>r270')
                ret.append('<input type="checkbox" name="rot270" value="%s" />'%
                           pic.rel_path)
                ret.append('</label>')

                ret.append('</td></tr>')
                ret.append('</table>')

            ret.append('</dl>')
            ret.append('\n')

        return ''.join(ret)

    def formatPic(self):
        ret = []
        if config.authenticated and not config.editing:
            ret.append(self.formatEditButtons())

        ret.append(
            self.image_link(target_url = self.pic.img_rel_path((-1,-1)),
                            img_src    = self.pic.img_rel_path(config.WEB_SIZE),
                            img_alt    = "picture - %s",
                            img_title  = "View full size %s"%self.pic.rel_path))
        return ''.join(ret)

    def formatEditButtons(self):
        ret = []
        ret.append('<div id="edit-buttons">')

        ret.append('<form method="post">')
        ret.append('<input type="hidden" name="rm" value="%s" />'%
                   self.pic.rel_path)
        ret.append('<input type="submit" name="commit" value="Delete" />')
        ret.append('</form>')

        ret.append('<form method="post">')
        ret.append('<input type="hidden" name="rot90" value="%s" />'%
                   self.pic.rel_path)
        ret.append('<input type="submit" name="commit" value="Rotate 90" />')
        ret.append('</form>')

        ret.append('<form method="post">')
        ret.append('<input type="hidden" name="rot270" value="%s" />'%
                   self.pic.rel_path)
        ret.append('<input type="submit" name="commit" value="Rotate 270" />')
        ret.append('</form>')

        ret.append('<form method="post">')
        ret.append('<input type="hidden" name="highlight" value="%s" />'%
                   self.pic.rel_path)
        ret.append('<input type="submit" name="commit" value="Highlight" />')
        ret.append('</form>')

        ret.append('</div>')

        ret.append('\n')
        return ''.join(ret)


    def formatPicComment(self):
        if config.editing:
            ret = []
            ret.append('<label id="pic-filename">Filename:')
            ret.append('<input type="text" name="filename" value="%s" />'%
                       self.pic.rel_path)
            ret.append('</label>')
            ret.append('<label id="pic-comment">Comment:'
                       '<textarea%s rows="3" cols="40" name="%s.comment">'%
                       (cls_recent(self.pic.comment),self.pic.rel_path))
            ret.append(util.escHtml(self.pic.comment))
            ret.append('</textarea>'
                       '</label>')

            ret.append('<input id="pic-commit" type="submit" name="commit" value="Save" />')

            ret.append('<label>Delete')
            ret.append('<input type="checkbox" name="rm" value="%s" />'%
                       self.pic.rel_path)
            ret.append('</label>')

            ret.append('<label>Rotate 90')
            ret.append('<input type="checkbox" name="rot90" value="%s" />'%
                       self.pic.rel_path)
            ret.append('</label>')

            ret.append('<label>Rotate 270')
            ret.append('<input type="checkbox" name="rot270" value="%s" />'%
                       self.pic.rel_path)
            ret.append('</label>')

            ret.append('<label>Highlight')
            ret.append('<input type="checkbox" name="highlight" value="%s" />'%
                       self.pic.rel_path)
            ret.append('</label>')

            return ''.join(ret)
        else:
            return util.str2paragraphs(util.escHtml(self.pic.comment))

    def formatPicInfo(self):
        return self.pic.info

    def formatPicDl(self):
        # if admin mode is on, then show a [dl] link.
        if config.admin:
            url = self.pic.img_rel_path((-1,-1)) + '?dl=1'
            return '<a href="%s">[dl]</a>'%url
        else:
            return ''

    def formatComment(self):
        if config.editing:
            ret = []
            ret.append('<label id="album-comment">Album comment:'
                       '<textarea%s rows="3" cols="60" name=".comment">'
                       %(cls_recent(self.album.comment)))
            ret.append(util.escHtml(self.album.comment))
            ret.append('</textarea>'
                       '</label>')
            ret.append('<label id="album-title">Album title:')
            ret.append('<input type="text" name=".title" value="%s" />'%
                       util.escHtml(self.album.title))
            ret.append('</label>')
            ret.append('<br />')
            return ''.join(ret)
        else:
            return util.str2paragraphs(util.escHtml(self.album.comment))

    def formatLogin(self):
        if not config.authenticated:
            if config.admin:
                ret = []
                ret.append('<div class="login">')
                ret.append('<a href="%s%s">Login/Edit</a>'%(
                            config.EDIT_ROOT,config.input_path))
                ret.append(' | <a href="%s?admin=0">Hide</a>' %
                           config.input_path)
                ret.append('</div>')
                return ''.join(ret)
            else:
                return ''
        ret = []
        # if config.editing:
        ret.append('<form method="POST">')
        # else:
        #     ret.append('<form method="GET">')
        ret.append('<div class="login">')
        if config.editing:
            ret.append('<input type="submit" name="commit" value="Exit" />')
            ret.append('<input type="submit" name="commit" value="Save" />')
        else:
            ret.append('<input type="submit" name="edit" value="Edit" />')
        ret.append('Logged in as <span>%s</span>.'%self.remote_user)
        ret.append(' <a href="%s%s">Exit</a>'%(
                   config.PUBLIC_ROOT,config.input_path))

        ret.append('</div>')
        return ''.join(ret)

    def formatEndLogin(self):
        if not config.editing:
            return ''
        return '</form>'

    def formatBodyClass(self):
        if config.editing:
            return 'editing'
        else:
            return ''

    def commit(self):
        print >>sys.stderr, "Commit form: %s"% repr(self.form),
        redirect = False
        title = self.form.getfirst('.title')
        if title:
            self.album.title = title
        comment = self.form.getfirst('.comment')
        if comment:
            self.album.comment = comment
        highlight_name = self.form.getfirst('highlight')
        if highlight_name:
            self.album.highlight_name = highlight_name

        for key in self.form.keys():
            if key.endswith('.comment'):
                rel_name = key[:-len(':comment')]
                if not rel_name: continue
                util.name_validate(rel_name)
                pic = findPic(self.album.path + rel_name)
                # there might be up to two place the user could modify a
                # picture comment
                for comment in self.form.getlist(key)[:2]:
                    if pic.comment != comment:
                        pic.comment = comment
                        break

        display_path = self.pic_path[-1].fullpath
        if config.commit_redirect_rel:
            display_path = self.album.path + config.commit_redirect_rel

        for rel_name in self.form.getlist('rm'):
            util.name_validate(rel_name)
            pic = findPic(self.album.path + rel_name)
            if pic.fullpath == display_path:
                config.pending_redirect = config.root+self.album.path
            pic.tdel()

        for rel_name in self.form.getlist('rot90'):
            util.name_validate(rel_name)
            pic = findPic(self.album.path + rel_name)
            pic.rotate(90)

        for rel_name in self.form.getlist('rot270'):
            util.name_validate(rel_name)
            pic = findPic(self.album.path + rel_name)
            pic.rotate(270)

        # this might rename and redirect
        filename = self.form.getfirst('filename')
        if self.pic and filename:
            self.pic.rel_path = filename

if __name__=='__main__':
    try:
        Presenter(os.environ)
    except util.AccessError, e:
        e.print_exit()

