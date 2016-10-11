#!/usr/bin/python
from __future__ import print_function

import sys, os, string, subprocess, shutil, cgi, posixpath, errno, copy, wsgiref.util, posixpath, warnings, hashlib, imghdr
# python3 has different urllib paths
try:
    from urllib import quote_plus, quote, urlencode
except:
    from urllib.parse import quote_plus, quote, urlencode

# Python 3 does not have a separate "cPickle"
try:
    import cPickle as pickle
except ImportError:
    import pickle

# cgi.escape triggers a depricated warning in Python 3.2
try:
  from html import escape
except ImportError:
  from cgi import escape

import Setup

if (Setup.USE_PIL):
  try:
    from PIL import Image
  except ImportError:
    print("You specify PIL in Setup.py, but you do not have PIL installed.\nGet PIL at http://www.pythonware.com/products/pil",file=sys.stderr)
    Setup.USE_PIL = False

class Pic:

  def __init__(self, start_response,aPicPath = ''):
    self.start_response = start_response
    self.isPic = False
    self.picPath = os.path.normpath(os.path.abspath(aPicPath))
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
    pickle_suffix = '_' + str(os.path.getmtime(pic_path)) + "_" + str(os.path.getsize(pic_path))
    pickle_path = os.path.join( \
      head, \
      '.pickle_' + tail + pickle_suffix \
    )
    if len(pickle_path) > Setup.f_namemax:
      pickle_path = os.path.join( head, '.pickle_{}_{}'.format(Pic.getShortenedName(tail),pickle_suffix))
    return os.path.normpath(pickle_path)

  
  @staticmethod
  def getShortenedName(orig_name):
    # sometimes the pickled or resized names are too big for the filesystem
    # We'll try to make a unique name by using two different hashes tacked together
    # Stitch together SHA1 and MD5, since those are short-ish hashes gauranteed
    # to be available in hashlib
    b_fname = orig_name.encode()
    sha_text = hashlib.sha1(b_fname).hexdigest()
    md5_text = hashlib.md5(b_fname).hexdigest()
    return sha_text + '_' + md5_text
    
    
  def savePickledVersion(self):
    pickle_path = self.getPicklePath(self.picPath)
    [head, tail] = os.path.split(pickle_path)
    try:
      os.makedirs(head)
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        raise
    with open(pickle_path, 'wb') as f:
      # cannot pickle the start_response object, temporarily delete it
      start_response = self.start_response
      del(self.start_response)
      pickle.dump( self, f )
      # restore start_response object
      self.start_response = start_response


  @staticmethod
  def loadPickledVersion(start_response, pic_path):
    pickle_path = Pic.getPicklePath(pic_path)
    with open(pickle_path,"rb") as f:
      new_obj = pickle.load( f )
    # restore start_response (needed to delete to pickle)
    new_obj.start_response = start_response
    return new_obj


  def getResizedLink(self,this_name):
    # return a path to either an existing thumbnail or to the script that makes thumbs
    # path relative to pics directory
    pic_path = self.resizedDict[this_name]['path']
    pic_relpic = os.path.normpath(os.path.relpath(self.picPath,Setup.albumLoc))
    # make it url-friendly
    
    pic_relpic_safe = self.makePathUrlFriendly(pic_relpic)
    # picture name
    [head, pic_fname] = os.path.split(self.picPath)
    pic_name_safe = self.getName()
    pic_fname_safe = self.makePathUrlFriendly(pic_fname, use_quote_plus=True)
    pic_width = self.resizedDict[this_name]['width']
    pic_height = self.resizedDict[this_name]['height']
    if self.resizedDict[this_name]['exists']:
      # path relative to the web server
      pic_relweb = os.path.relpath(pic_path,Setup.pathToPicCache)
      pic_relweb = os.path.normpath(os.path.join(Setup.webPathToPicCache,pic_relweb))
      # un-windows the path and make it safe for the web
      pic_relweb_safe = self.makePathUrlFriendly(self.webifyPath(pic_relweb))
    else:
      # path to the picture making script
      script_path = os.path.join(Setup.pathToCGI,'index.cgi')
      script_relweb = os.path.normpath(os.path.relpath(script_path,Setup.pathToCGI))
      script_relweb_safe = self.makePathUrlFriendly(self.webifyPath(script_relweb),use_quote_plus=True)
      pict_args = { 'pict_creator': this_name, 'pict_path': pic_relpic }
      pic_relweb_safe = script_relweb_safe + "?" + urlencode(pict_args)
      
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
    with open(self.picPath,'rb') as f:
      # PIL uses logger to throw crap onto stderr. We'll redirect it for now
      old_stderr = sys.stderr
      with open(os.devnull,'w') as devnull:
        sys.stderr = devnull
        try:
          this_image = Image.open(f)
        except:
          sys.stderr = old_stderr
          raise
      sys.stderr = old_stderr
      [self.picDim[0], self.picDim[1]] = this_image.size
      self.picFormat = this_image.format
      # get the rotation
      try:
        warnings.simplefilter("ignore")
        this_exif = this_image._getexif()
        warnings.resetwarnings()
      except (AttributeError,IOError,ZeroDivisionError,ValueError, IndexError):
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
    # swallow any subprocess stderr output by redirecting to dev/null
    with open(os.devnull, 'w') as dev_null:
      text = subprocess.check_output( \
        [Setup.pathToIdentify, '-format', '%w %h %m %[exif:orientation]', this_path],\
        stderr=dev_null \
      )
    picDim = text.split()
    self.picDim[0] = int(picDim[0])
    self.picDim[1] = int(picDim[1])
    self.picFormat = picDim[2].decode()
    if len(picDim) > 3:
      self.picOrientation = int(picDim[3])
    else:
      self.picOrientation = 1

    
  def updatePicInfo(self):
    self.isPic = False
    tail = os.path.splitext(self.picPath)[1][1:].strip().upper()
    if tail == '':
      # file has no extension - see if we can still figure it out
      # Needed to do this because many of my old pictures came from Mac, which
      # formerly did not make much use of extensions.
      this_type = imghdr.what(self.picPath)
      if not this_type is None:
        tail = this_type.upper()
      print('Missing extension, guess: {} in {}'.format(tail, self.picPath), file=sys.stderr)
    if not tail in Setup.image_formats:
      print('Not supported extension: {} in {}'.format(tail,self.picPath),file=sys.stderr)
      return
    # PIL is usually faster, but not for PhotoShop files.
    if Setup.USE_PIL and not tail == 'PSD':
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
      if meta_separator in metaLine:
      #if string.find(metaLine, meta_separator) != -1:
        splitMetaLine = metaLine.split(meta_separator)
        #splitMetaLine = string.split(metaLine, meta_separator)
        imageName = splitMetaLine[0].strip()
        #imageName = string.strip(splitMetaLine[0])
        if (imageName == fileName):
          metaFile.close()
          return splitMetaLine[1].strip()
          #return string.strip(splitMetaLine[1])
    metaFile.close()
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
      path_pre = '%sx%s' % (this_image['width'], this_image['height'])
      this_image['path'] =  os.path.normpath(os.path.join( \
        Setup.pathToPicCache, \
        os.path.relpath(pic_path,Setup.albumLoc), \
        '{}.{}.jpg'.format(path_pre,head) \
      ))
      if len(this_image['path']) > Setup.f_namemax:
        this_image['path'] =  os.path.normpath(os.path.join( \
          Setup.pathToPicCache, \
          os.path.relpath(pic_path,Setup.albumLoc), \
          '{}.{}.jpg'.format(path_pre,self.getShortenedName(head)) \
        ))

      # We have the filename, now update the status flag if it exists
      if os.path.isfile(this_image['path']):
        this_image['exists'] = True
      else:
        this_image['exists'] = False
        
        
  def resizeWithPIL(self,this_image):
      with open(self.picPath, 'rb') as f:
        # PIL uses logger to throw crap onto stderr. We'll redirect it for now
        old_stderr = sys.stderr
        with open(os.devnull,'w') as devnull:
          sys.stderr = devnull
          try:
            originalImage = Image.open(f)
          except:
            sys.stderr = old_stderr
            raise
        sys.stderr = old_stderr
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
    except WindowsError as exception:
      if exception.errno != 183: # Cannot create a file when that file already exists
          raise
    [_, tail] = os.path.split(self.picPath)
    [f_name, f_ext] = os.path.splitext(tail)
    writer = self.start_response(
      '200 OK',
      [
        ("Content-Type","image/jpeg"),
        ("Content-Disposition",'attachment; filename="{}".jpeg'.format(f_name))
      ]
    )
    # PIL is usually faster than ImageMagic - but not on Photoshop files
    if Setup.USE_PIL and not f_ext.lower() == 'psd':
      try:
        self.resizeWithPIL(this_image)
      except (IOError,ValueError) as this_exception:
        if 'cannot identify image file' in str(this_exception) or\
           'image has wrong mode'       in str(this_exception):
          # PIL has failed us, try with imagemagick
          self.resizeWithIM(this_image)
        else:
          raise
    else:
      # use imagemagick
      self.resizeWithIM(this_image)
    f = open(this_image['path'],'rb')
    return wsgiref.util.FileWrapper(f, blksize=131072)


  def downloadImage(self, format):
    if format.lower() == self.picFormat.lower():
      # directly output the file
      [_, tail] = os.path.split(self.picPath)
      [f_name, f_ext] = os.path.splitext(tail)
      writer = self.start_response(
        '200 OK',
        [
          ("Content-Type","image/jpeg"),
          ("Content-Disposition",'attachment; filename="{}.{}"'.format(f_name,format.lower()))
        ]
      )
      f = open(self.picPath,'rb')
      return wsgiref.util.FileWrapper(f, blksize=131072)
    
    # convert the file.
    self.resizedDict['original'] = { \
      'exists': False, \
      'path': '', \
      'width': self.picDim[0], \
      'height': self.picDim[1] \
    }
    self.updateResizedImages()
    return self.spitOutResizedImage('original')
    
  def getOriginal(self):
    return self.picPath


  def getResizedPicPath(self, prefix):
    relative_path = os.path.relpath(self.picPath,Setup.albumLoc)
    cache_path = os.path.join(Setup.pathToPicCache, relative_path)
    [head,tail] = os.path.split(cache_path)
    resizedPicPath = os.path.join(head,prefix+"."+tail)
    return os.path.normpath(resizedPicPath)


  def getName(self):
    [head,tail] = os.path.split(self.picPath)
    # split the full path file name to just the name with no extension
    [pic_name, _] = os.path.splitext(tail)
    # make it html-friendly
    pic_name_safe = escape(pic_name,True).encode('ascii','xmlcharrefreplace')
    return pic_name_safe.decode()


  def getFileName(self):
    [head,tail] = os.path.split(self.picPath)
    return tail 

  @staticmethod
  def makePathUrlFriendly(path, use_quote_plus=False):
    # because Windows uses the backslash "\", we must be sure that paths are
    # converted to forward slashes "/" for urls
    url_list = os.path.normpath(path).split(os.sep)
    if use_quote_plus:
      return quote_plus(posixpath.join(*url_list))
    else:
      return quote(posixpath.join(*url_list))
    
  def __str__(self):
    return self.getName()


  def __repr__(self):
    return "Pic(%r)" % self.picPath


  # Python 3 does not support __cmp__ or the cmp function. Need to add __lt__
  def __cmp__(self,other):
    return cmp(self.getName(),other.getName())

  # Python 3 needs a less than method to support sorting.
  def __lt__(self, other):
    return self.getName() < other.getName()
