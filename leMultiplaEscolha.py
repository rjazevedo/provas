#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Lê as respostas das perguntas de múltipla escolha"""

# Based on https://www.pyimagesearch.com/2016/10/03/bubble-sheet-multiple-choice-scanner-and-test-grader-using-omr-python-and-opencv/

# import the necessary packages
from imutils.perspective import four_point_transform
from imutils import contours
from itertools import product
import numpy as np
import argparse
import imutils
import cv2
import csv
import sys
import math
import os
import scipy
import scipy.cluster.hierarchy as sch

# from sklearn.cluster import KMeans

debug = False
blue = (255, 0, 0)
red = (0, 0, 255)
green = (0, 255, 0)
MIN_RADIUS = 9
MAX_RADIUS = 14
EPSILON = 3

def printDebug(msg):
	return
	if debug:
		print(msg)


def confidence(a):
    dim=len(a)
    indexed_a=np.argsort(a)[::-1]
    best = indexed_a[0]
    second_best = indexed_a[1]
    D=scipy.zeros([dim,dim])
    # calculate distances
    for i in range(dim):
        for j in range(dim):
            D[i,j]=abs(a[i]-a[j])
    #links=sch.linkage(D,method="average")
    #links=sch.linkage(D,method="centroid")
    #links=sch.linkage(D,method="ward")
    links=sch.linkage(D,method="weighted")
    #links=sch.linkage(D,method="single")
    cdim=len(links)
    dist01=links[cdim-1][2] # distance singleton to last formed cluster
    #ret_conf=0.0
    ret_conf=dist01
    if dist01<80: # empirical value! 
        printDebug(' * bad1, not enough difference from singleton to cluster dist01={}, {}'.format(dist01,a))
        return -1
    if links[cdim-1][0]>=dim:
        # log(LOG,' * bad3, cluster singleton number is not that of an element {}'.format(a))
        printDebug(' * bad3, cluster singleton number is not that of an element {}'.format(a))
        return -1
    if best!=links[cdim-1][0]:
        # log(LOG,' * bad4, best is not the singleton element {}'.format(a))
        printDebug(' * bad4, best is not the singleton element {}'.format(a))
        return -1
    printDebug('********** accepted best={} dist01={} a={}'.format(a[best],dist01,a))
    return best


def Mostra(imagem):
	display = cv2.resize(imagem, (480, 640))
	cv2.imshow('imagem', display)
	tecla = cv2.waitKey(0)
	if (chr(tecla) == 'q'):
		sys.exit(1)
	return

def Distancia(p1, p2):
	return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1])  ** 2)

def EncontraRetangulo(imagem, docCnt):
	# define os extremos da imagem (cantos)
	(w, h, j) = imagem.shape
	topL = [0, h]
	topR = [w, h]
	bottomL = [0, 0]
	bottomR = [w, 0]

	# Coloca os pontos mais distantes possíveis
	imgTopL = bottomR
	imgTopR = bottomL
	imgBottomL = topR
	imgBottomR = topL

	distTL = Distancia(topL, imgTopL)
	distTR = Distancia(topR, imgTopR)
	distBL = Distancia(bottomL, imgBottomL)
	distBR = Distancia(bottomR, imgBottomR)

	for ponto in docCnt:
		p = ponto[0]
		d = Distancia(p, topL)
		if d < distTL:
			distTL = d
			imgTopL = p

		d = Distancia(p, topR)
		if d < distTR:
			distTR = d
			imgTopR = p

		d = Distancia(p, bottomL)
		if d < distBL:
			distBL = d
			imgBottomL = p

		d = Distancia(p, bottomR)
		if d < distBR:
			distBR = d
			imgBottomR = p

	docCnt = np.ndarray((4, 1, 2), dtype=int)
	docCnt[0][0] = imgTopL
	docCnt[1][0] = imgTopR
	docCnt[2][0] = imgBottomR
	docCnt[3][0] = imgBottomL

	return docCnt

