# $Id: Pic.py 113 2005-09-27 23:28:33Z quarl $

import os
import glob
import util
import config
import image_util

# TODO: cache the multiple os.stat calls

def findPic(path):
    if os.path.isfile(config.ALBUMS_DIR+path):
        return Pic(path)

    # careful to only match filename.ext where ext is in MEDIA_TYPES
    # -- don't match filename.ext.* or filename.*.ext
    #
    # Note: if we ever use non-3-character extensions, this code will have to
    # rewritten.
    pics = glob.glob(config.ALBUMS_DIR + path + '.???')
    if len(pics) == 1:
        return Pic(path + pics[0][-4:])

    return None


class Pic(object):
    def __init__(self, path):
        # path should start with / and be relative to config.ALBUMS_DIR
        assert(path.startswith('/'))
        self.path = util.path_nonext(path)
        self.pathext = util.path_ext(path)

        if not os.path.exists(config.ALBUMS_DIR+path):
            raise ValueError("Nonexistent Pic '%s'"%self.path)
        if not util.is_media(path):
            util.error_forbidden()

    def __eq__(self, otherpic):
        return otherpic and self.fullpath == otherpic.fullpath

    def _get_rel_path(self):
        return os.path.basename(self.path)
    def _set_rel_path(self, p):
        util.name_validate(p)
        if self.rel_path != p:
            old_name = self.path + '.' + self.pathext
            new_name = p + '.' + self.pathext
            util.log("Renaming %s to %s" %(repr(old_name), repr(new_name)))
            os.rename(config.ALBUMS_DIR+old_name,
                      config.ALBUMS_DIR+os.path.join(os.path.dirname(self.path), new_name))
            util.redirect_rel(p)
    rel_path = property(_get_rel_path, _set_rel_path)
    title = property(_get_rel_path)
    breadcrumb = property(_get_rel_path)

    def _get_fullpath(self):
        return '%s.%s' %(self.path, self.pathext)
    fullpath = property(_get_fullpath)

    # def _get_rel_fullpath(self):
    #     return os.path.basename('%s.%s' %(self.path, self.pathext))
    # rel_full_path = property(_get_rel_full_path)


    def _recent(self):
        return util.recent(util.xstat(config.ALBUMS_DIR+self.path))

    def img_rel_path(self, size):
        u = "%s/%s" %(self.rel_path, util.sized(size))
        if self._recent():
            # force browser to retrieve latest, since this was recently
            # modified
            u += '?'
        return u

    def img_path(self, size):
        return "%s/%s" %(self.path, util.sized(size))

    def is_image(self):
        return (self.pathext in config.IMAGE_TYPES)

    def is_movie(self):
        return (self.pathext in config.MOVIE_TYPES)

    # send jpg data to user
    def show(self, size):
        if size == (-1,-1):
            util.cat(config.ALBUMS_DIR+self.fullpath,1)
            raise SystemExit

        fpath = config.ALBUMS_DIR + self.fullpath
        if self.is_image():
            self.show_image(fpath, self.fullpath[1:], size)
        elif self.is_movie():
            # get first frame of movie
            image_rpath = "%s.jpg" %(self.fullpath[1:])
            image_fpath = os.path.join(config.CACHE_DIR, image_rpath)
            image_util.convert_to_image(fpath, image_fpath)
            self.show_image(image_fpath, image_rpath, size, True)
        else:
            raise Exception("Invalid file type")
    def show_image(self, fpath, rpath, size, movie=False):
        # Note: the resized path should keep the same extension
        resized_fpath = os.path.join(
            config.CACHE_DIR, "%s/%s,%s" %(os.path.dirname(rpath),
                                            util.sized(size),
                                            os.path.basename(rpath)))
        util.cat(image_util.resize_image(fpath, resized_fpath, size, movie))
        raise SystemExit

    comment = util.metadata_property('.comment')

    def _get_info(self):
        ret = []
        try:
            info = image_util.image_info(config.ALBUMS_DIR+self.fullpath)
        except Exception, e:
            return '<!-- Pic._get_info exception: %s -->'%e
        if info.time_str:
            ret.append('<tr><td>Picture taken:</td><td>%s</td></tr>' %info.time_str)
        if info.dimensions:
            ret.append('<tr><td>Dimensions:</td><td>%dx%d</td></tr>' %info.dimensions)
        if info.original_dimensions and not image_util.dimensions_equal(info.dimensions, info.original_dimensions):
            ret.append('<tr><td>Original Dimensions:</td><td>%dx%d</td></tr>' %info.original_dimensions)
        # if info.frame_rate:
        #     ret.append('<tr><td>Frame Rate:</td><td>%s</td></tr>' %info.frame_rate)
        if info.duration:
            ret.append('<tr><td>Duration:</td><td>%.1f sec</td></tr>' %info.duration)
        if info.video_codec:
            ret.append('<tr><td>Video codec:</td><td>%s</td></tr>' %info.video_codec)
        if info.file_size:
            ret.append('<tr><td>File size:</td><td>%s bytes</td></tr>' %
                       util.commify(info.file_size))

        if ret:
            ret = ['<table class="info">']+ret+['</table>']
            return '\n'.join(ret)
        else:
            return ''
    info = property(_get_info)

    def tdel(self):
        util.log("TDeleting %s" %(repr(self.fullpath)))
        util.tdel(config.ALBUMS_DIR+self.fullpath)

    def rotate(self, degrees):
        util.log("Rotating %d: %s" %(degrees, repr(self.fullpath)))
        image_util.rotate_image(config.ALBUMS_DIR+self.fullpath, degrees)
