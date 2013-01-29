#!/usr/local/bin/python
#!/usr/bin/python        # on mac

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

import cgi 
import os
import sys
import urllib
import traceback
from Pic   import Pic
from Presenter import Presenter
import Setup

def getArg(aForm, aKey):
  if aForm.has_key(aKey): 
    #print '<!-- %s: %s -->' % (aKey, aForm[aKey].value)
    return urllib.unquote(aForm[aKey].value) 
  return ''

  
if __name__=='__main__': 

  sys.stderr == sys.stdout 
  try:
    iForm = cgi.FieldStorage() 
    album       = getArg(iForm, 'album')
    pic         = getArg(iForm, 'pic')
    control     = getArg(iForm, 'control')
    adminAction = getArg(iForm, 'admin')

    pict_creator = getArg(iForm, 'pict_creator')
    download = getArg(iForm, 'download')
    if pict_creator != '':
      # make a picture
      pict_path = getArg(iForm, 'pict_path')
      pic_obj = Pic(os.path.join(Setup.albumLoc, pict_path))
      pic_obj.spitOutResizedImage(pict_creator)
    
    elif download == 'jpeg':
      # download the picture, converted to jpeg if necessary
      pict_path = getArg(iForm, 'pict_path')
      pic_obj = Pic(os.path.join(Setup.albumLoc, pict_path))
      pic_obj.downloadImage(download)
    else:
      # make the web page
      print 'Content-type: text/html; charset=utf-8\n' 
      #print '<!-- path     : %s -->' % os.path.abspath(os.curdir)
      #print '<!-- argv[0]  : %s -->' % os.path.dirname(sys.argv[0])

      Presenter(album, pic, control)
 
  except:
    print '''
      <pre><h1>pix broke, you get to keep both pieces</h1>
      Traceback has been logged.</pre>
    '''
    traceback.print_exc()
