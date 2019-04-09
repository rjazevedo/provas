#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Renomeia os arquivos baseado no QR-Code que existe dentro dele"""

from PIL import Image
from pyzbar.pyzbar import decode
import sys
import os
import argparse

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: {} arquivos ...'.format(sys.argv[0]))
        sys.exit(1)

    for nome in sys.argv[1:]:
 #       print(nome)
        img = Image.open(nome)
        qr = decode(img)
        print(qr)
        if len(qr) == 1:
            print(nome, ' -> ', qr[0].data).decode('utf-8') 
            os.rename(nome, str(qr[0].data)[2:-1] + '.png')
        else:
            qr = decode(img.rotate(90, expand=1))
            print(qr)
            print(nome, ' -> ' 'Encontrei {} QRCodes'.format(len(qr)))


