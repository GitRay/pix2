#!/usr/bin/python

import sys, os, string, subprocess, urllib, shutil, cgi, posixpath, errno, cPickle

import Setup

if (Setup.USE_PIL):
  try:
    from PIL import Image
  except ImportError:
    print "get PIL at http://www.pythonware.com/products/pil"
    Setup.USE_PIL = False

class Pic:

  def __init__(self, aPicPath = ''):
    self.isPic = False
    self.picPath = os.path.abspath(aPicPath)
    self.picDim = [0,0]      # width, height
    self.picFormat = ''
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
      if self.isPic:
        # update the thumbnail paths
        self.updateResizedImages()
        # save the pickled version to disk so we don't have to open the file again
        self.savePickledVersion()
    else:
      self.isPic = False
  
  @staticmethod
  def getPicklePath(pic_path):
    pic_relpic = os.path.relpath(pic_path, Setup.albumLoc)
    pic_cache = os.path.join(Setup.pathToPicCache, pic_relpic)
    [head, tail] = os.path.split(pic_cache)
    pickle_path = os.path.join( \
      head, \
      '.pickle_' + tail + '_' + str(os.path.getmtime(pic_path)) + "_" + str(os.path.getsize(pic_path)) \
    )
    return pickle_path

  
  def savePickledVersion(self):
    pickle_path = self.getPicklePath(self.picPath)
    [head, tail] = os.path.split(pickle_path)
    try:
      os.makedirs(head)
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        raise
    cPickle.dump( \
      self, \
      open(pickle_path, 'wb') \
    )

  @staticmethod
  def loadPickledVersion(pic_path):
    pickle_path = Pic.getPicklePath(pic_path)
    return cPickle.load( open( pickle_path, "r" ) )


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
      pic_relweb = os.path.relpath(pic_path,Setup.pathToPicCache)
      pic_relweb = os.path.join(Setup.webPathToPicCache,pic_relweb)
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

  def getPicDimsWithPIL(self):
    this_image = Image.open(self.picPath)
    [self.picDim[0], self.picDim[1]] = this_image.size
    self.picFormat = this_image.format
    # get the rotation
    try:
      this_exif = this_image._getexif()
    except (AttributeError,IOError):
      # this file has no EXIF data (might be a TIFF) or data could be missing or corrupt
      this_exif = {}
    if this_exif:
      # I got the number for the EXIF "Orientation" field (274) from PIL.ExifTags.TAGS
      self.picOrientation = this_exif.get(274,1)
    else:
      self.picOrientation = 1

  def getPicDimsWithIM(self):
    # add "[0]" to picture path so that imagemagick only looks at the first frame of the file,
    # just in case it is a big video
    this_path = self.picPath + '[0]'
    text = subprocess.check_output( \
      [Setup.pathToIdentify, '-format', '%w %h %m %[exif:orientation]', this_path] \
    )
    picDim = text.split()
    self.picDim[0] = int(picDim[0])
    self.picDim[1] = int(picDim[1])
    self.picFormat = picDim[2]
    if len(picDim) > 3:
      self.picOrientation = int(picDim[3])
    else:
      self.picOrientation = 1

    
  def updatePicInfo(self):
    self.isPic = False
    tail = os.path.splitext(self.picPath)[1][1:].strip().upper()
    if not tail in Setup.image_formats:
      print 'Not supported extension:', tail
      return
    if Setup.USE_PIL:
      # Look up the picture dimensions.
      try:
        self.getPicDimsWithPIL()
      except IOError:
        # PIL can't deal with this file type
        # retry with imagemagick
        try:
          self.getPicDimsWithIM()
        except subprocess.CalledProcessError:
          # imagemagic can't do it
          self.isPic = False
          return
    else:
      # fall back on imagemagick
      try:
        self.getPicDimsWithIM()
      except subprocess.CalledProcessError:
        # imagemagic can't do it
        self.isPic = False
        return      
    if self.picOrientation == 6 or self.picOrientation == 8:
      # Rotation 270 (6) or Rotation 90 (8)
      # swap width and height
      [self.picDim[1],self.picDim[0]] = self.picDim
    
    self.isPic = True
    
    
  def getComment(self):
    if self.getOriginal() == '':
      return ''

    pathAndName = self.getOriginal()
    #nameBegin = string.rfind(pathAndName, os.sep)
    #dir = pathAndName[:nameBegin]
    [dir, fileName] = os.path.split(pathAndName)

    try:
      # This is the pix-style meta file
      metaFile = open('%s%s.meta' % (dir, os.sep))
      meta_separator = '='
    except:
      try:
        # This is the yappa-style meta file 
        metaFile = open(os.path.join(dir,'captions.txt'))
        meta_separator = '|'
      except:
        return ''

    #fileName = pathAndName[nameBegin + 1:]

    for metaLine in metaFile:
      if string.find(metaLine, meta_separator) != -1:
        splitMetaLine = string.split(metaLine, meta_separator)
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
      [head,tail] = os.path.splitext(pic_name)
      this_image['path'] =  os.path.join( \
        Setup.pathToPicCache, \
        os.path.relpath(pic_path,Setup.albumLoc), \
        '%sx%s.%s.%s' % (this_image['width'], this_image['height'], head, 'jpg') \
      )
      
      # We have the filename, now update the status flag if it exists
      if os.path.isfile(this_image['path']):
        this_image['exists'] = True
      else:
        this_image['exists'] = False
        
        
  def resizeWithPIL(self,this_image):
      originalImage = Image.open(self.picPath)
      if self.picOrientation == 3:
        # Rotation 180
        originalImage.draft("RGB",tuple(self.picDim))
        newImage = originalImage.transpose(Image.ROTATE_180)
      elif self.picOrientation == 6:
        # Rotation 270
        originalImage.draft("RGB",tuple(self.picDim[::-1]))
        newImage = originalImage.transpose(Image.ROTATE_270)
      elif self.picOrientation == 8:
        # Rotation 90
        originalImage.draft("RGB",tuple(self.picDim[::-1]))
        newImage = originalImage.transpose(Image.ROTATE_90)
      else:
        # Leave it alone
        originalImage.draft("RGB",tuple(self.picDim))
        newImage = originalImage
      
      newImage = newImage.resize((this_image['width'], this_image['height']),Image.ANTIALIAS)
      newImage = newImage.convert("RGB")
      newImage.save(this_image['path'])

  def resizeWithIM(self, this_image):
    # add "[0]" to picture path so that imagemagick only looks at the first frame of the file,
    # just in case it is a big video
    this_path = self.picPath + '[0]'
    arguments = ['-resize','%sx%s' \
      % (this_image['width'],this_image['height']), this_image['path'] \
    ]
    if self.picOrientation == 3:
      # Rotation 180
      arguments = arguments + ['-rotate','180']
    elif self.picOrientation == 6:
      # Rotation 270
      arguments = arguments + ['-rotate','270']
    elif self.picOrientation == 8:
      # Rotation 90
      arguments = arguments + ['-rotate','90']

    subprocess.call([Setup.pathToConvert, this_path] + arguments)


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
      try:
        self.resizeWithPIL(this_image)
      except IOError as this_exception:
        if this_exception.message == 'cannot identify image file':
          # PIL has failed us, try with imagemagick
          self.resizeWithIM(this_image)
    else:
      # use imagemagick
      self.resizeWithIM(this_image)
          
    with open(this_image['path'], "r") as f:
      shutil.copyfileobj(f, sys.stdout)


  def downloadImage(self, format):
    if format.lower() == self.picFormat.lower():
      # directly output the file
      print "Content-Type: image/jpeg"
      print
      with open(self.picPath, "r") as f:
        shutil.copyfileobj(f, sys.stdout)
      return
    
    # convert the file.
    self.resizedDict['original'] = { \
      'exists': False, \
      'path': '', \
      'width': self.picDim[0], \
      'height': self.picDim[1] \
    }
    self.updateResizedImages()
    self.spitOutResizedImage('original')
    
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


  def __str__(self):
    return self.getName()


  def __repr__(self):
    return "Pic(%r)" % self.picPath


  def __cmp__(self,other):
    return cmp(self.getName(),other.getName())
