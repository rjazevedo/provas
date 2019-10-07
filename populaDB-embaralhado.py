#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Popula DB com base nos arquivos de provas da Univesp"""

import csv
import sys
import argparse
import os
import random

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
        self.novo = False
        self.codigo = ''
        self.provaPolo = self.prova + '-' + self.polo
        self.GeraCodigo()
        return

    def GeraCodigo(self):
        self.codigo = self.dataStr + '-' + \
                      self.polo + '-' + self.disciplina + '-' + \
                      self.prova + '-' + self.ra

        return self.codigo

    def idProva(self):
        return self.disciplina + '-' + self.prova
    
    def idProvaPolo(self):
        return self.disciplina + '-' + self.provaPolo

    def EncontraArquivo(self, prefixo):
        arquivo = os.path.join(prefixo, self.polo, self.codigo)
        nFolhas = self.folhasDissertativas + 1
        retorno = []
        for i in range(1, nFolhas + 1):
            a = arquivo + '-' + format(i, '02d') + '.png'
            if os.path.isfile(a):
                retorno.append([self.disciplina, self.provaPolo, self.ra, i, a])
        return retorno
# Alterado por Guilherme em 14/8, 12:16
#        if len(retorno) == nFolhas:
#            return retorno
#        else: 
#            return []

class CorretorDisciplina:
    def __init__(self, nome, corretor):
        self.nome = nome
        self.proximo = -1
        self.lista = [corretor]

    def Inclui(self, corretor):
        self.lista.append(corretor)

    def Proximo(self):
        return random.choice(self.lista)
        # self.proximo += 1
        # return self.lista[self.proximo % len(self.lista)]

    def __str__(self):
        return self.nome + ': ' + str(self.lista)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Le arquivo de provas para popular o DB')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com a descrição das provas.csv')
    parser.add_argument('-b', '--basecorrecoes', type=str, required=False, help='Arquivo base das correções já gerado anteriormente')
    parser.add_argument('-c', '--corretores', type=str, required=True, help='Arquivos com mapeamento de corretores por disciplinas')
    parser.add_argument('-a', '--arquivos', type=str, required=True, help='Pasta dos arquivos de provas (comece com SGA)')
    parser.add_argument('-g', '--guias', type=str, required=True, help='Pasta dos arquivos dos guias de correção')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Pasta de saida')

    args = parser.parse_args()

    print('[populaDB] Lendo entrada...')
    entrada = list(csv.reader(open(args.entrada)))
    corretores = list(csv.reader(open(args.corretores)))

    if args.basecorrecoes != None:
        baseCorrecoes = list(csv.reader(open(args.basecorrecoes)))
    else:
        baseCorrecoes = []

    temCorretor = {}
    for base in baseCorrecoes:
        temCorretor[base[0] + base[1] + base[2]] = True

    print('[populaDB] Processando dados...')
    linhasProvas = [LinhaProva(x) for x in entrada[1:]]

    provas = {}
    for l in linhasProvas:
        provas[l.idProvaPolo()] = l

    saida = []
    questoes = []
    guias = []
    # Processa uma vez cada prova distinta. Estamos olhando as variações dos polos aqui também.
    for prova in sorted(provas.keys()):
        p = provas[prova]
        saida.append([p.disciplina, p.provaPolo, p.folhasDissertativas + 1])

        for q in range(1, p.questoesObjetivas + 1):
            if q < 5:
                questoes.append([p.disciplina, p.provaPolo, q, 'Objetiva', 1.5])
            else:
                questoes.append([p.disciplina, p.provaPolo, q, 'Objetiva', 2.0])
                
        if p.folhasDissertativas != 0:
            questoes.append([p.disciplina, p.provaPolo, p.questoesObjetivas + 1, 'Dissertativa', 2.0])
            questoes.append([p.disciplina, p.provaPolo, p.questoesObjetivas + 2, 'Dissertativa', 2.0])

        guia = os.path.join(args.guias, p.idProvaPolo() + '.pdf')
        if os.path.isfile(guia):
            guias.append([p.disciplina, p.provaPolo, p.folhasDissertativas + 1, guia])
        else:
            guia = os.path.join(args.guias, p.idProva() + '.pdf')
            if os.path.isfile(guia):
                guias.append([p.disciplina, p.prova, p.folhasDissertativas + 1, guia])
            else:
                print('[populaDB] Arquivo não encontrado:', guia)

    disciplinas = {}
    for c in corretores:
        if c[0] in disciplinas:
            disciplinas[c[0]].Inclui(c[1])
        else:
            disciplinas[c[0]] = CorretorDisciplina(c[0], c[1])

    folhas = []
    correcoes = []
    for f in linhasProvas:
        a = f.EncontraArquivo(args.arquivos)
        if len(a) != 0:
            if f.disciplina in disciplinas:
                if (f.disciplina + f.prova + f.ra) not in temCorretor:
                    correcoes.append([f.disciplina, f.provaPolo, f.ra, disciplinas[f.disciplina].Proximo()])
                    folhas.extend(a)
            else:
                print('[populaDB] Disciplina sem corretor:', f.disciplina)


    print('[populaDB] Gravando saída...')

    csv.writer(open(os.path.join(args.saida, 'provas.csv'), 'wt')).writerows(saida)
    csv.writer(open(os.path.join(args.saida, 'questoes.csv'), 'wt')).writerows(questoes)
    csv.writer(open(os.path.join(args.saida, 'guias.csv'), 'wt')).writerows(guias)
    csv.writer(open(os.path.join(args.saida, 'folhas.csv'), 'wt')).writerows(folhas)
    csv.writer(open(os.path.join(args.saida, 'correcoes.csv'), 'wt')).writerows(correcoes)

    sys.exit(0)


