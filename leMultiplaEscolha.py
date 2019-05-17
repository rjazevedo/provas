#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Lê as respostas das perguntas de múltipla escolha"""

# Based on https://www.pyimagesearch.com/2016/10/03/bubble-sheet-multiple-choice-scanner-and-test-grader-using-omr-python-and-opencv/

# import the necessary packages
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import csv
import sys
 
def get_contour_precedence(contour, cols):
    tolerance_factor = 10
    origin = cv2.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]

def ProcessaImagem(nome):
	# load the image, convert it to grayscale, blur it
	# slightly, then find edges
	image = cv2.imread(nome)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(blurred, 75, 200)

	# find contours in the edge map, then initialize
	# the contour that corresponds to the document

	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	docCnt = None
	
	# ensure that at least one contour was found
	if len(cnts) > 0:
		# sort the contours according to their size in
		# descending order
		cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
	
		# loop over the sorted contours
		for c in cnts:
			# approximate the contour
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	
			# if our approximated contour has four points,
			# then we can assume we have found the paper
			if len(approx) == 4:
				docCnt = approx
				break

	# apply a four point perspective transform to both the
	# original image and grayscale image to obtain a top-down
	# birds eye view of the paper
	paper = four_point_transform(image, docCnt.reshape(4, 2))
	warped = four_point_transform(gray, docCnt.reshape(4, 2))


	# Crop paper border to easily find the bubles inside
	#help(paper)

	(w, h) = warped.shape
	xi = int(0 + 0.1 * w)
	yi = int(0 + 0.1 * h)
	xf = int(w * 0.9)
	yf = int(h * 0.9)
	warped = warped[xi:xf, yi:yf]

	(w, h, j) = paper.shape
	xi = int(0 + 0.1 * w)
	yi = int(0 + 0.1 * h)
	xf = int(w * 0.9)
	yf = int(h * 0.9)
	paper = paper[xi:xf, yi:yf]

	# apply Otsu's thresholding method to binarize the warped
	# piece of paper
	thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

	# find contours in the thresholded image, then initialize
	# the list of contours that correspond to questions
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	questionCnts = []
	blue = (255, 0, 0)
	red = (0, 0, 255)
	green = (0, 255, 0)
	maxX = maxY = minX = minY = None
	bloco = 20
	avgdY = 0
	avgdX = 0
	boundrect = []

	# loop over the contours
	for c in cnts:
		# compute the bounding box of the contour, then use the
		# bounding box to derive the aspect ratio
		(x, y, w, h) = cv2.boundingRect(c)
		ar = w / float(h)
	
		# in order to label the contour as a question, region
		# should be sufficiently wide, sufficiently tall, and
		# have an aspect ratio approximately equal to 1
		if w >= bloco and h >= bloco and ar >= 0.8 and ar <= 1.2:
			questionCnts.append(c)
			boundrect.append((x, y, w, h))
		# 	cv2.drawContours(paper, [c], -1, blue, 3)
		# 	cv2.imshow('resultado', paper)
		# 	cv2.waitKey(0)
		# else:
		# 	cv2.drawContours(paper, [c], -1, red, 3)
		# 	cv2.imshow('resultado', paper)
		# 	cv2.waitKey(0)

	for (x, y, w, h) in boundrect:
		if maxX == None:
			minX = x
			minY = y
			maxX = x + w
			maxY = y + h
			avgdY = h
			avgdX = w
		else:
			if x < minX:
				minX = x
			if y < minY:
				minY = y
			if x + w > maxX:
				maxX = x + w
			if y + h > maxY:
				maxY = y + h
			avgdY += h
			avgdX += w

	avgdY //= len(questionCnts)
	avgdX //= len(questionCnts)
	print(minX, minY, maxX, maxY)
	print(avgdY, avgdX)
	print(len(questionCnts))
	questionCnts.sort(key = lambda x : get_contour_precedence(x, paper.shape[1]))

	# sort the question contours top-to-bottom, then initialize
	# the total number of correct answers
	#questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]


	# for c in questionCnts:
	# 	cv2.drawContours(paper, [c], -1, green, 3)
	# 	cv2.imshow('resultado', paper)
		
	# cv2.waitKey(0)

	sys.exit(0)

	resposta = []
	
	# each question has 5 possible answers, to loop over the
	# question in batches of 5
	for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
		# sort the contours for the current question from
		# left to right, then initialize the index of the
		# bubbled answer
		cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
		bubbled = None
		r = []

		# loop over the sorted contours
		for (j, c) in enumerate(cnts):
			# construct a mask that reveals only the current
			# "bubble" for the question
			mask = np.zeros(thresh.shape, dtype="uint8")
			cv2.drawContours(mask, [c], -1, 255, -1)
	
			# apply the mask to the thresholded image, then
			# count the number of non-zero pixels in the
			# bubble area
			mask = cv2.bitwise_and(thresh, thresh, mask=mask)
			total = cv2.countNonZero(mask)
			print(total)
	
			# if the current total has a larger number of total
			# non-zero pixels, then we are examining the currently
			# bubbled-in answer
			if bubbled is None or total > bubbled[0]:
				bubbled = (total, j)

			if total > 200:
				r.append(chr(ord('a') + j))
				color = (0, 0, 255)
			else:
				color = (255, 0, 0)

		if len(r) == 1:
			resposta.append(r[0])
		elif len(r) > 1:
			resposta.append('*')
		else:
			resposta.append('_')
		
		# # initialize the contour color and the index of the
		# # *correct* answer
		# color = (0, 0, 255)
		# k = ANSWER_KEY[q]
	
		# # check to see if the bubbled answer is correct
		# if k == bubbled[1]:
		# 	color = (0, 255, 0)
		# 	correct += 1
	
		# # draw the outline of the correct answer on the test
		# cv2.drawContours(paper, [cnts[k]], -1, color, 3)

	saida = csv.writer(open(nome[:-3] + 'csv', 'wt'))
	for i, r in enumerate(resposta):
		saida.writerow([i + 1, r])



if __name__ == '__main__':
	# construct the argument parse and parse the arguments

	ProcessaImagem('20190427-0002-TAE501-P005-1500137-01.png')
	ProcessaImagem('20190418-0002-AAG001-P002-1705829-01.png')
	sys.exit(0)

	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", nargs='+', required=True, help="path to the input image")
	args = vars(ap.parse_args())
	
	quantidade = 0
	for arquivo in args['image']:
		print(arquivo)
		ProcessaImagem(arquivo)
		quantidade += 1

	print(quantidade, 'arquivos processados.')
