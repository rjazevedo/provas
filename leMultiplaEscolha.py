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
import math
# from sklearn.cluster import KMeans

debug = False

def Mostra(imagem):
	 display = cv2.resize(imagem, (480, 640))
	 cv2.imshow('imagem', display)
	 cv2.waitKey(0)
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

	blue = (255, 0, 0)
	red = (0, 0, 255)
	green = (0, 255, 0)

	# find contours in the edge map, then initialize
	# the contour that corresponds to the document

	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	docCnt = None
	cnts = [EncontraRetangulo(image, x) for x in cnts]
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

	if len(cnts) > 0:
		docCnt = EncontraRetangulo(image, cnts[0])
		if debug:
			cv2.drawContours(image, [docCnt], -1, blue, 3)
			Mostra(image)
	
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
			if debug:
				cv2.drawContours(paper, [c], -1, blue, 3)
				cv2.imshow('resultado', paper)
				cv2.waitKey(0)
		else:
			if debug:
				cv2.drawContours(paper, [c], -1, red, 3)
				cv2.imshow('resultado', paper)
				cv2.waitKey(0)

	if len(questionCnts) == 0:
		print('Não encontrei marcas. Arquivo errado?')
		return

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
	avgdY2 = avgdY // 2
	avgdX2 = avgdX // 2

	# Na horizontal, temos 5 bolinhas * avgdX largura + 4 * espacoX
	espacoX = (maxX - minX - 5 * avgdX) // 4

	# Na vertical, podemos ter 4 ou 6 questões * avgdY e 3 ou 5 espaços
	espacoY4 = (maxY - minY - 4 * avgdY) // 3
	espacoY6 = (maxY - minY - 6 * avgdY) // 5
	if espacoY4 > avgdY:
		espacoY = espacoY6
		questoes = 6
	else:
		espacoY = espacoY4
		questoes = 4

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

	# Monta matriz de respostas com o número de questões e 5 bolinhas para cada
	matrizRespostas = np.zeros((questoes, 5), dtype=int)
	# print(matrizRespostas)
	centros = []
	for i in range(0, questoes):
		centros.append([])
		for j in range(0, 5):
			centros[i].append((minX + j * avgdX + j * espacoX + avgdX2, minY + i * avgdY + i * espacoY + avgdY2))

	# print(centros)
	# print(len(questionCnts))
	# print(matrizRespostas)

	for (i, c) in enumerate(questionCnts):
		# construct a mask that reveals only the current
		# "bubble" for the question
		mask = np.zeros(thresh.shape, dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)

		# apply the mask to the thresholded image, then
		# count the number of non-zero pixels in the
		# bubble area
		mask = cv2.bitwise_and(thresh, thresh, mask=mask)
		total = cv2.countNonZero(mask)
		(x, y, w, h) = cv2.boundingRect(c)
		for (a, l) in enumerate(centros):
			for (b, (cx, cy)) in enumerate(l):
				if abs(cx - (x + w // 2)) < avgdX2 and abs(cy - (y + h // 2)) < avgdY2:
					matrizRespostas[a][b] = total

	# print(matrizRespostas)
	resposta = []
	for (i, l) in enumerate(matrizRespostas):
		max = np.max(l)
		min = np.min(l)
		avg = np.average(l)
		r = ''
		if max - avg > 100: # Parece que temos um ou mais vencedores
			for (j, n) in enumerate(l):
				if n > avg + 100:
					r += chr(j + 65)
			if len(r) > 1:
				r = '+'
		elif avg > 300: # todos muito altos
			r = '+'
		else:           # nada preenchido
			r = '_'

		resposta.append(r)

	print(resposta)

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

	saida = csv.writer(open(nome[:-3] + 'csv', 'wt'))
	for i, r in enumerate(resposta):
		saida.writerow([i + 1, r])



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
	ap.add_argument("-d", "--debug", required=False, action='store_true', help="debug image algorithm")
	args = vars(ap.parse_args())
	
	if args['debug']:
		debug = True

	quantidade = 0
	for arquivo in args['image']:
		print(arquivo)
		ProcessaImagem(arquivo)
		quantidade += 1

	print(quantidade, 'arquivos processados.')
