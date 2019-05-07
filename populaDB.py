#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Popula DB com base nos arquivos de provas da Univesp"""

import csv
import sys
import argparse
import os

# Cabeçalho
# 0 Nome
# 1 RA
# 2 Cod Polo
# 3 Polo
# 4 Data
# 5 Curso
# 6 Turma
# 7 Bimestre
# 8 Codigo Discpl
# 9 Disciplina
# 10 Variante
# 11 Objetivas
# 12 Dissertativas

def DataInvertida(dataStr):
    return dataStr[6:10] + dataStr[3:5] + dataStr[0:2]


class LinhaProva:
    def __init__(self, campos):
        self.nomeAluno = campos[0]
        self.ra = campos[1]
        self.polo = campos[2]
        self.nomePolo = campos[3]
        self.data = campos[4]
        self.curso = campos[5]
        self.turma = campos[6]
        self.bimestre = campos[7]
        self.disciplina = campos[8]
        self.nomeDisciplina = campos[9]
        self.prova = campos[10]
        self.questoesObjetivas = int(campos[11])
        self.folhasDissertativas = int(campos[12])
        self.dataStr = DataInvertida(self.data)
        self.codigo = ''
        self.GeraCodigo()
        return

    def GeraCodigo(self):
        self.codigo = self.dataStr + '-' + \
                      self.polo + '-' + self.disciplina + '-' + \
                      self.prova + '-' + self.ra

        return self.codigo

    def idProva(self):
        return self.disciplina + '-' + self.prova

    def EncontraArquivo(self, prefixo):
        arquivo = os.path.join(prefixo, self.polo, self.codigo)
        nFolhas = self.folhasDissertativas + 1
        retorno = []
        for i in range(1, nFolhas + 1):
            a = arquivo + '-' + format(i, '02d') + '.png'
            if os.path.isfile(a):
                retorno.append([self.disciplina, self.prova, self.ra, i, a])
        if len(retorno) == nFolhas:
            return retorno
        else: 
            return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Le arquivo de provas para popular o DB')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com a descrição das provas.csv')
    parser.add_argument('-a', '--arquivos', type=str, required=True, help='Pasta dos arquivos de provas')
    parser.add_argument('-g', '--guias', type=str, required=True, help='Pasta dos arquivos dos guias de correção')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Pasta de saida')
    

    args = parser.parse_args()

    print('Lendo entrada...')
    entrada = list(csv.reader(open(args.entrada)))

    linhasProvas = [LinhaProva(x) for x in entrada[1:]]

    provas = {}
    for l in linhasProvas:
        provas[l.idProva()] = l

    print('Processando dados...')
    saida = []
    questoes = []
    guias = []
    for prova in sorted(provas.keys()):
        p = provas[prova]
        saida.append([p.disciplina, p.prova, p.folhasDissertativas + 1])
        for q in range(1, p.questoesObjetivas + 1):
            questoes.append([p.disciplina, p.prova, q, 'Objetiva', 0.0])
        if p.folhasDissertativas != 0:
            questoes.append([p.disciplina, p.prova, p.questoesObjetivas + 1, 'Dissertativa', 0.0])
            questoes.append([p.disciplina, p.prova, p.questoesObjetivas + 2, 'Dissertativa', 0.0])

        guia = os.path.join(args.guias, p.idProva() + '.pdf')
        if os.path.isfile(guia):
            guias.append([p.disciplina, p.prova, guia])
        else:
            print('Arquivo não encontrado:', guia)

    folhas = []
    for f in linhasProvas:
        a = f.EncontraArquivo(args.arquivos)
        folhas.extend(a)

    print('Gerando saída...')

    csv.writer(open(os.path.join(args.saida, 'provas.csv'), 'wt')).writerows(saida)
    csv.writer(open(os.path.join(args.saida, 'questoes.csv'), 'wt')).writerows(questoes)
    csv.writer(open(os.path.join(args.saida, 'guiasCorrecao.csv'), 'wt')).writerows(guias)
    csv.writer(open(os.path.join(args.saida, 'folhas.csv'), 'wt')).writerows(folhas)

    sys.exit(0)


