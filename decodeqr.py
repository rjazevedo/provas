#!/usr/local/bin/python3

from PIL import Image
from pyzbar.pyzbar import decode
import sys
import os

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: {} arquivos ...'.format(sys.argv[0]))
        sys.exit(1)

    for nome in sys.argv[1:]:
 #       print(nome)
        qr = decode(Image.open(nome))
        if len(qr) == 1:
            print(nome, ' -> ', qr[0].data) 
            os.rename(nome, str(qr[0].data)[2:-1] + '.png')
        else:
            print('Encontrei {} QRCodes'.format(len(qr)))


