#!/usr/bin/python

import sys, os, string

from Pic import Pic

class Album:

	def __init__(self, albumDir, recurse = 1):
		self.albumDir = albumDir

		self.albums = []
		self.pics   = []

		if (recurse):
			for entry in os.listdir(albumDir):
				if (entry[0] != '.'):
					entryAndPath = '%s%s%s' % (albumDir, os.sep, entry)
					if os.path.isdir(entryAndPath):
						self.albums.append(Album(entryAndPath, 0))
					elif os.path.isfile(entryAndPath):
						self.pics.append(Pic(entryAndPath))


	def getAlbums(self):
		return self.albums


	def getPics(self):
		return self.pics


	def getName(self):
		sepLoc = string.rfind(self.albumDir, os.sep) + 1
		return string.replace(self.albumDir[sepLoc:], '_', ' ')


	def getLinkPath(self):
		fullPath = self.albumDir
		loc = string.find(fullPath, os.sep) + 1
		return fullPath[loc:]


	def getBreadCrumb(self):
		linkPath = self.getLinkPath()
		breadCrumb   = ''
		runningCrumb = ''

		if linkPath != '':
			for crumb in string.split(linkPath, os.sep):
				runningCrumb = '%s%s%s' % (runningCrumb, os.sep, crumb)
				displayCrumb = string.replace(crumb, '_', ' ')
				breadCrumb = '%s | <a href="?album=%s">%s</a>' % (
					breadCrumb, 
					runningCrumb[1:],
					displayCrumb)

		return breadCrumb[3:]
