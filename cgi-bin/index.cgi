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

import os
import sys
from Application import Application
import wsgiref

def start_response(self, status, headers,exc_info=None):
    """'start_response()' callable as specified by PEP 333"""
    assert type(status) is StringType,"Status must be a string"
    assert len(status)>=4,"Status must be at least 4 characters"
    assert int(status[:3]),"Status message must begin w/3-digit code"
    assert status[3]==" ", "Status message must have a space after code"
    
    print("Status: {}".format(status))
    for x in headers:
      print("{}: {}".format(x[0],x[1]))
      
    return sys.stdout.write

  
if __name__=='__main__': 

  sys.stderr == sys.stdout
  # This application is designed to be run from a wsgi server, so this cgi script
  # will just re-use the Application object.
  
  # construct a wsgi-compliant environ dictionary
  environ = dict(os.environ.items())
  environ["wsgi.version"] = (1,0)
  environ["wsgi.scheme"] = wsgiref.guess_scheme(environ)
  environ["wsgi.input"] = sys.stdin
  environ['wsgi.errors'] = sys.stderr
  environ['wsgi.multithread'] = True
  environ['wsgi.multiprocess'] = True
  environ['wsgi.run_once'] = True
  
  app = Application()
  app(environ, start_response)
  