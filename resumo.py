#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Resumo das informações sobre as provas"""
import os
import argparse
import csv
import sys
from utils import BuscaArquivos, LinhaProva, Arquivos2Dict
import shutil


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resumo do status dos arquivos na pasta.')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com descrição de todas as provas (.csv)')
    parser.add_argument('-a', '--ausentes', type=str, required=True, help='Arquivo com as informações dos ausentes (.csv)')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Pasta com as provas')

    args = parser.parse_args()

    print('Lendo entrada...')

    pngs = BuscaArquivos(args.provas, recursivo = True, tipo = '.png')
    pngs = Arquivos2Dict(pngs)
    print(len(pngs), 'arquivos de folhas presentes (.PNG).')

    csvs = BuscaArquivos(args.provas, recursivo = True, tipo = '.csv')
    csvs = Arquivos2Dict(csvs)
    print(len(csvs), 'arquivos de leituras presentes (.CSV).')

    provas = csv.reader(open(args.entrada))
    next(provas)
    provas = [LinhaProva(a) for a in provas]
    print(len(provas), 'provas foram geradas para aplicação.')

    ausentes = csv.reader(open(args.ausentes))
    ausentes = ['-'.join(x) for x in ausentes]
    print(len(ausentes), 'cadernos de resposta estão marcadas como ausentes.')

    folhasFaltantes = 0
    provasCompletas = {}
    provasIncompletas = {}
    polosPendentes = {}

    print('Processando dados...')
    for prova in provas:
        for folha in prova.idPaginas():
            if not folha in pngs:
                folhasFaltantes += 1
                provasIncompletas[prova.codigo] = True
                polosPendentes[prova.polo] = True
        if not provasIncompletas[prova.codigo]:
            provasCompletas[prova.codigo] = True

    print(len(provasCompletas), 'provas completas.')
    print(folhasFaltantes, 'folhas faltantes.')
    print(len(provasIncompletas), 'provas incompletas.')
    print(len(polosPendentes), 'polos com pendências.')

