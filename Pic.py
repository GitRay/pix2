#!/usr/bin/python

import sys, os, string

try:
	from PIL import Image
except ImportError:
	print >> sys.stderr, ("PIL not installed http://www.pythonware.com/products/pil")
	sys.exit(0)

class Pic:

	def __init__(self, aPicPath):
		self.picPath = aPicPath
		

	def getComment(self):
		if self.getOriginal() == '':
			return ''

		pathAndName = self.getOriginal()
		nameBegin = string.rfind(pathAndName, os.sep)
		dir = pathAndName[:nameBegin]

		try:
			metaFile = open('%s%s.meta' % (dir, os.sep))
		except:
			return ''

		fileName = pathAndName[nameBegin + 1:]

		for metaLine in metaFile:
			if string.find(metaLine, '=') != -1:
				splitMetaLine = string.split(metaLine, '=')
				imageName = string.strip(splitMetaLine[0])
				if (imageName == fileName):
					return string.strip(splitMetaLine[1])
		return ''


	def getWeb(self):
		return self.getResized(self.getResizedPicPath('web'), 500, 400)


	def getThumb(self):
		return self.getResized(self.getResizedPicPath('thumb'), 80, 60)


	def getResized(self, newName, newWidth, newHeight):
		originalImage = Image.open(self.picPath)
		width, height = originalImage.size

		if ((width < newWidth) or (height < newHeight)):
			return self.picPath
		else:
			if not os.path.exists(newName):

				newHeight = (height * newWidth) / width
				newImage  = originalImage.resize((newWidth, newHeight))
				newImage.save(newName)

			return newName


	def getOriginal(self):
		return self.picPath


	def getResizedPicPath(self, prefix):
		fileNameEnd   = string.rfind(self.picPath, '.')
		fileNameBegin = string.rfind(self.picPath, os.sep) + 1

		return '%s.%s_%s' % (
			self.picPath[:fileNameBegin], prefix, self.picPath[fileNameBegin:]) 


	def getName(self):
		sepLoc = string.rfind(self.picPath, os.sep) + 1
		dotLoc = string.rfind(self.picPath, '.')

		return string.replace(self.picPath[sepLoc:dotLoc], '_', ' ')


	def getFileName(self):
		sepLoc = string.rfind(self.picPath, os.sep) + 1
		return self.picPath[sepLoc:]


	def __repr__(self):
		return self.getName() 
