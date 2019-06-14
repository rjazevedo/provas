#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Roda leitor de lista de presenca"""
import os
import argparse
import csv
import sys
from utils import BuscaArquivos, LinhaProva, Arquivos2Dict
import shutil

def QuebraNome(nome):
    campos = os.path.basename(nome).split('-')
    if len(campos) == 6:
        return campos
    else:
        return ['', '', '', '']


CMD='/home/provas/folhasProvas/presence/presence -c '

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Roda o scanner nos arquivos de respostas de múltipla escolha.')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com descrição de todas as provas (.csv)')
    parser.add_argument('-a', '--ausentes', type=str, required=True, help='Arquivo com as informações dos ausentes (.csv)')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Pasta com as provas')
    parser.add_argument('-t', '--teste', action='store_true', required=False, help='Testa a execução (não executa nada)')
    parser.add_argument('-f', '--forca', action='store_true', required=False, help='Força a execução mesmo já tendo executado antes')

    args = parser.parse_args()

    arquivos = BuscaArquivos(args.provas, recursivo = True, tipo = '.png')
    entrada = Arquivos2Dict(arquivos)
    print(len(arquivos), 'arquivos a verificar')

    provas = csv.reader(open(args.entrada))
    next(provas)
    provas = [LinhaProva(a) for a in provas]

    presencas = {}
    for p in provas:
        labelProva = p.LabelProva()
        if not labelProva in presencas:
            presencas[labelProva] = [[p.ra, p.nomeAluno]]
        else:
            presencas[labelProva].append([p.ra, p.nomeAluno])

    contagem = 0
    ausentes = []
    for p in presencas.keys():
        alunos = len(presencas[p])
        folha = 1
        pagina = 1

        while alunos != 0:
            if alunos > 20:
                quantidade = 20
                alunos -= 20
            else:
                quantidade = alunos
                alunos = 0

            arquivo = p + '-presenca-' + format(pagina, '02d')
            pagina += 1

            if arquivo in entrada:
                txtFile = os.path.join(os.path.dirname(entrada[arquivo]), 'result', os.path.basename(entrada[arquivo][:-4]) + '.txt')
                print('*', txtFile, '*')
                if os.path.isfile(entrada[arquivo]):
                    if args.forca or not os.path.isfile(txtFile):
                        if args.teste:
                            print(CMD,  quantidade, entrada[arquivo])
                        else:
                            os.system(CMD + ' ' + str(quantidade) + ' ' + entrada[arquivo])
                            if os.path.isfile(txtFile):
                                listaPresenca = [x[:-1].split('. ') for x in open(txtFile).readlines()]
                                campos = QuebraNome(txtFile)[0:4]

                                for linha in listaPresenca:
                                    aluno = presencas[p].pop(0)
                                    if linha[1] == 'Ausente':
                                        c = campos.copy()
                                        c.append(aluno.ra)
                                        ausentes.append(c)

                        contagem += 1

    print(contagem, 'arquivos processados')
    csv.writer(open(args.ausentes, 'wt')).writerows(ausentes)

