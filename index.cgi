#!/usr/bin/python

import cgi 
import os
import sys
import string
from Album import Album
from Pic   import Pic

albumLoc = 'album'

class Presenter: 
	def __init__(self, subAlbum, pic):
		templateLines = open('template.html')

		currDir = '%s%s%s' % (albumLoc, os.sep, subAlbum)	
		album = Album(currDir)
		if (pic != ''):
			pic = Pic('%s%s%s' % (currDir, os.sep, pic))
		else:
			pic = Pic('')
		#else:
		#	if len(album.getPics()) == 0:
		#		pic = Pic('')
		#	else:
		#		firstPic = album.getPics()[0].getFileName()
		#		pic = Pic('%s%s%s' % (currDir, os.sep, firstPic))

		self.printMetaData(albumLoc, currDir, pic)

		for line in templateLines:
			try:
				line = string.replace(line, '@breadcrumb@', self.formatBreadCrumb(album, pic )) 
				line = string.replace(line, '@title@',      self.formatTitle(     album, pic ))
				line = string.replace(line, '@albums@',     self.formatAlbums(    album      ))
				#line = string.replace(line, '@album-description@', self.formatAlbumDescription(album))
				line = string.replace(line, '@pics-list@',  self.formatPicsList(  album      ))
				line = string.replace(line, '@pics-thumb@', self.formatPicsThumb( album      ))
				#line = string.replace(line, '@web-pic@',    self.formatWebPic(    pic ))
				#line = string.replace(line, '@comment@',    pic.getComment())
				line = self.formatContent(line, album, pic)
			except:
				line = 'Unexpected error:', sys.exc_info()[0]
				#raise

			print line,


	def printMetaData(self, albumLoc, currDir, pic):
		print '<!--'
		print 'albumLoc : %s' % albumLoc
		print 'subAlbum : %s' % currDir
		print 'pic      : %s' % pic
		print '-->'


	def formatBreadCrumb(self, album, pic):
		outLines = []
		outLines.append(album.getBreadCrumb())
		if (pic.getName() != ''):
			outLines.append(' | %s' % (pic))

		return string.join(outLines) 


	def formatTitle(self, album, pic):

		albumSep = ' | '
		if (album.getName() == ''):
			albumSep = ''

		picSep = ' | '
		if (pic.getName() == ''):
			picSep = ''

		return "%s%s%s%s" % (albumSep, album.getName(), picSep, pic)


	def formatAlbums(self, album):
		albums = album.getAlbums() 

		if len(albums) == 0:
			return ''

		outLines = []
		outLines.append('<h2>albums</h2>')
		outLines.append('<ul>')

		for album in albums:
			outLines.append('<li><a href="?album=%s">%s</a>' % (
				album.getLinkPath(), 
				album.getName()))

		outLines.append('</ul>')

		return string.join(outLines, '\n')



	def formatPicsList(self, album):
		pics = album.getPics()

		if len(pics) == 0:
			return ''

		outLines = ['<h2>pictures</h2>']
		outLines.append('<ul>')

		for pic in pics:
			outLines.append('<li><a href="?%s=%s&pic=%s">%s</a></li>' % (
				albumLoc,
				album.getName(), 
				pic.getOriginal(),
				pic))
		
		outLines.append('</ul>')

		return string.join(outLines, '\n')


	def formatPicsThumb(self, album):
		pics = album.getPics()

		if len(pics) == 0:
			return ''

		outLines = ['<h2>pictures</h2>']

		for pic in pics:
			outLines.append('<a href="?album=%s&pic=%s"><img src="%s"/></a>' % (
				album.getLinkPath(), 
				pic.getFileName(),
				pic.getThumb()))

		return string.join(outLines, '\n')

	def formatContent(self, line, album, pic):
		if pic.getOriginal() == '':
			line = string.replace(line, '@album-description@', album.getDescription())
			line = string.replace(line, '@web-pic@',           '')
			line = string.replace(line, '@comment@',           '')
		else:
			line = string.replace(line, '@album-description@', '')
			line = string.replace(line, '@web-pic@',           self.formatWebPic(pic))
			line = string.replace(line, '@comment@',           pic.getComment())
		return line


	def formatWebPic(self, pic):
		if pic.getOriginal() == '':
			return ''

		outLines = []
		outLines.append(
			'<a href="%s"><img src="%s"/></a>' % (
				pic.getOriginal(), 
				pic.getWeb()))
		return string.join(outLines, '\n')


def getArg(aForm, aKey):
	if aForm.has_key(aKey): 
		print '<!-- %s: %s -->' % (aKey, aForm[aKey].value)
		return aForm[aKey].value 
	return ''


if __name__=='__main__': 

	sys.stderr == sys.stdout 
	print 'Content-type:text/html\n' 
	iForm = cgi.FieldStorage() 
	Presenter(getArg(iForm, 'album'), getArg(iForm, 'pic'))
