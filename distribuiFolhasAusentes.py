#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Distribui folhas em branco para os ausentes"""
import os
import argparse
import csv
import sys
from utils import BuscaArquivos, LinhaProva, Arquivos2Dict
import shutil


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Roda o scanner nos arquivos de respostas de múltipla escolha.')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com descrição de todas as provas (.csv)')
    parser.add_argument('-a', '--ausentes', type=str, required=True, help='Arquivo com as informações dos ausentes (.csv)')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Pasta com as provas')
    parser.add_argument('-t', '--teste', action='store_true', required=False, help='Testa a execução (não executa nada)')
    parser.add_argument('-f', '--forca', action='store_true', required=False, help='Força a execução mesmo já tendo executado antes')

    folhaBranca = os.path.join(os.path.dirname(sys.argv[0]), 'folha-em-branco.png')

    args = parser.parse_args()

    arquivos = BuscaArquivos(args.provas, recursivo = True, tipo = '.png')
    entrada = Arquivos2Dict(arquivos)
    print(len(arquivos), 'arquivos presentes')

    provas = csv.reader(open(args.entrada))
    next(provas)
    provas = [LinhaProva(a) for a in provas]
    print(len(provas), 'provas a verificar')

    ausentes = csv.reader(open(args.ausentes))
    ausentes = ['-'.join(x) for x in ausentes]
    print(len(ausentes), 'ausentes a processar')

    contagem = 0

    for prova in provas:
        if  prova.codigo in ausentes:
            for folha in prova.idPaginas():
                if not folha in entrada:
                    folha += '.png'
                    shutil.copyfile(folhaBranca, os.path.join(args.provas, folha))
                    contagem += 1

    print(contagem, 'arquivos em branco distribuidos')

