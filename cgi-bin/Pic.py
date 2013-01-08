#!/usr/bin/python

import sys, os, string, subprocess

import Setup

if (Setup.USE_PIL):
  try:
    from PIL import Image
  except ImportError:
    print "get PIL at http://www.pythonware.com/products/pil"
    Setup.USE_PIL = False

class Pic:

  def __init__(self, aPicPath):
    # validate that it is a pic if it has a filename
    self.picPath = aPicPath

  def getComment(self):
    if self.getOriginal() == '':
      return ''

    pathAndName = self.getOriginal()
    #nameBegin = string.rfind(pathAndName, os.sep)
    #dir = pathAndName[:nameBegin]
    [dir, fileName] = os.path.split(pathAndName)

    try:
      metaFile = open('%s%s.meta' % (dir, os.sep))
    except:
      return ''

    #fileName = pathAndName[nameBegin + 1:]

    for metaLine in metaFile:
      if string.find(metaLine, '=') != -1:
        splitMetaLine = string.split(metaLine, '=')
        imageName = string.strip(splitMetaLine[0])
        if (imageName == fileName):
          return string.strip(splitMetaLine[1])
    return ''


  def getWeb(self):
    path = self.getResized(self.getResizedPicPath('web'), 500, 400)
    if not os.path.isabs(path):
      # path is relative to webserver root. Give it a slash
      path = os.sep + path     
    return path


  def getThumb(self):
    path = self.getResized(self.getResizedPicPath('thumb'), 80, 60)
    if not os.path.isabs(path):
      # path is relative to webserver root. Give it a slash
      path = os.sep + path
    return path


  def getResized(self, newName, newWidth, newHeight):
    if (Setup.USE_PIL):
      # using Python Imaging Library
      try:
        originalImage = Image.open(self.picPath)
      except:
        print '<?-- not an image: ',self.picPath,' -->'
        return ''
      width, height = originalImage.size

      if ((width < newWidth) or (height < newHeight)):
        return self.picPath
      else:
        if not os.path.exists(newName):

          newHeight = (height * newWidth) / width
          newImage  = originalImage.resize((
            newWidth, newHeight))
          newImage.save(newName)

        return newName

    else:
      # using ImageMagick
      try:
        text = subprocess.check_output([Setup.pathToIdentify, '-format', '%h %w', self.picPath])
      except:
        # identify failed. Probably not an image file
        return ''
      [height, width] = text.split()

      if ((width < newWidth) or (height < newHeight)):
        return self.picPath
      else:
        if not os.path.exists(newName):
          newHeight = (int(height) * newWidth) / int(width)
          if subprocess.call([Setup.pathToConvert, self.picPath, '-sample', '%sx%s' % (newWidth,newHeight), newName]):
            # convert failed
            return ''
          #os.popen('convert "%s" -sample %sx%s "%s"' % (
          #  self.picPath, newWidth, newHeight, newName))
        return newName


  def getOriginal(self):
    return self.picPath


  def getResizedPicPath(self, prefix):
    [head,tail] = os.path.split(self.picPath)
    resizedPicPath = os.path.join(head,"."+prefix+tail)
    return resizedPicPath


  def getName(self):
    # split the full path file name to just the name with no extension
    [head,tail] = os.path.split(self.picPath)
    [root,ext] = os.path.splitext(tail)
    return root


  def getFileName(self):
    [head,tail] = os.path.split(self.picPath)
    return tail 


  def __repr__(self):
    return self.getName() 
