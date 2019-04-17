#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Binariza uma imagem"""
from PIL import Image
import sys

img = Image.open(sys.argv[1])
thresh = int(sys.argv[2])
fn = lambda x : 255 if x > thresh else 0
r = img.convert('L').point(fn, mode='1')
r.save(sys.argv[3])
