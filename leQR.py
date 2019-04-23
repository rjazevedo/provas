#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corta o retângulo do canto superior direito da imagem (QR-Code?)"""

from PIL import Image
from pyzbar.pyzbar import decode
import sys

if __name__ == '__main__':
    for arquivo in sys.argv[1:]:
        img = Image.open(arquivo)
        qr = decode(img)
        if len(qr) == 1:
            print(arquivo, qr[0].data)
