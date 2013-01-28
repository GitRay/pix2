## Copyright (C) 2013 Ray Cathcart (Pix2)
## Copyright (C) 2005, 2006 Karl Chen (QuickyPix)
## Copyright (C) 2005 Hollis Blanchard (QuickyPix)
## Copyright (C) 2005 Demian Neidetcher (Pix)

## This file is part of Pix2.

## Pix2 is free software; you can redistribute it and/or modify it under
## the terms of the GNU General Public License as published by the Free
## Software Foundation; either version 2, or (at your option) any later
## version.

## Pix2 is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.

## You should have received a copy of the GNU General Public License along
## with Pix2; see the file COPYING.  If not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
## USA.

import os
import urllib
from Album import Album
from Pic   import Pic
import Setup

class Presenter: 
  def __init__(self, subAlbum, picName, control):
    templateLines = open(os.path.join(Setup.pathToTemplate,'template.html'))

    currDir = os.path.join(Setup.albumLoc,subAlbum)
    album = Album(currDir)
    if (control == ''):
      if (picName != ''):
        pic = Pic(os.path.join(currDir,picName))
      else:
        pic = Pic('')
    else:
      if (control == 'first'):
      	pic = Pic(os.path.join(currDir,album.getFirstPic()))
      if (control == 'previous'):
      	pic = Pic(os.path.join(currDir,album.getPreviousPic(picName)))
      if (control == 'next'):
      	pic = Pic(os.path.join(currDir,album.getNextPic(picName)))
      if (control == 'last'):
      	pic = Pic(os.path.join(currDir,album.getLastPic()))

    self.printMetaData(currDir, pic, control)

    line = ''.join(templateLines)
    line = line.replace('@path@',       Setup.webPathToTemplate)
    line = line.replace('@breadcrumb@', self.formatBreadCrumb(album, pic )) 
    line = line.replace('@title@',      self.formatTitle(     album, pic ))
    line = line.replace('@albums@',     self.formatAlbums(    album      ))
    line = line.replace('@pics@',       self.formatPics(      album, pic ))
    line = line.replace('@meta@',       self.formatMeta(      album      ))
    line = line.replace('@control@',    self.formatControl(   album, pic ))
    line = self.formatContent(line, album, currDir, pic)
    print line,


  def printMetaData(self, currDir, pic, control):
    print '<!--'
    print 'subAlbum : %s' % currDir
    print 'pic      : %s' % pic
    print 'control  : %s' % control
    print 'pix ver  : %s' % Setup.pixVersion
    print '-->'


  def formatBreadCrumb(self, album, pic):
    outLines = []
    outLines = outLines + album.getBreadCrumb()
    outLines.reverse()
    if pic.isPic:
      [head, tail] = os.path.split(pic.picPath)
      outLines.append(tail)
    if len(outLines) > 0:
      outLines[0] = ' ' + Setup.seperator + ' ' + outLines[0]
    return (' ' + Setup.seperator + ' ').join(outLines) 


  def formatTitle(self, album, pic):

    albumSep = ' %s ' % (Setup.seperator)
    if (album.getName() == ''):
      albumSep = ''

    picSep = ' %s ' % (Setup.seperator)
    if (pic.getName() == ''):
      picSep = ''

    return "%s%s%s%s" % (albumSep, album.getName(), picSep, pic)


  def formatAlbums(self, album):
    albums = album.getAlbums() 

    if len(albums) == 0:
      return ''

    outLines = ['<h2>%s albums</h2>' % (len(albums))]
    for album in albums:
      outLines.append('<a href="?album=%s">%s</a><br>' % (
        urllib.quote_plus(album.getLinkPath()), 
        album.getName()))
    return '\n'.join(outLines)


  def formatPics(self, album, pic):
    if album.getNumPics() == 0:
      return ''

    pics     = album.getPics()
    outLines = ['<h2>%s pictures </h2>' % (len(pics))]

    for currPic in pics:
      if not currPic.isPic:
        continue
      selected = ''
      [pic_fname_safe, pic_relpic_safe, pic_name_safe, pic_relweb_safe, pic_width, pic_height] = \
        currPic.getResizedLink('thumb')
      if (currPic.getName() == pic.getName()):
        selected = 'id="selected-pic"'

      #[thumb_name,width,height] = currPic.getThumb()
      #if thumb_name != '':
      outLines.append( \
        '<a href="?album=%s&pic=%s"><img class="thumb" %s alt="%s" title="%s" src="%s" width="%s" height="%s"/></a>' \
        % ( \
          urllib.quote_plus(album.getLinkPath()), \
          pic_fname_safe, \
          selected, \
          pic_name_safe, \
          pic_name_safe, \
          pic_relweb_safe, \
          pic_width, \
          pic_height \
        ) \
      ) 

    return '\n'.join(outLines)


  def formatMeta(self, album):
    try:
      metaFileName = '%s%s%s.meta' % (Setup.albumLoc, album.getLinkPath(), os.sep)
      metaFile = open(metaFileName)
    except:
      return ''
    return '<a target="_new" href="%s%s%s.meta">m</a> %s ' % (Setup.albumLoc, album.getLinkPath(), os.sep, Setup.seperator) 


  def formatControl(self, album, pic):
    if (len(album.getPics()) < 4):
      return ''

    control   = '&nbsp; <a href="?album=%s&pic=%s&control=%s">%s</a> &nbsp; '
    albumPath = album.getLinkPath()
    picFile   = pic.getFileName()

    firstLink    = control % (albumPath, picFile, 'first',    '|<')
    previousLink = control % (albumPath, picFile, 'previous', '<<')
    nextLink     = control % (albumPath, picFile, 'next',     '>>')
    lastLink     = control % (albumPath, picFile, 'last',     '>|')

    return '%s %s %s %s' % (firstLink, previousLink, nextLink, lastLink) 


  def formatContent(self, line, album, currDir,  pic):
    albumDescription = album.getDescription().strip()

    # TODO: this can be done better
    if pic.getOriginal() != '':
      line = line.replace('@album-description@', '')
      line = line.replace('@web-pic@',           self.formatWebPic(pic))
      line = line.replace('@comment@',           pic.getComment())

    elif albumDescription != '': 
      line = line.replace('@album-description@', albumDescription)
      line = line.replace('@web-pic@',           '')
      line = line.replace('@comment@',           '')

    else:
      if album.getNumPics() > 0:
        firstPic = album.getPics()[0].getFileName()
        pic = Pic('%s%s%s' % (currDir, os.sep, firstPic))
      else:
        pic = Pic('')

      line = line.replace('@album-description@', '')
      line = line.replace('@web-pic@', self.formatWebPic(pic))
      line = line.replace('@comment@', pic.getComment())

    return line


  def formatWebPic(self, pic):
    if not pic.isPic:
      return ''
    [pic_fname_safe, pic_relpic_safe, pic_name_safe, pic_relweb_safe, pic_width, pic_height] = \
      pic.getResizedLink('web')
    
    #return '<img align="right" src="%s" width="%s" height="%s" />' % (pic_relweb_safe, pic_width, pic_height)
    return '<a href="%s"><img class="picture" alt="%s" title="%s" src="%s" width="%s" height="%s" /></a>' % ( \
      Setup.webPathToCGI + '/index.cgi?pict_path=' + pic_relpic_safe + '&download=jpeg', \
      'click here to download the original image', \
      'click here to download the original image', \
      pic_relweb_safe, \
      pic_width, \
      pic_height \
    )