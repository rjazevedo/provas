#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corta o retângulo do canto superior direito da imagem (QR-Code?)"""

from PIL import Image
import sys

if __name__ == '__main__':
    for arquivo in sys.argv[1:]:
        img = Image.open(arquivo)
        w, h = img.size
        img = img.crop((int(0.75 * w), 0, w, int(0.25 * h)))
        img.save('crop-' + arquivo)

