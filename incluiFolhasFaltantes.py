#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Remove Pendências de Folhas Faltantes dos Polos incluindo folhas em branco"""
import os
import argparse
import csv
import sys
from utils import BuscaArquivos, LinhaProva, Arquivos2Dict
import shutil


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Inclui folhas em branco nas provas incompletas dos polos, removendo as pendências.')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com descrição de todas as provas (.csv)')
    parser.add_argument('-n', '--numeroPolo', type=str, required=True, help='Numero do polo a preencher as folhas ausentes (4 dígitos)')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Pasta com as provas')
    parser.add_argument('-t', '--teste', action='store_true', required=False, help='Testa a execução (não realiza as cópias nada)')

    folhaBranca = os.path.join(os.path.dirname(sys.argv[0]), 'folha-nao-digitalizada.png')

    args = parser.parse_args()

    arquivos = BuscaArquivos(args.provas, recursivo = True, tipo = '.png')
    entrada = Arquivos2Dict(arquivos)
    print(len(arquivos), 'arquivos presentes')

    provas = csv.reader(open(args.entrada))
    next(provas)
    provas = [LinhaProva(a) for a in provas]
    print(len(provas), 'provas a verificar')

    contagem = 0
    respostasBrancas = 0

    for prova in provas:
        if prova.polo == args.numeroPolo:
            for folha in prova.idPaginas():
                if not folha in entrada:
                    if args.teste:
                        print(folha)
                    else:
                        shutil.copyfile(folhaBranca, os.path.join(args.provas, folha + '.png'))
                    contagem += 1

            if prova.questoesObjetivas != 0:
                nomeArquivo = os.path.join(args.provas, prova.polo, prova.codigo + '-01.csv')
                if not os.path.isfile(nomeArquivo):
                    if args.teste:
                        print(nomeArquivo)
                    else:
                        respostasBranco = [[x, '_'] for x in range(1, prova.questoesObjetivas + 1)]
                        csv.writer(open(nomeArquivo, 'wt')).writerows(respostasBranco)
                    respostasBrancas += 1

    print(contagem, 'arquivos em branco distribuidos')
    print(respostasBrancas, 'respostas em branco distribuídas')

