# $Id: image_pil.py 244 2005-12-05 10:39:30Z quarl $

# Support for image operations using PIL.

## Copyright (C) 2005 Hollis Blanchard
## Copyright (C) 2005 Karl Chen

## This file is part of QuickyPix.

## QuickyPix is free software; you can redistribute it and/or modify it under
## the terms of the GNU General Public License as published by the Free
## Software Foundation; either version 2, or (at your option) any later
## version.

## QuickyPix is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.

## You should have received a copy of the GNU General Public License along
## with QuickyPix; see the file COPYING.  If not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
## USA.

from PIL import Image

def resize(fpath, resized_fpath, (new_width, new_height), movie):
    if movie:
        # not implemented yet for PIL
        import image_im
        return image_im.resize(fpath, resized_fpath, (new_width, new_height), movie)

    # TODO: add "movie" text with ImageDraw.text()
    originalImage = Image.open(fpath)
    newImage = originalImage.resize((new_width, new_height), Image.ANTIALIAS)
    # TODO: adaptively use the input image's JPEG quality, like ImageMagick
    # does.  otherwise at least use a configuration parameter.
    newImage.save(resized_fpath, quality=90)

def get_size(fpath):
    image = Image.open(fpath)
    return int(image.size[0]), int(image.size[1])

