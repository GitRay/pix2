#!/usr/bin/python

import sys, os, string, urllib

from Pic import Pic
import Setup

class Album:

  def __init__(self, albumDir, recurse = 1):
    self.albumDir = albumDir
    
    self.albums = []
    self.pics   = []
    
    if not recurse:
      return

    for entry in sorted(os.listdir(albumDir),reverse=True):
      if (entry[0] != '.'):
        # skip files that start with a dot
        #pathAndEntry = '%s%s%s' % (albumDir, os.sep, entry)
        pathAndEntry = os.path.join(albumDir,entry)
        if os.path.isdir(pathAndEntry):
          self.albums.append(Album(pathAndEntry, False))
        elif os.path.isfile(pathAndEntry):
          # for performance, try to load pickled version
          try:
            self.pics.append(Pic.loadPickledVersion(pathAndEntry))
          except IOError:
            # load from scratch
            try:
              self.pics.append(Pic(pathAndEntry))
            except: 
              print '<!-- not a picture: %s -->' % (pathAndEntry)


  def getAlbums(self):
    return self.albums


  def getNumPics(self):
    return len(self.pics)


  def getFirstPic(self):
    return self.getPics()[0].getFileName()


  def getLastPic(self):
    return self.getPics()[-1].getFileName()


  def getPreviousPic(self, picName):
    return self.getPics()[self.findIndex(picName) - 1].getFileName()


  def getNextPic(self, picName):
    if (picName == ''):
      nextIndex = 0
    else:
      nextIndex = self.findIndex(picName) + 1
      if (nextIndex >= len(self.getPics())):
        nextIndex = 0

    return self.getPics()[nextIndex].getFileName()

  
  def findIndex(self, picName):
    currNum = 0
    for pic in self.getPics():
      if (picName == pic.getFileName()):
        return currNum
      currNum = currNum + 1
    return 0


  def getPics(self):
    process_meta = True
    try:
      metaFile = open('%s%s.meta' % (self.albumDir, os.sep))
    except IOError:
      process_meta = False

    displayPics = []
    copyOfPics = self.pics[:]
    if process_meta:
      displayPics = []
      for metaLine in metaFile:
        if string.find(metaLine, '=') != -1:
          splitMetaLine = string.split(metaLine, '=')
          currMetaImage = string.strip(splitMetaLine[0])
          for currPic in copyOfPics:
            if (currMetaImage == currPic.getFileName()):
              displayPics.append(currPic)
              copyOfPics.remove( currPic)

    # we got the ordered ones, now get the rest
    displayPics.extend(copyOfPics)
    
    # rifle through pics and eliminate any that don't exist
    pics_to_return = []
    for this_pic in displayPics:
      if this_pic.isPic:
        pics_to_return.append(this_pic)
    pics_to_return.sort()
    
    return pics_to_return


  def getName(self):
    [head,tail] = os.path.split(self.albumDir)
    return tail


  def getLinkPath(self):
    #path should be relative to pics directory
    path = os.path.relpath(self.albumDir, Setup.albumLoc)
    # make it safe for url
    path = urllib.quote_plus(path)
    return path


  def getBreadCrumb(self):
    linkPath = self.getLinkPath()
    breadCrumb   = []
    runningCrumb = ''

    while linkPath != '' and linkPath != '.':
      [head,tail] = os.path.split(linkPath)
      runningCrumb = head
      breadCrumb.append( '<a href="?album=%s">%s</a>' % ( \
        urllib.quote_plus(linkPath), \
        tail \
      ))
      linkPath = head


    return breadCrumb
  
  def getDescription(self):
    try:
      metaFile = open('%s%s.meta' % (self.albumDir, os.sep))
    except:
      return ''

    description = [] 
    startReading = 0
    for metaLine in metaFile:
      if string.find(metaLine, '<album description>') == 0:
        startReading = 1
      elif string.find(metaLine, '</album description>') == 0:
        startReading = 0 

      if startReading:
        description.append(metaLine)
    return string.join(description[1:])
