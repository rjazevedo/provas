#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Gera Marca d'água em arquivo PDF"""

import csv
import os
import os.path
import string
import sys
import tempfile
import string

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import code128
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as rpImage
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def MarcaDAgua(s):
    c = canvas.Canvas(s + '.pdf', pagesize = A4)
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.setFont('Helvetica', 24)
    #c.rotate(45)
    for i in range(0, 21, 2):
        for j in range(0, 30):
            c.drawString((i + 0.5) * cm, j * cm, s)
    c.save()
    return



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Uso: {} numero'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    MarcaDAgua(sys.argv[1])

