#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Renomeia os arquivos baseado no QR-Code que existe dentro dele"""

import cv2
import imutils
from pyzbar.pyzbar import decode
import sys
import os
import argparse
import shutil

args = None
contagem = 0

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

    rotated = imutils.rotate_bound(image, 90)
    yield(rotated)

    rotated = imutils.rotate_bound(image, 180)
    yield(rotated)

    rotated = imutils.rotate_bound(image, 270)
    yield(rotated)


def Mostra(imagem):
    display = cv2.resize(imagem, (480, 640))
    cv2.imshow('imagem', display)
    tecla = cv2.waitKey(0)
    if (chr(tecla) == 'q'):
        sys.exit(1)
    return

def AchaQR(img):
    x = img.shape
    w = x[0]
    h = x[1]
    # w, h = img.shape    
    # img = img.crop((int(0.6 * w), 0, w, int(0.4 * h)))
    # warped = warped[xi:xf, yi:yf]
    xi = int(0.5 * w)
    yi = 0
    xf = w
    yf = int(0.5 * h)
    img = img[yi:yf, xi:xf]
    # Mostra(img)
    qr = decode(img)
    if len(qr) == 1:
        return qr[0].data
    else:
        return '' 

def Binariza(img, thresh = 200):
    fn = lambda x : 255 if x > thresh else 0
    return img.convert('L').point(fn, mode='1')


def DecodificaArquivo(arquivo, destino):
    if not os.path.isfile(arquivo):
        return False

    image = cv2.imread(arquivo)
    # i = 0
    for img in GeraImagens(image):
        # print(i)
        # i += 1
        qr = AchaQR(img)
        if qr != '':
            break

    # Testa a imagem binarizada
    # if qr == '': 
    #     qr = AchaQR(Binariza(img))

    # Testa as 3 rotações possíveis caso não tenha achado ainda
    # if qr == '':
    #     for _ in range(0, 3):
    #         img = img.rotate(90, expand = 1)
    #         qr = AchaQR(img)
    #         if qr != '':
    #             break

    if qr != '':
        nomeArquivo = os.path.join(destino, os.path.basename(str(qr)[2:-1]) + '.png')
        if nomeArquivo[0:4] != 'http':
            cv2.imwrite(nomeArquivo, img)
        os.remove(arquivo)
        return True

    return False


def IncrementaContagem(contagem = 0):
    pngFile = os.path.join(args.refugo, '{:010d}'.format(contagem) + '.png')
    jpgFile = os.path.join(args.refugo, '{:010d}'.format(contagem) + '.jpg')
    while os.path.isfile(pngFile) or os.path.isfile(jpgFile):
        contagem += 1
        pngFile = os.path.join(args.refugo, '{:010d}'.format(contagem) + '.png')
        jpgFile = os.path.join(args.refugo, '{:010d}'.format(contagem) + '.jpg')
    return contagem


def MoveRefugo(arquivo, contagem):
    contagem = IncrementaContagem()
    if arquivo.endswith('.png') or arquivo.endswith('.PNG'):
        shutil.move(arquivo, os.path.join(args.refugo, '{:010d}'.format(contagem) + '.png'))
        contagem += 1
    elif arquivo.endswith('.jpg') or arquivo.endswith('.JPG'):
        shutil.move(arquivo, os.path.join(args.refugo, '{:010d}'.format(contagem) + '.jpg'))
        contagem += 1
    return contagem

def BuscaArquivos(p):
    resposta = []
    for arquivo in os.scandir(p):
        if not arquivo.name.startswith('.'):
            if arquivo.is_file():
                resposta.append(os.path.join(p, arquivo.name))
            elif arquivo.is_dir():
                resposta.extend(BuscaArquivos(os.path.join(p, arquivo.name)))

    return resposta


def QuebraPDF(arquivo):
    contagem = 0
    apagar = BuscaArquivos(args.trabalho)
    for a in apagar:
        contagem = MoveRefugo(a, contagem)
    print('==> Separando as folhas do PDF')
    os.system('convert -density 150 -background white "' + arquivo + '" ' + os.path.join(args.trabalho, 'a.png'))
    lista = BuscaArquivos(args.trabalho)
    return lista
    

def ProcessaArquivos(listaArquivos, copiar):
    contagem = 0
    for nome in listaArquivos:
        print('=>', nome)
        if nome.endswith('.jpg') or nome.endswith('.JPG'):
            destino = os.path.join(args.trabalho, 'tmp.jpg')
            if copiar:
                shutil.copyfile(nome, destino)
                nome = destino
            if not DecodificaArquivo(nome, args.saida):
                print('==> Refugo: ' + nome)
                contagem = MoveRefugo(nome, contagem)
        elif nome.endswith('.png') or nome.endswith('.PNG'):
            destino = os.path.join(args.trabalho, 'tmp.png')
            if copiar:
                shutil.copyfile(nome, destino)
                nome = destino
            if not DecodificaArquivo(nome, args.saida):
                print('==> Refugo: ' + nome)
                contagem = MoveRefugo(nome, contagem)
        elif nome.endswith('.pdf') or nome.endswith('.PDF'):
            lista = QuebraPDF(nome)
            ProcessaArquivos(lista, copiar = False)
        else:
            print('==> Arquivo descartado ' + nome)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converte arquivos de provas em folhas individuais identificadas')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Pasta de entrada')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Pasta de saida')
    parser.add_argument('-t', '--trabalho', type=str, required=True, help='Pasta de trabalho')
    parser.add_argument('-r', '--refugo', type=str, required=True, help='Pasta de refugo')

    args = parser.parse_args()

    listaArquivos = BuscaArquivos(args.entrada)
    ProcessaArquivos(listaArquivos, copiar = True)
    

    # for nome in sys.argv[1:]:
    #     print(nome)
    #     DecodificaArquivo(nome)
        # img = Image.open(nome)
        # w, h = img.size
        # img = img.crop((int(0.75 * w), 0, w, int(0.25 * h)))
        # #img.show()

        # qr = decode(img)
        # print(qr)
        # if len(qr) == 1:
        #     print(nome, ' -> ', qr[0].data)
        #     os.rename(nome, str(qr[0].data)[2:-1] + '.png')
        # else:
        #     qr = decode(img.rotate(90, expand=1))
        #     print(qr)
        #     print(nome, ' -> ' 'Encontrei {} QRCodes'.format(len(qr)))


