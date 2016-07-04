import cv2
import os
import numpy as np
from sklearn.externals import joblib

class CaptchaDecoder:
	def __init__(self):
		if os.path.exists('model/captcha.pkl'):
			self.classifier = joblib.load('model/captcha.pkl')
		else:
			raise FileNotFoundError
	
	def deNoise(self): 
		for i in range(len(self.img)):
			for j in range(len(self.img[i])):
				if self.img[i][j] == 255:
					count = 0 
					for k in range(-2, 3):
						for l in range(-2, 3):
							try:
								if self.img[i + k][j + l] == 255:
									count += 1
							except IndexError:
								pass
					if count <= 4:
						self.img[i][j] = 0
						
		self.img = cv2.dilate(self.img, (2, 2), iterations=1)

	def splitImage(self):
		contours, hierarchy = cv2.findContours(self.img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
		cnts = sorted([(c, cv2.boundingRect(c)[0]) for c in contours], key=lambda x:x[1])
		
		self.boundary = []
		
		for index, (c, _) in enumerate(cnts):
			(x, y, w, h) = cv2.boundingRect(c)
		
			try:
				if w > 8 and h > 8:
					add = True
					for i in range(0, len(self.boundary)):
						if abs(cnts[index][1] - self.boundary[i][0]) <= 3:
							add = False
							break
					if add:
						self.boundary.append((x, y, w, h))
			except IndexError:
				pass
	
	def rotate(self):
		self.data = []
		for index, (x, y, w, h) in enumerate(self.boundary):
			roi = self.img[y: y + h, x: x + w]
			thresh = roi.copy() 
			
			angle = 0
			smallest = 999
			row, col = thresh.shape
		
			for ang in range(-60, 61):
				M = cv2.getRotationMatrix2D((col / 2, row / 2), ang, 1)
				t = cv2.warpAffine(thresh.copy(), M, (col, row))
		
				r, c = t.shape
				right = 0
				left = 999
		
				for i in range(r):
					for j in range(c):
						if t[i][j] == 255 and left > j:
							left = j
						if t[i][j] == 255 and right < j:
							right = j
		
				if abs(right - left) <= smallest:
					smallest = abs(right - left)
					angle = ang
		
			M = cv2.getRotationMatrix2D((col / 2, row / 2), angle, 1)
			thresh = cv2.warpAffine(thresh, M, (col, row))
			thresh = cv2.resize(thresh, (20, 20))
		
			self.data.append(thresh)
	
	def identifyFromArray(self):
		self.data = np.array(self.data)
		self.data = self.data.reshape(len(self.data),-1)
		self.data = (self.data - np.min(self.data, 0)) / (np.max(self.data, 0) + 0.0001)
		answer = self.classifier.predict(self.data)
		return ''.join(answer)
		
		
	def identify(self,imgpath):
		if not os.path.exists(imgpath):
			raise FileNotFoundError
		self.img = cv2.imread(imgpath, flags=cv2.IMREAD_GRAYSCALE)
		retval, self.img = cv2.threshold(self.img, 115, 255, cv2.THRESH_BINARY_INV)
		self.deNoise()
		self.splitImage()
		self.rotate()
		return self.identifyFromArray()

if __name__ == '__main__':
	decoder = CaptchaDecoder()
	print(decoder.identify('pic.jpg'))
