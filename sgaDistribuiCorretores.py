#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dada duas listas de corretores contendo a alocação de disciplina e a carga de trabalho, distribui
as correções de provas"""

###############################################
# Uso: sgaCorretores.py -a corretores.csv -c 38
#
# 38: é o calendário do bimestre 2019/2
#
# o arquivo dbpass.txt deve estar no diretório
#
# Corresponde à: CreateSubmissionsCorrectorsFromCSV
###############################################

from sqlalchemy import func
import os
import sys
import argparse
import db
import csv
import heapq

args = None
peso = 2 # Número de questões a corrigir por prova. Apesar de fazermos a alocação por prova, a contabilidade é sempre por questões.

####################
# Inicia Sessão 
####################
sess = db.Session()
sess.autoflush = True  # default


class Corretor:
    def __init__(self, disciplina, email, nome):
        self.nome = nome
        self.email = email
        self.passado = 0
        self.corrigidas = 0
        self.disciplinas = [disciplina]
        
    def __cmp__(self, other):
        """ Corretores serão ordenados pelo número de questões corrigidas"""
        return self.corrigidas - other.corrigidas
    
    def __lt__(self, other):
        return self.corrigidas < other.corrigidas
    
    def __gt__(self, other):
        return self.corrigidas > other.corrigidas
    
    def __eq__(self, other):
        return self.corrigidas == other.corrigidas
    
    def __repr__(self):
        return '{0} <{1}> ({2})'.format(self.nome, self.email, str(self.corrigidas))
    
class Disciplina:
    def __init__(self, sigla):
        self.sigla = sigla
        self.dbId = 0
        self.corretores = []
      
    
def AtribuiCorretores(arqCorretores, arqEstatisticas):
    if not os.path.isfile(arqCorretores):
        print('Arquivo não encontrado:', arqCorretores)
        return
  
    todosCorretores = {}
    todasDisciplinas = {}
    for [d, e, n] in csv.reader(open(arqCorretores)): # disciplina, email, nome
        if e not in todosCorretores:
            c = Corretor(d, e, n)
            todosCorretores[e] = c
            if d not in todasDisciplinas:
                disc = Disciplina(d)
                todasDisciplinas[d] = disc
                disc.corretores.append(c)
            else:
                todasDisciplinas[d].corretores.append(c)
        else:
            todosCorretores[e].disciplinas.append(d)
            if d not in todasDisciplinas:
                disc = Disciplina(d)
                todasDisciplinas[d] = disc
                disc.corretores.append(todosCorretores[e])
            else:
                todasDisciplinas[d].corretores.append(todosCorretores[e])
                
    if os.path.isfile(arqEstatisticas):
        for [e, p, c] in csv.reader(open(arqEstatisticas)):
            if e in todosCorretores:
                todosCorretores[e].passado = p
                todosCorretores[e].corrigidas = c
        
    for d in todasDisciplinas.keys():
        print(d)
        heapq.heapify(todasDisciplinas[d].corretores)
        print(todasDisciplinas[d].corretores)
  

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Associa corretores (internal_users) a provas dos alunos levando em conta a carga de trabalho de correção.')
    parser.add_argument('-c', '--corretores', type=str, required=True, help='Arquivo CSV com os emails dos corretores')
    parser.add_argument('-e', '--estatisticas', type=str , required=True, help='Arquivo CSV com as estatísticas de correção por corretor)')

    args = parser.parse_args()
    
    AtribuiCorretores(args.corretores, args.estatisticas)