def image_generator(orig):
    yield(orig)
    blur_values = (True,False)
    threshold_values = (False,True)
    kernel_size_values = (3,5)
    dilation_values = (0,2,1,0)
    erosion_values = (0,1,2,3)
    for z in product(blur_values,threshold_values,kernel_size_values,dilation_values,erosion_values):
        blur = z[0]
        threshold = z[1]
        kernel_size = z[2]
        dilation = z[3]
        erosion = z[4]
        printDebug("blur={}, threshold={},kernel_size={},dilation={},erosion={}".format(z[0],z[1],z[2],z[3],z[4]))
        image = orig.copy()
        if threshold:
            #thresh_val, thresh_img = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)
            #thresh_val, thresh_img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
            image = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,37,2)

        if blur:
            image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        if erosion > 0:
            kernel = np.ones((kernel_size,kernel_size), np.uint8)
            image = cv2.erode(image, kernel, iterations=erosion)
        if dilation > 0:
            kernel = np.ones((kernel_size,kernel_size), np.uint8)
            image = cv2.dilate(image, kernel, iterations=dilation)
        #show_image(image,'image.png',2)
        yield(image)

def get_contour_precedence(contour, cols):
    tolerance_factor = 10
    origin = cv2.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]


def AchaRetangulo(image, gray):
	edged = cv2.Canny(gray, 75, 200)
	# Mostra(image)

	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	docCnt = None

	#Mostra(image)
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
			# cv2.drawContours(gray, [approx], -1, red, 3)
			if len(approx) == 4:
				(x, y, w, h) = cv2.boundingRect(c)
				# print(x, y, w, h, w * h)
				if (1.5 < w / h < 1.7) and (w * h > 180000):
					if debug:
						cv2.drawContours(gray, [approx], -1, blue, 3)
						Mostra(gray)

					docCnt = approx
					paper = four_point_transform(gray, docCnt.reshape(4, 2))
					return paper
	# Mostra(gray)
	return None


def Mediana(v):
	v2 = sorted(v.copy())

	return v2[len(v2) // 2]


def AchaCentros(image):
	# thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
	circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 25,param1=40,param2=25,minRadius=MIN_RADIUS,maxRadius=MAX_RADIUS)

	if circles is None:
		return (0, [])

	circles = np.round(circles[0, :]).astype("int")
	circle_tuples = []

	for x,y,r in circles:
		circle_tuples.append((x,y,r))

	maxX = minX = maxY = minY = None
	for (x, y, r) in circle_tuples:
		if maxX == None:
			minX = x - r
			minY = y - r
			maxX = x + r
			maxY = y + r
			avgdY = r
			avgdX = r
		else:
			if x - r < minX:
				minX = x - r
			if y - r < minY:
				minY = y - r
			if x + r > maxX:
				maxX = x + r
			if y + r > maxY:
				maxY = y + r
			avgdY += 2 * r
			avgdX += 2 * r

	avgdY //= len(circle_tuples)
	avgdX //= len(circle_tuples)
	avgdY2 = avgdY // 2
	avgdX2 = avgdX // 2

	# Na horizontal, temos 5 bolinhas * avgdX largura + 4 * espacoX
	espacoX = (maxX - minX - 5 * avgdX) // 4

	# Na vertical, podemos ter 4 ou 6 questões * avgdY e 3 ou 5 espaços
	espacoY4 = (maxY - minY - 4 * avgdY) // 3
	espacoY6 = (maxY - minY - 6 * avgdY) // 5

	# as linhas abaixo tentam detectar o número de questões
	if espacoY4 > avgdY:
		espacoY = espacoY6
		questoes = 6
	else:
		espacoY = espacoY4
		questoes = 4

	if debug:
		print(questoes, 'questões detectadas')

	centros = []
	for i in range(0, questoes):
		centros.append([])
		for j in range(0, 5):
			centros[i].append((minX + j * avgdX + j * espacoX + avgdX2, minY + i * avgdY + i * espacoY + avgdY2, avgdX2))

	return (len(circle_tuples), centros)


