#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corta o retângulo do canto superior direito da imagem (QR-Code?)"""

import cv2
from pyzbar.pyzbar import decode
import sys

def GeraImagens(image):
    # Tenta a imagem original
    yield(image)

    # Tenta borrar um pouco
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    yield(gray)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    yield(blurred)

    adapt = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    yield (adapt)

    thresh = cv2.threshold(adapt, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    yield(thresh)


if __name__ == '__main__':
    for arquivo in sys.argv[1:]:
        # i = 0
        img = cv2.imread(arquivo)
        for image in GeraImagens(img):
            # print(i)
            # i += 1
            qr = decode(image)
            if len(qr) == 1:
                print(arquivo, qr[0].data)
                break

