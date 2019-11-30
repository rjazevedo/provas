#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from odf.opendocument import OpenDocumentText, load
from odf.style import Style, TextProperties, ParagraphProperties, ListLevelProperties
from odf.text import P, List, ListItem, ListStyle, ListLevelStyleBullet

MAXIMO_POLOS = 337

def TamanhoListas(arquivoODF):
    doc = load(arquivoODF)
    resposta = []
    listas = doc.getElementsByType(List)
    for l in listas:
        resposta.append(len(l.getElementsByType(ListItem)))
    return resposta

def ListaListas(doc):
    contagem = 1
    listas = doc.getElementsByType(List)
    for l in listas:
        print('*****', contagem, '*****')
        contagem += 1
        el = l.getElementsByType(ListItem)
        # if len(el) == 5:
        for e in el:
            print('*', e)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: listaQuestoes.py <prova.odt>')
        sys.exit(1)

    for arquivo in sys.argv[1:]:
        print(arquivo)
        ListaListas(load(arquivo))