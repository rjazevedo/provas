#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Remove Corretor Duplicado"""

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
import json

args = None

offer_types = { 'regular': 1, 'dp': 2, 'exam': 1 } #acrescentado o exam

####################
# Inicia Sessão 
####################
sess = db.Session()
sess.autoflush = True  # default


def erro( str ):
    print( "Erro: " + str )

def RemoveDuplicado(calendario, tipo):
    """ Remove corretores duplicados para uma mesma prova """
        
    # Para cada Activity Record Submission (atividade que precisa de avaliação)
    todasProvas = sess.query(db.ActivityRecordSubmissions)[-1000:]
    
    for prova in todasProvas:
        corretores = [x for x in prova.correctors if x.role == 'grader']
        
        if len(corretores) <= 1:
            continue
          
        print('-----')
        print(prova, len(corretores))
        # Trata separadamente os casos corrigidos dos não corrigidos
        if len(prova.activity_test.questions) == len(prova.corrections):
            # Prova corrigida, mantem o(s) corretores que corrigiram
            corrigiram = {}
            for x in prova.corrections:
              corrigiram[x.corrector_data.get('corrector_id', 0)] = True
              
            for c in corretores:
                if not c.internal_user_id in corrigiram:
                    print('Corrigida. Deveria apagar:', c.internal_user)
          
        else:
            # Prova não corrigida, mantem o primeiro corretor
            for c in corretores[1:]:
                print('Não corrigida. Deveria apagar:', c.internal_user)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove múltiplos corretores duplicados para a mesma prova deixando apenas um')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')

    args = parser.parse_args()

    calendario = args.calendario
    tipo = args.tipo

    if args.tipo is not None:
        if args.tipo not in ['regular','dp','exam']:#acrescimo de exam
            print( 'Tipo de submissão deve ser regular, exam ou dp' )
            sys.exit(1)
        tipo = args.tipo

    RemoveDuplicado(calendario, tipo)

