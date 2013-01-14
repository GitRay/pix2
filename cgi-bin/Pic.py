#!/usr/bin/python

import sys, os, string, subprocess, urllib, shutil, cgi, posixpath, errno

import Setup

if (Setup.USE_PIL):
  try:
    from PIL import Image
  except ImportError:
    print "get PIL at http://www.pythonware.com/products/pil"
    Setup.USE_PIL = False

class Pic:

  def __init__(self, aPicPath = ''):
    self.isPic = True
    self.picPath = os.path.abspath(aPicPath)
    self.picDim = [0,0]      # width, height
    self.picOrientation = 1
    self.resizedDict = { \
      'thumb': { \
        'exists': False, \
        'path': '', \
        'width': 80, \
        'height': 60 \
      }, \
      'web': { \
        'exists': False, \
        'path': '', \
        'width': 500, \
        'height': 400 \
      } \
    }
    
    # if the aPicPath is filled in, just look up the dimensions and some EXIF info
    if aPicPath != '':
      self.updatePicInfo()
      # update the thumbnail paths
      self.updateResizedImages()
    else:
      self.isPic = False
  
  def getResizedLink(self,this_name):
    # return a path to either an existing thumbnail or to the script that makes thumbs
    # path relative to pics directory
    pic_path = self.resizedDict[this_name]['path']
    pic_relpic = os.path.relpath(self.picPath,Setup.albumLoc)
    # make it url-friendly
    pic_relpic_safe = urllib.quote_plus(pic_relpic)
    # picture name
    [head, pic_fname] = os.path.split(self.picPath)
    pic_name_safe = self.getName()
    pic_fname_safe = urllib.quote(pic_fname)
    pic_width = self.resizedDict[this_name]['width']
    pic_height = self.resizedDict[this_name]['height']
    if self.resizedDict[this_name]['exists']:
      # path relative to the web server
      pic_relweb = os.path.relpath(pic_path,Setup.pathToCGI)
      # un-windows the path and make it safe for the web
      pic_relweb_safe = urllib.quote(self.webifyPath(pic_relweb))
    else:
      # path to the picture making script
      script_path = os.path.join(Setup.pathToCGI,'index.cgi')
      script_relweb = os.path.relpath(script_path,Setup.pathToCGI)
      script_relweb_safe = urllib.quote(self.webifyPath(script_relweb))
      pict_args = { 'pict_creator': this_name, 'pict_path': pic_relpic }
      pic_relweb_safe = script_relweb_safe + "?" + urllib.urlencode(pict_args)
      
    # Return web-friendly information about the photo
    return pic_fname_safe, pic_relpic_safe, pic_name_safe, pic_relweb_safe, pic_width, pic_height
  
  def webifyPath(self,path):
    # Windows likes backslashes. The web does not.
    abs_path = ''
    if os.path.isabs(path):
      abs_path = os.sep
      path = path[1:]
    remaining_path = path
    split_path = []
    while remaining_path != '':
      [head,tail] = os.path.split(remaining_path)
      remaining_path = head
      split_path = [tail] + split_path
    split_path = [abs_path] + split_path
    return posixpath.join(*split_path)

  def updatePicInfo(self):
    if Setup.USE_PIL:
      # Look up the picture dimensions.
      this_image = Image.open(self.picPath)
      [self.picDim[0], self.picDim[1]] = this_image.size
      # get the rotation
      this_exif = this_image._getexif()
      if this_exif:
        # I got the number for the EXIF "Orientation" field (274) from PIL.ExifTags.TAGS
        self.picOrientation = this_exif.get(274,1)
      else:
        self.picOrientation = 1
    else:
      text = subprocess.check_output([Setup.pathToIdentify, '-format', '%h %w %[exif:orientation]', self.picPath])
      try:
        [self.picDim[0], self.picDim[1], self.picOrientation] = text.split()
      except ValueError:
        # must not be any orientation data
        [self.picDim[0], self.picDim[1]] = text.split()
        self.picOrientation = 1
        
    
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

  def resizeCalcs(self, max_width, max_height, orig_width, orig_height):
     # Calculate the dimensions.
    ratio = 1.0*orig_width/orig_height
    new_width = orig_width
    new_height = orig_height
    if orig_width > max_width:
      #width is larger than height
      new_width = max_width
      new_height = int(round(max_width / ratio,0))
    if new_height > max_height:
      new_width = int(round(max_height * ratio,0))
      new_height = max_height
    return [new_width, new_height]
   
  def updateResizedImages(self):
    for this_resize in self.resizedDict:
      this_image = self.resizedDict[this_resize]
      [this_image['width'], this_image['height']] = \
        self.resizeCalcs(this_image['width'],this_image['height'],*self.picDim)
      [pic_path, pic_name] = os.path.split(self.picPath)
      this_image['path'] =  os.path.join( \
        Setup.pathToPicCache, \
        os.path.relpath(pic_path,Setup.albumLoc), \
        '%sx%s.%s' % (this_image['width'], this_image['height'], pic_name) \
      )
      
      
      # We have the filename, now update the status flag if it exists
      this_image['exists'] = False
      if Setup.USE_PIL:
        try:
          # opening with Image might be slower than just checking for existence
          this_resized = Image.open(this_image['path'])
          this_image['exists'] = True
        except IOError:
          # thumbnail does not exist
          this_image['exists'] = False
      else:
        # use imagemagick
        try:
          # opening with identify is certainly slower than just checking for existence.
          text = subprocess.check_output([Setup.pathToIdentify, '-format', '%h %w', self.picPath])
          this_image['exists'] = True
        except CalledProcessError:
          # identify could not process the file
          this_image['exists'] = False
  
  def spitOutResizedImage(self, resize_type):
    this_image = self.resizedDict[resize_type]
    # make sure the path to the resized file exists
    [head, tail] = os.path.split(this_image['path'])
    try:
      os.makedirs(head)
    except OSError as exception:
      if exception.errno != errno.EEXIST:
          raise
    print "Content-Type: image/jpeg"
    print
    if Setup.USE_PIL:
      originalImage = Image.open(self.picPath)
      newImage  = originalImage.resize((this_image['width'], this_image['height']))
      newImage.save(this_image['path'])
    else:
      # use imagemagick
      subprocess.call([Setup.pathToConvert, self.picPath, '-sample', '%sx%s' \
        % (this_image['width'],this_image['height']), this_image['path']] \
      )
    
    with open(this_image['path'], "r") as f:
      shutil.copyfileobj(f, sys.stdout)


  def getOriginal(self):
    return self.picPath


  def getResizedPicPath(self, prefix):
    relative_path = os.path.relpath(self.picPath,Setup.albumLoc)
    cache_path = os.path.join(Setup.pathToPicCache, relative_path)
    [head,tail] = os.path.split(cache_path)
    resizedPicPath = os.path.join(head,prefix+"."+tail)
    return resizedPicPath


  def getName(self):
    [head,tail] = os.path.split(self.picPath)
    # split the full path file name to just the name with no extension
    [pic_name, _] = os.path.splitext(tail)
    # make it html-friendly
    pic_name_safe = cgi.escape(pic_name,True).encode('ascii','xmlcharrefreplace')
    return pic_name_safe


  def getFileName(self):
    [head,tail] = os.path.split(self.picPath)
    return tail 


  def __repr__(self):
    return self.getName() 
