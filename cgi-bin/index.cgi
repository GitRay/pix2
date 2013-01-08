#!/usr/bin/python

import cgi 
import os
import sys
import string
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
      	pic = Pic(os.path.join(currDir,album.getPreviousPic(picnName)))
      if (control == 'next'):
      	pic = Pic(os.path.join(currDir,album.getNextPic(picName)))
      if (control == 'last'):
      	pic = Pic(os.path.join(currDir,album.getLastPic()))

    self.printMetaData(currDir, pic, control)

    line = string.join(templateLines, '')
    line = string.replace(line, '@path@',       os.path.relpath(Setup.pathToTemplate,Setup.pathToCGI)+os.path.sep )
    line = string.replace(line, '@breadcrumb@', self.formatBreadCrumb(album, pic )) 
    line = string.replace(line, '@title@',      self.formatTitle(     album, pic ))
    line = string.replace(line, '@albums@',     self.formatAlbums(    album      ))
    line = string.replace(line, '@pics@',       self.formatPics(      album, pic ))
    line = string.replace(line, '@meta@',       self.formatMeta(      album      ))
    line = string.replace(line, '@control@',    self.formatControl(   album, pic ))
    line = self.formatContent(line, album, currDir, pic)
    print line,


  def printMetaData(self, currDir, pic, control):
    print '<!--'
    print 'path     : %s' % os.path.abspath(os.curdir)
    print 'albumLoc : %s' % Setup.albumLoc
    print 'subAlbum : %s' % currDir
    print 'pic      : %s' % pic
    print 'control  : %s' % control
    print 'pix ver  : %s' % Setup.pixVersion
    print '-->'


  def formatBreadCrumb(self, album, pic):
    outLines = []
    outLines = outLines + album.getBreadCrumb()
    outLines.reverse()
    if (pic.getName() != ''):
      [head, tail] = os.path.split(pic.picPath)
      outLines.append(tail)
    if len(outLines) > 0:
      outLines[0] = ' | ' + outLines[0]
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
    return string.join(outLines, '\n')


  def formatPics(self, album, pic):
    if album.getNumPics() == 0:
      return ''

    pics     = album.getPics()
    outLines = ['<h2>%s pictures </h2>' % (len(pics))]

    for currPic in pics:
      selected = ''
      if (currPic.getName() == pic.getName()):
        selected = 'id="selected-pic"'

      outLines.append('<a href="?album=%s&pic=%s"><img %s alt="%s" title="%s" src="%s"/></a>' % ( \
        urllib.quote_plus(album.getLinkPath()), \
        urllib.quote_plus(currPic.getFileName()), \
        selected, \
        currPic.getName(), \
        currPic.getName(), \
        urllib.quote(os.path.relpath(currPic.getThumb(),Setup.pathToCGI)) \
      )) 
    return string.join(outLines, '\n')


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
    albumDescription = string.strip(album.getDescription())

    # TODO: this can be done better
    if pic.getOriginal() != '':
      line = string.replace(line, '@album-description@', '')
      line = string.replace(line, '@web-pic@',           self.formatWebPic(pic))
      line = string.replace(line, '@comment@',           pic.getComment())

    elif albumDescription != '': 
      line = string.replace(line, '@album-description@', albumDescription)
      line = string.replace(line, '@web-pic@',           '')
      line = string.replace(line, '@comment@',           '')

    else:
      if album.getNumPics() > 0:
        firstPic = album.getPics()[0].getFileName()
        pic = Pic('%s%s%s' % (currDir, os.sep, firstPic))
      else:
        pic = Pic('')

      line = string.replace(line, '@album-description@', '')
      line = string.replace(line, '@web-pic@', self.formatWebPic(pic))
      line = string.replace(line, '@comment@', pic.getComment())

    return line


  def formatWebPic(self, pic):
    if pic.getOriginal() == '':
      return ''

    # use this return so that the users can click on the web-sized image and
    # then see the original image.  of course sometimes the originals are huge
    # so using the alternate return will keep your bandwidth usage down.
    # return '<a href="%s"><img align="right" alt="%s" title="%s" src="%s"/></a>' % (
    #     pic.getOriginal(), 
    #     'click here to view the original image',
    #     'click here to view the original image',
    #     pic.getWeb())

    return '<img align="right" src="%s"/>' % urllib.quote(os.path.relpath(pic.getWeb(),Setup.pathToCGI))


def getArg(aForm, aKey):
  if aForm.has_key(aKey): 
    print '<!-- %s: %s -->' % (aKey, aForm[aKey].value)
    return aForm[aKey].value 
  return ''


def doAdminFunction(action, album, pic):
  # TODO: 
  # presumablye in the future if there were any other admin functions
  # besides clean there would be some if statements here
  print '<pre>'
  print 'cleaning cache recursively from %s%s' % (Setup.albumLoc, album)

  albumToClean = '%s%s' % (Setup.albumLoc, album)
  for root, dirs, files in os.walk(albumToClean):
    for file in files:
      if string.find(file, '.web_') == 0 or string.find(file, '.thumb_') == 0:
        pathAndEntry = '%s%s%s' % (root, os.sep, file)
        os.remove(pathAndEntry)
        print 'deleted <i>%s</i>' % (pathAndEntry)
  print '</pre>'


if __name__=='__main__': 

  sys.stderr == sys.stdout 
  print 'Content-type:text/html\n' 
  print '<?-- path     : %s -->' % os.path.abspath(os.curdir)
  print '<?-- argv[0]  : %s -->' % os.path.dirname(sys.argv[0])
  try:
    iForm       = cgi.FieldStorage() 
    album       = getArg(iForm, 'album')
    pic         = getArg(iForm, 'pic')
    control     = getArg(iForm, 'control')
    adminAction = getArg(iForm, 'admin')
    if (adminAction != ''):
      doAdminFunction(adminAction, album, pic)
    else:
      Presenter(album, pic, control)
  except Exception, exceptionData:
    print '''
      <pre><h1>pix broke, you get to keep both pieces</h1>%s</pre>
    ''' % exceptionData
