#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corta o retângulo do canto superior direito da imagem (QR-Code?)"""

import cv2
from pyzbar.pyzbar import decode
import sys
import numpy as np

def Mostra(imagem):
    display = cv2.resize(imagem, (480, 640))
    cv2.imshow('imagem', display)
    tecla = cv2.waitKey(0)
    if (chr(tecla) == 'q'):
        sys.exit(1)
    return

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
    w = x[0]
    h = x[1]
    # w, h = img.shape    
    # img = img.crop((int(0.6 * w), 0, w, int(0.4 * h)))
    # warped = warped[xi:xf, yi:yf]
    xi = int(0.5 * w)
    yi = 0
    xf = w
    yf = int(0.5 * h)
    return image[yi:yf, xi:xf]

if __name__ == '__main__':
    for arquivo in sys.argv[1:]:
        img = cv2.imread(arquivo)
        for image in GeraImagens(img):
            image = Crop(image)
            Mostra(image)
            qr = decode(image)
            if len(qr) == 1:
                print(arquivo, qr[0].data)
                break
        else:
            print(arquivo, 'não reconhecido')

