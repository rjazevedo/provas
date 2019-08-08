#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Associa corretores (internal_users) a provas de alunos no SGA
de acordo com a carga atual de cada corretor"""

########################################################
# Sempre um dryrun por default, sempre somente uma
# simulação. Para efetivar associações no BD, use: --commit
# 
# Casos de uso:
# 
# 1) sgaCarrossel.py -c calendario -d codigo_da_disciplina
#    sgaCarrossel.py -c 37 -d AAG001
# 
#    Lista estatísticas de submissões da disciplina e
#    de corretores atualmente associados
# 
# 2) 
# 
# 
# 
# 
# 
# o arquivo dbpass.txt deve estar no diretório
########################################################

from sqlalchemy import func
import os
import sys
import argparse
import db
import csv

args = None

offer_types = { 'regular': 1, 'dp': 2 }

def erro( str ):
    print( "Erro: " + str )


def associa( 
            ca,   # Cód. da disciplina
            cid,   # ID do calendário
            st   # Tipo da submissão
            ):
    """Associa corretores a provas de uma disciplina de acordo com a carga dos corretos no SGA"""

    print( "Calendário: ", cid )
    print( "Disciplina: ", ca )
    print()

    ####################
    # Inicia Sessão 
    ####################
    sess = db.Session()
    sess.autoflush = True  # default

    # submissões
    submissions = sess.query(db.ActivityRecordSubmissions,
                             db.ActivityRecords,
                             db.ActivityOffers,
                             db.CurricularActivities) \
                      .filter(db.ActivityOffers.curricular_activity_id == db.CurricularActivities.id) \
                      .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                      .filter(db.ActivityRecords.activity_offer_id == db.ActivityOffers.id) \
                      .filter(db.ActivityRecordSubmissions.activity_record_id == db.ActivityRecords.id) \
                      .filter(db.CurricularActivities.code == ca) \
                      .filter(db.ActivityOffers.calendar_id == cid) \
                      .filter(db.ActivityRecordSubmissions.submission_type == st) \
                      .all()

    print( len(submissions) )

    # provas
#    test = sess.query(db.ActivityTests) \
#               .filter(db.ActivityTests.curricular_activity_id == activity.id) \
#               .all()

#    for t in test:
#       print( t.id )
#       print( t.code )
#       print( t.total_pages )
#       print( t.curricular_activity_id )

#    sess.commit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Associa corretores (internal_users) a provas de alunos'
                                                 ' no SGA de acordo com a carga atual de cada corretor')
    parser.add_argument('-a', '--arquivo', type=str, help='Arquivo CSV com os emails dos corretores')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')
    parser.add_argument('-d', '--disciplina', type=str, required=True, help='Código da disciplina')
    parser.add_argument('--commit', action="store_true", help='Efetiva associações no BD')

    args = parser.parse_args()

    disciplina = args.disciplina
    calendario = args.calendario
    tipo = args.tipo

    if args.tipo is not None:
        if args.tipo not in ['regular','dp']:
            print( 'Tipo de submissão deve ser regular ou dp' )
            sys.exit(1)
        tipo = args.tipo

    associa( 
             disciplina, 
             calendario,
             tipo
           )

#    if args.commit:

#    if not os.path.isfile(arquivo):
#        print( 'Arquivo ' + arquivo + ' não encontrado!' )
#        sys.exit(1)

    ####################
    # percorre CSV
    ####################

#    with open(arquivo, newline='') as f:
#        reader = csv.reader(f, delimiter=',')
#        for row in reader:
#            associaCorretor(
#                             row[0],      # str, Cód. da disciplina
#                             row[1],      # str, Cód. da prova
#                             row[2],      # str, RA do aluno
#                             row[3],      # str, Email do corretor (internal_user)
#                             tipo,        ### str, Tipo da submissão
#                             calendario   ### int, ID do calendário
#                           )
