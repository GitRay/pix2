#!/usr/bin/python

import sys, os, string

# if this is false we try to use ImageMagick
# if you set it to true we try to import and use PIL
USE_PIL = 0 

if (USE_PIL):
	try:
		from PIL import Image
	except ImportError:
		print "get PIL at http://www.pythonware.com/products/pil"
		USE_PIL = 0

class Pic:

	def __init__(self, aPicPath):
		# validate that it is a pic if it has a filename
		# this is a TOTAL hack, i should be ashamed of that this line of code is necessary, 
		# we get some stray '//' in the urls, causes trouble on freebsd for some reason. 
		self.picPath = string.replace(aPicPath, '%s%s' % (os.sep, os.sep), os.sep) 
			
		#self.picPath = aPicPath
		#if (aPicPath != ''):
		#	originalImage = Image.open(aPicPath)


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
		if (USE_PIL):
			# using Pyton Imaging Library
			originalImage = Image.open(self.picPath)
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
			pipe = os.popen("identify %s" % self.picPath, 'r')
			text = pipe.read()
			sts  = pipe.close() # not sure why you do this
			
			wordNum = 0
			width   = 0
			height  = 0 
			for word in text.split():
				if (wordNum == 2):
					width, height = word.split('x')
				wordNum = wordNum + 1

			if ((width < newWidth) or (height < newHeight)):
				return self.picPath
			else:
				if not os.path.exists(newName):
					newHeight = (int(height) * newWidth) / int(width)
					os.popen('convert "%s" -sample %sx%s "%s"' % (
						self.picPath, newWidth, newHeight, newName))
				return newName


	def getOriginal(self):
		return self.picPath


	def getResizedPicPath(self, prefix):
		fileNameEnd   = string.rfind(self.picPath, '.')
		fileNameBegin = string.rfind(self.picPath, os.sep) + 1

		resizedPicPath = '%s.%s_%s' % (self.picPath[:fileNameBegin], prefix, self.picPath[fileNameBegin:]) 
		#print '<pre>self.picPath: %s</pre>' % (self.picPath)
		#print '<pre>returning resizedPicPath: %s</pre>' % (resizedPicPath)

		return resizedPicPath


	def getName(self):
		sepLoc = string.rfind(self.picPath, os.sep) + 1
		dotLoc = string.rfind(self.picPath, '.')

		return string.replace(self.picPath[sepLoc:dotLoc], '_', ' ')


	def getFileName(self):
		sepLoc = string.rfind(self.picPath, os.sep) + 1
		fileName = self.picPath[sepLoc:]

		#print '<pre>returning fileName: %s</pre>' % (fileName)
		return fileName 


	def __repr__(self):
		return self.getName() 