def LeBolinhas(image, centros):

	# apply Otsu's thresholding method to binarize the warped
	# piece of paper
	thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

	# find contours in the thresholded image, then initialize
	# the list of contours that correspond to questions
	# cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# cnts = imutils.grab_contours(cnts)
	# questionCnts = []
	# maxX = maxY = minX = minY = None
	# bloco = 20
	# avgdY = 0
	# avgdX = 0
	# boundrect = []

	circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 25,param1=40,param2=25,minRadius=MIN_RADIUS,maxRadius=MAX_RADIUS)
	if circles is None:
		return (0, [])
	# 	circulos = len(circles[0])
	# 	# print(circulos, 'círculos')
	# 	if circulos != 20 and circulos != 30:
	# 		return (0, [])
	# 	elif circulos == 20:
	# 		questoes = 4
	# 	else:
	# 		questoes = 6
	# else:
	# 	return (0, [])
	
	circles = np.round(circles[0, :]).astype("int")
	# return tuples so that sort works as expected
	circle_tuples = []
	for x,y,r in circles:
		circle_tuples.append((x,y,r))

	if debug:
		print(circle_tuples)
	# answers = []
	# for i in range(linhas):
	# 	avalues = []
	# 	for j in range(0,5):
	# 		x, y, r = circle_tuples[i*5+j]
	# 		#print('draw circle',x,y,r)
	# 		#print('start={}, num={}, i={}, j={}, start+i+num*j*rows={}'.format(start,num,i,j,start+i+num*j*rows))
	# 		#print()
	# 		#output = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB) # may use it to show answers
	# 		#cv2.circle(output, (x, y), r, (255, 255, 255), 1)
	# 		#cv2.rectangle(output, (x-r-EPSILON, y-r-EPSILON),(x+r+EPSILON,y+r+EPSILON), (0, 0, 255), 1)
	# 		#cv2.imshow("output.png", output)
	# 		#cv2.waitKey(0)
	# 		crop = thresh[y-r-EPSILON:EPSILON+r+y,x-r-EPSILON:EPSILON+r+x]

	# 		h,w = crop.shape[:2]
	# 		avalues.append(int(np.sum(crop)/(h*w)))
	# 		print(avalues)
	# 		avalues.append(np.sum(crop))

	# 	#print(avalues)
	# 	# debug("%d" % (i+1))
	# 	best = confidence(avalues)
	# 	answers.append(best)
	# print(answers)

	# return (0, [])


	# loop over the contours
	# for c in cnts:
	# 	# compute the bounding box of the contour, then use the
	# 	# bounding box to derive the aspect ratio
	# 	(x, y, w, h) = cv2.boundingRect(c)
	# 	ar = w / float(h)

	# 	# in order to label the contour as a question, region
	# 	# should be sufficiently wide, sufficiently tall, and
	# 	# have an aspect ratio approximately equal to 1
	# 	if w >= bloco and h >= bloco and 0.8 <= ar <= 1.2:
	# 		questionCnts.append(c)
	# 		boundrect.append((x, y, w, h))
	# 		if debug:
	# 			cv2.drawContours(image, [c], -1, blue, 3)
	# 			Mostra(image)
	# 	else:
	# 		if debug:
	# 			cv2.drawContours(image, [c], -1, red, 3)
	# 			Mostra(image)

	# if len(questionCnts) == 0:
	# 	# print('Não encontrei marcas. Arquivo errado?')
	# 	return (0, [])


	# maxX = minX = maxY = minY = None
	# for (x, y, r) in circle_tuples:
	# 	if maxX == None:
	# 		minX = x - r
	# 		minY = y - r
	# 		maxX = x + r
	# 		maxY = y + r
	# 		avgdY = r
	# 		avgdX = r
	# 	else:
	# 		if x - r < minX:
	# 			minX = x - r
	# 		if y - r < minY:
	# 			minY = y - r
	# 		if x + r > maxX:
	# 			maxX = x + r
	# 		if y + r > maxY:
	# 			maxY = y + r
	# 		avgdY += 2 * r
	# 		avgdX += 2 * r

	# avgdY //= len(circle_tuples)
	# avgdX //= len(circle_tuples)
	# avgdY2 = avgdY // 2
	# avgdX2 = avgdX // 2

	# # Na horizontal, temos 5 bolinhas * avgdX largura + 4 * espacoX
	# espacoX = (maxX - minX - 5 * avgdX) // 4

	# # Na vertical, podemos ter 4 ou 6 questões * avgdY e 3 ou 5 espaços
	# espacoY4 = (maxY - minY - 4 * avgdY) // 3
	# espacoY6 = (maxY - minY - 6 * avgdY) // 5

	# # as linhas abaixo tentam detectar o número de questões
	# if espacoY4 > avgdY:
	# 	espacoY = espacoY6
	# 	questoes = 6
	# else:
	# 	espacoY = espacoY4
	# 	questoes = 4

	questoes = len(centros)
	if debug:
		print(questoes, 'questões detectadas')

	# print(minX, minY, maxX, maxY)
	# print(avgdY, avgdX)
	# print(len(questionCnts))
	# print(espacoX, espacoY, espacoY4, espacoY6)
	#questionCnts.sort(key = lambda x : get_contour_precedence(x, paper.shape[1]))

	# sort the question contours top-to-bottom, then initialize
	# the total number of correct answers
	#questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]

	# for c in questionCnts:
	# 	cv2.drawContours(paper, [c], -1, green, 3)
	# 	cv2.imshow('resultado', paper)
		
	# cv2.waitKey(0)

	# Mostra(thresh)
	for l in centros:
		for (x, y, r) in l:
			cv2.circle(thresh, (x, y), r, (0, 0, 0), 2)

	# Mostra(thresh)

	# Monta matriz de respostas com o número de questões e 5 bolinhas para cada
	matrizRespostas = np.zeros((questoes, 5), dtype=int)
	# print(matrizRespostas)
	limiar = 1000

	for (a, l) in enumerate(centros):
		for (b, (x, y, r)) in enumerate(l):
			crop = thresh[y-r-EPSILON:EPSILON+r+y,x-r-EPSILON:EPSILON+r+x]
			h,w = crop.shape[:2]
			matrizRespostas[a][b] = int(np.sum(crop)/(h*w))
			if debug:
				print(matrizRespostas[a][b])
				Mostra(crop)

	# for (x, y, r) in circle_tuples:
	# 	crop = thresh[y-r-EPSILON:EPSILON+r+y,x-r-EPSILON:EPSILON+r+x]
	# 	h,w = crop.shape[:2]
	# 	total = int(np.sum(crop)/(h*w))
	# 	if h * w // 4 < limiar:
	# 		limiar = h * w // 4
	# 	# if debug:
	# 	# 	print(total)
	# 	# 	Mostra(crop)

	# 	# construct a mask that reveals only the current
	# 	# "bubble" for the question
	# 	# mask = np.zeros(thresh.shape, dtype="uint8")
	# 	# cv2.drawContours(mask, [c], -1, 255, -1)

	# 	# apply the mask to the thresholded image, then
	# 	# count the number of non-zero pixels in the
	# 	# bubble area
	# 	# mask = cv2.bitwise_and(thresh, thresh, mask=mask)
	# 	# total = cv2.countNonZero(mask)
	# 	# (x, y, w, h) = cv2.boundingRect(c)
	# 	for (a, l) in enumerate(centros):
	# 		for (b, (cx, cy, raio)) in enumerate(l):
	# 			if abs(cx - x) < r and abs(cy - y) < r:
	# 				matrizRespostas[a][b] = total
	# 				# if debug:
	# 				# 	print('Centro', cy, cx, r)
	# 				break

	if debug:
		print('Matriz Resposta:', matrizRespostas)

	resposta = []
	for (i, l) in enumerate(matrizRespostas):
		c = confidence(l)
		if c >= 0:
			r = chr(c + 65)
		else:
			r = '_'
		resposta.append(r)
		# continue
		# # if debug:
		# # 	print(confidence(l))
		# # max = np.max(l)
		# # min = np.min(l)
		# # avg = np.average(l)
		# # med = Mediana(l)
		# r = ''
		# # if 0.7 * max > med : # Parece que temos um ou mais vencedores
		# for (j, n) in enumerate(l):
		# 	if n >= limiar:
		# 		r += chr(j + 65)
		# if len(r) > 1:
		# 	r = '+'
		# elif len(r) == 0:          # nada preenchido
		# 	r = '_'
		# TODO: Existe o caso de todas as questões marcadas com todas as opções que não é tratado.

		# resposta.append(r)

	if debug:
		print('Resposta:', resposta)

	# print(matrizRespostas)
	# print('Resposta:', resposta)

	return (len(circles), resposta)


