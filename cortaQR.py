#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corta o retângulo do canto superior direito da imagem (QR-Code?)"""

from PIL import Image
from pyzbar.pyzbar import decode
import sys

if __name__ == '__main__':
    for arquivo in sys.argv[1:]:
        print(arquivo)
        img = Image.open(arquivo)
        w, h = img.size
        img = img.crop((int(0.6 * w), 0, w, int(0.4* h)))
        qr = decode(img)
        if len(qr) == 1:
            print(qr[0].data)
        else:
            img.save('crop-' + arquivo)

