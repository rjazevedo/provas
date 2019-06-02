#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corta o retângulo do canto superior direito da imagem (QR-Code?)"""

import cv2
from pyzbar.pyzbar import decode
from itertools import product
import sys
import numpy as np
import os
import imutils


def Mostra(imagem):
    display = cv2.resize(imagem, (480, 640))
    cv2.imshow('imagem', display)
    tecla = cv2.waitKey(0)
    if (chr(tecla) == 'q'):
        sys.exit(1)
    return

def image_generator(orig):
    orig = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
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
        # printDebug("blur={}, threshold={},kernel_size={},dilation={},erosion={}".format(z[0],z[1],z[2],z[3],z[4]))
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


def GeraImagens(image):
    # Tenta a imagem original
    yield(image)

    # Tenta borrar um pouco
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    yield(gray)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    yield(blurred)

    adapt = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    print('Threshold')
    yield (adapt)

    thresh = cv2.bitwise_not(cv2.threshold(adapt, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1])
    print('OTSU')
    yield(thresh)

    kernel = np.ones((3,3), np.uint8) 
    img_erosion = cv2.erode(adapt, kernel, iterations=1) 
    yield(img_erosion)

    img_dilation = cv2.dilate(img_erosion, kernel, iterations=1) 
    yield(img_dilation)

def Crop(image):
    x = image.shape
    h = x[0]
    w = x[1]
    xi = int(0.5 * w)
    yi = 0
    xf = w
    yf = int(0.5 * h)
    return image[yi:yf, xi:xf]

def AchaQR(img):
    # Mostra(img)
    qr = decode(img)
    if len(qr) == 1:
        return qr[0].data
    else:
        return '' 

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Uso:', sys.argv[0], '<lista de arquivos>')
        sys.exit(1)
    for arquivo in sys.argv[1:]:
        try:
            if not os.path.isfile(arquivo):
                continue
            img = cv2.imread(arquivo)
        except RuntimeError:
            continue
        
        if img is None:
            continue

        achou = False

        for image in image_generator(Crop(img)):
            qr = AchaQR(image)
            if len(qr) > 20:
                print(arquivo, qr)
                achou = True
                break

        if not achou:
            for image in image_generator(Crop(imutils.rotate_bound(img, 90))):
                qr = AchaQR(image)
                if len(qr) > 20:
                    print(arquivo, qr)
                    achou = True
                    break

        if not achou:
            for image in image_generator(Crop(imutils.rotate_bound(img, 180))):
                qr = AchaQR(image)
                if len(qr) > 20:
                    print(arquivo, qr)
                    achou = True
                    break

        if not achou:
            for image in image_generator(Crop(imutils.rotate_bound(img, 270))):
                qr = AchaQR(image)
                if len(qr) > 20:
                    print(arquivo, qr)
                    achou = True
                    break

        if not achou:
            print(arquivo, 'não reconhecido')