def ContaRespostasValidas(respostas):
	i = 0
	for r in respostas:
		if r in 'ABCDE':
			i += 1

	return i

def ProcessaImagem(nome, saida):
	# load the image, convert it to grayscale, blur it
	# slightly, then find edges
	if not os.path.isfile(nome):
		return

	try:
		image = cv2.imread(arquivo)
	except RuntimeError:
		return 

	if image is None:
		return 

	image = cv2.resize(image, (1240, 1753))
	# Mostra(image)
	(h, w, j) = image.shape
	xi = int(0.1 * w)
	yi = int(0.35 * h)
	xf = int(0.9 * w)
	yf = int(0.75 * h)
	image = image[yi:yf, xi:xf]

	# Mostra(image)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	for img in image_generator(gray):
		paper = AchaRetangulo(image, img)

		if paper is not None and debug:
			(h, w) = paper.shape
			xi = int(0.3 * w)
			yi = int(0.3 * h)
			xf = int(0.7 * w)
			yf = int(0.7 * h)
			paper = warped = paper[yi:yf, xi:xf]
			Mostra(paper)
			print('Achou')
			break

	if paper is None:
		print('Não achei retângulo')
		return
	# # Mostra(gray)
	# blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	# # Mostra(blurred)
	# edged = cv2.Canny(blurred, 75, 200)
	# # Mostra(edged)

	# # find contours in the edge map, then initialize
	# # the contour that corresponds to the document

	# cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# cnts = imutils.grab_contours(cnts)
	# docCnt = None
	# cnts = [EncontraRetangulo(image, x) for x in cnts]
	# cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

	# # if debug:
	# # 	for c in cnts:
	# # 		cv2.drawContours(image, [c], -1, green, 3)
	# # 		Mostra(image)

	# if len(cnts) > 0:
	# 	docCnt = cnts[0]
	# 	if debug:
	# 		cv2.drawContours(image, [docCnt], -1, blue, 3)
	# 		Mostra(image)
	
	# ensure that at least one contour was found
	# if len(cnts) > 0:
	# 	# sort the contours according to their size in
	# 	# descending order
	# 	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

	# 	# loop over the sorted contours
	# 	for c in cnts:
	# 		# approximate the contour
	# 		peri = cv2.arcLength(c, True)
	# 		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	# 		print(len(c), len(approx))

	# 		if debug:
	# 			cv2.drawContours(image, [c], -1, blue, 3)
	# 			Mostra(image)

	# 		# if our approximated contour has four points,
	# 		# then we can assume we have found the paper
	# 		if len(approx) == 4:
	# 			docCnt = approx
	# 			break

	# print(type(docCnt), docCnt)

	# apply a four point perspective transform to both the
	# original image and grayscale image to obtain a top-down
	# birds eye view of the paper
	# warped = paper = four_point_transform(image, docCnt.reshape(4, 2))
	# warped = four_point_transform(gray, docCnt.reshape(4, 2))

	# Crop paper border to easily find the bubles inside
	#help(paper)

	# (w, h) = warped.shape
	# xi = int(0 + 0.1 * w)
	# yi = int(0 + 0.1 * h)
	# xf = int(w * 0.9)
	# yf = int(h * 0.9)
	# warped = warped[xi:xf, yi:yf]

	# (w, h) = paper.shape
	# xi = int(0 + 0.1 * w)
	# yi = int(0 + 0.1 * h)
	# xf = int(w * 0.9)
	# yf = int(h * 0.9)
	# paper = paper[xi:xf, yi:yf]

	centros = []
	nBolas = 0
	for img in image_generator(paper):
		(n, c) = AchaCentros(img)
		if n > nBolas:
			nBolas = n
			centros = c

	if len(centros) == 0:
		print('Não achei as bolinhas')

	resposta = []
	nRespostas = 0
	bolas = 0
	for img in image_generator(paper):
		(b, r) = LeBolinhas(img, centros)
		if b >= bolas:
			q = ContaRespostasValidas(r)
			if q > nRespostas:
				resposta = r
				nRespostas = q
				bolas = b

	# return

	# resposta = []
	
	# # each question has 5 possible answers, to loop over the
	# # question in batches of 5
	# for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
	# 	# sort the contours for the current question from
	# 	# left to right, then initialize the index of the
	# 	# bubbled answer
	# 	cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
	# 	bubbled = None
	# 	r = []

	# 	# loop over the sorted contours
	# 	for (j, c) in enumerate(cnts):
	# 		# construct a mask that reveals only the current
	# 		# "bubble" for the question
	# 		mask = np.zeros(thresh.shape, dtype="uint8")
	# 		cv2.drawContours(mask, [c], -1, 255, -1)
	
	# 		# apply the mask to the thresholded image, then
	# 		# count the number of non-zero pixels in the
	# 		# bubble area
	# 		mask = cv2.bitwise_and(thresh, thresh, mask=mask)
	# 		total = cv2.countNonZero(mask)
	# 		print(total)
	
	# 		# if the current total has a larger number of total
	# 		# non-zero pixels, then we are examining the currently
	# 		# bubbled-in answer
	# 		if bubbled is None or total > bubbled[0]:
	# 			bubbled = (total, j)

	# 		if total > 200:
	# 			r.append(chr(ord('a') + j))
	# 			color = (0, 0, 255)
	# 		else:
	# 			color = (255, 0, 0)

	# 	if len(r) == 1:
	# 		resposta.append(r[0])
	# 	elif len(r) > 1:
	# 		resposta.append('*')
	# 	else:
	# 		resposta.append('_')
		
	# 	# # initialize the contour color and the index of the
	# 	# # *correct* answer
	# 	# color = (0, 0, 255)
	# 	# k = ANSWER_KEY[q]
	
	# 	# # check to see if the bubbled answer is correct
	# 	# if k == bubbled[1]:
	# 	# 	color = (0, 255, 0)
	# 	# 	correct += 1
	
	# 	# # draw the outline of the correct answer on the test
	# 	# cv2.drawContours(paper, [cnts[k]], -1, color, 3)

	saida = csv.writer(open(saida, 'wt'))
	for i, r in enumerate(resposta):
		saida.writerow([i + 1, r])

	return resposta

if __name__ == '__main__':
	# construct the argument parse and parse the arguments

	# ProcessaImagem('20190427-0002-TAE501-P005-1500137-01.png')
	# ProcessaImagem('20190426-0107-LIN031-P001-1800222-01.png')
	# ProcessaImagem('p1-6.png')
	# ProcessaImagem('p2-6.png')
	# ProcessaImagem('p3-6.png')
	# sys.exit(0)

	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", nargs='+', required=True, help="path to the input image")
	ap.add_argument("-f", "--force", required=False, action='store_true', help="replace output file if it exists")
	ap.add_argument("-d", "--debug", required=False, action='store_true', help="debug image algorithm")
	args = vars(ap.parse_args())
	
	if args['debug']:
		debug = True

	quantidade = 0
	for arquivo in args['image']:
		saida = arquivo[:-3] + 'csv'
		if args['force'] or not os.path.isfile(saida):
			print(arquivo, ProcessaImagem(arquivo, saida))
			quantidade += 1

	print(quantidade, 'arquivos processados.')
