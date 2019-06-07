#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corrige questões de Múltipla Escolha"""

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
        self.novo = False
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

    def LeNotas(self, prefixo):
        arquivo = os.path.join(prefixo, self.polo, self.codigo + '-01.csv')
        if os.path.isfile(arquivo):
            notas = list(csv.reader(open(arquivo)))
            if len(notas) < 4:
                return []
            return notas
        return []

class Gabarito:
    def __init__(self, campos):
        self.disciplina = campos[0]
        self.prova = campos[1]
        self.nQuestoes = int(campos[2])
        self.respostas = campos[3:(self.nQuestoes + 3)]

    def Nome(self):
        return self.disciplina + self.prova

    def Verifica(self, respostas):
        if len(respostas) == self.nQuestoes:
            for linha in respostas:
                if len(linha) != 2:
                    return False
            return True
        else:
            return False
        
    def Comentario(self, questao, resposta):
        if self.respostas[questao - 1] == resposta:
            return 'Resposta Correta (gabarito = ' + self.respostas[questao - 1] + ')'
        elif resposta == '_':
            return 'Resposta em branco (gabarito = ' + self.respostas[questao - 1] + ')'
        elif resposta == '+':
            return 'Múltiplas respostas lidas (gabarito = ' + self.respostas[questao - 1] + ')'
        else:
            return 'Aluno respondeu errado (' + resposta + ') (gabarito = ' + self.respostas[questao - 1] + ')'

    def Nota(self, questao, resposta):
        if self.nQuestoes < questao:
            print('Questão fora do intervalo de respostas:', self.disciplina, self.prova, questao)
            sys.exit(1)

        if self.respostas[questao - 1] == resposta:
            return 10
        else:
            return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Corrige questões de Múltipla Escolha')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com a descrição das provas.csv')
    parser.add_argument('-g', '--gabarito', type=str, required=False, help='Gabarito de todas as provas a serem corrigidas')
    parser.add_argument('-a', '--arquivos', type=str, required=True, help='Pasta dos arquivos de provas com as questões lidas')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Arquivo de saída com as notas')

    args = parser.parse_args()

    print('Lendo entrada...')
    entrada = list(csv.reader(open(args.entrada)))
    gabarito = list(csv.reader(open(args.gabarito)))[1:] # Pula cabeçalho

    print('Processando dados...')
    linhasProvas = [LinhaProva(x) for x in entrada[1:]]

    gabaritos = {}
    for l in gabarito:
        g = Gabarito(l)
        gabaritos[g.Nome()] = g

    notas = []
    quantidade = 0
    semGabarito = 0
    semResposta = 0
    divergencia = 0
    for p in linhasProvas:
        respostas = p.LeNotas(args.arquivos)
        if len(respostas) != 0:
            token = p.disciplina + p.prova
            if token not in gabaritos:
                print('Gabarito não encontrado:', p.disciplina, p.prova)
                semGabarito += 1
                continue
            g = gabaritos[token]
            if g.Verifica(respostas):
                for i in range(0, g.nQuestoes):
                    q = int(respostas[i][0])
                    r = respostas[i][1]
                    notas.append([p.disciplina, p.prova, p.ra, q, g.Nota(q, r), g.Comentario(q, r)])
                    quantidade += 1
            else:
                print('Divergência de tamanho entre arquivo de respostas e gabarito:', p.codigo)
                divergencia += 1
        else:
            print('Não achei o arquivo com respostas:', p.codigo)
            semResposta += 1

    print(quantidade, 'folhas corrigidas.')
    print(semGabarito, 'provas sem gabarito.')
    print(semResposta, 'sem arquivo de resposta.')
    print(divergencia, 'divergências entre tamanho de arquivo.')
    print('Gravando saída...')

    csv.writer(open('notas.csv', 'wt')).writerows(notas)



