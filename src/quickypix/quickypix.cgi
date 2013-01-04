#!/usr/bin/python2.3

# $Id: quickypix.cgi 280 2005-12-17 00:00:46Z quarl $

## Copyright (C) 2005 Demian Neidetcher
## Copyright (C) 2005 Karl Chen
## Copyright (C) 2005 Hollis Blanchard

## This file is part of QuickyPix.

## QuickyPix is free software; you can redistribute it and/or modify it under
## the terms of the GNU General Public License as published by the Free
## Software Foundation; either version 2, or (at your option) any later
## version.

## QuickyPix is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.

## You should have received a copy of the GNU General Public License along
## with QuickyPix; see the file COPYING.  If not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
## USA.

import Presenter
import util
import os

if __name__=='__main__':
    try:
        Presenter.Presenter(os.environ)
    except util.AccessError, e:
        e.print_exit()

