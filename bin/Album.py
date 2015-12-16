from __future__ import print_function
#try:
#  from urllib import quote_plus
#except:
#  from urllib.parse import quote_plus
  
import sys, os, string, cgi

from Pic import Pic
import Setup

class Album:

  def __init__(self, albumDir, start_response, recurse = 1):
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
            self.pics.append(Pic.loadPickledVersion(start_response,pathAndEntry))
          except (IOError, EOFError):
            # load from scratch
            try:
              #remove faulty pickled version
              self.pics.append(Pic(start_response,pathAndEntry))
            except: 
              print('file in picture folder is not a picture: %s\n  reason: %s' % (pathAndEntry,sys.exc_info()[0]), file=sys.stderr)


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
        if not '=' in metaLine:
        #if string.find(metaLine, '=') != -1:
          #splitMetaLine = string.split(metaLine, '=')
          splitMetaLine = metaLine.split('=')
          #currMetaImage = string.strip(splitMetaLine[0])
          currMetaImage = splitMetaLine[0].strip()
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
    return cgi.escape(tail,True).encode('ascii','xmlcharrefreplace')


  def getLinkPathRaw(self):
    #path should be relative to pics directory
    path = os.path.relpath(self.albumDir, Setup.albumLoc)
    return path
        
  def getLinkPath(self):
    path = self.getLinkPathRaw()
    # make it safe for url
    path = Pic.makePathUrlFriendly(path,use_quote_plus=True)
    return path


  def getBreadCrumb(self):
    linkPath = self.getLinkPathRaw()
    breadCrumb   = []
    runningCrumb = ''

    while linkPath != '' and linkPath != '.':
      [head,tail] = os.path.split(linkPath)
      runningCrumb = head
      breadCrumb.append( '<a href="?album=%s">%s</a>' % ( \
        Pic.makePathUrlFriendly(linkPath), \
        cgi.escape(tail,True).encode('ascii','xmlcharrefreplace').decode('ascii') \
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
      #if string.find(metaLine, '<album description>') == 0:
      if metaLine.find('<album description>') == 0:
        startReading = 1
      #elif string.find(metaLine, '</album description>') == 0:
      elif metaLine.find('</album description>') == 0:
        startReading = 0 

      if startReading:
        description.append(metaLine)
    #return string.join(description[1:])
    return ''.join(description[1:])