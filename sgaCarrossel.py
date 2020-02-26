#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Associa corretores (internal_users) a provas de alunos no SGA
de acordo com a carga atual de cada corretor"""

########################################################
# Casos de uso:
# 
# 1) sgaCarrossel.py -c calendario -d codigo_da_disciplina
#    sgaCarrossel.py -c 37 -d AAG001
# 
#    Lista estatísticas de submissões da disciplina e
#    de corretores atualmente associados
# 
# 2) sgaCarrossel.py -a arquivo_de_corretores -c calendario --commit
#    sgaCarrossel.py -a corretores.csv -c 37 --commit
# 
#    Roda o carrossel para todas as submissões sem 'grader' associado,
#    de todas as disciplinas no arquivo; depois, lista a estatística de
#    corretores associados para cada disciplina
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

offer_types = { 'regular': 1, 'dp': 2, 'exam': 1 } #acrescentado o exam

def erro( str ):
    print( "Erro: " + str )

def estatistica( ca ):

    global sess, tipo, calendario

    # ids (internal_users) dos 'grader's atualmente associados às submissões
    graders =  sess.query(db.ActivityRecordSubmissionCorrectors.internal_user_id) \
                     .distinct(db.ActivityRecordSubmissionCorrectors.internal_user_id) \
                     .join(db.ActivityRecordSubmissions,db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                     .filter(db.ActivityOffers.offer_type == offer_types[tipo]) \
                     .filter(db.CurricularActivities.code == ca) \
                     .filter(db.ActivityOffers.calendar_id == calendario) \
                     .filter(db.ActivityRecordSubmissions.submission_type == tipo) \
                     .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader')

    print( "Número de corretores atualmente associados: ", graders.count() )

    print( "Carga atual total associada a cada corretor (qualquer disciplina deste calendario):" )

    carga =  sess.query(db.ActivityRecordSubmissionCorrectors.internal_user_id) \
                     .join(db.ActivityRecordSubmissions,db.ActivityRecords,db.ActivityOffers) \
                     .filter(db.ActivityOffers.offer_type == offer_types[tipo]) \
                     .filter(db.ActivityOffers.calendar_id == calendario) \
                     .filter(db.ActivityRecordSubmissions.submission_type == tipo)

    go = []

    for g in graders:
        c = sess.query(db.InternalUsers).filter(db.InternalUsers.id == g.internal_user_id).first()
        cnt = carga.filter(db.ActivityRecordSubmissionCorrectors.internal_user_id == g.internal_user_id).count()
        go.append( [cnt,c.name,c.email,c.role] )

    go.sort(reverse=True)

    for g in go:
        print( "[", g[0], "]", g[1], ",", g[2], ",", g[3] )


def associa_grader():

#        submission_corrector = db.ActivityRecordSubmissionCorrectors(
#                                                    activity_record_submission_id = submission.id,
#                                                    role = 'grader',
#                                                    internal_user_id = corrector.id,
#                                                    created_at = func.now(),
#                                                    updated_at = func.now()
#                                                   )
#        sess.add(submission_corrector)
    pass

def associa( ca ):
    """Associa corretores a provas de uma disciplina de acordo com a carga dos corretos no SGA"""

    global sess, tipo, calendario, commit

    print( "Calendário: ", calendario )
    print( "Disciplina: ", ca )

    # todas as submissões da disciplina/calendario/tipo
    submissions = sess.query(db.ActivityRecordSubmissions.id) \
                      .join(db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                      .filter(db.ActivityOffers.offer_type == offer_types[tipo]) \
                      .filter(db.CurricularActivities.code == ca) \
                      .filter(db.ActivityOffers.calendar_id == calendario) \
                      .filter(db.ActivityRecordSubmissions.submission_type == tipo)

    print( "Número de provas submetidas: ", submissions.count() )

    # ids de submissões que já têm 'grader' associados
    has_grader_ids = sess.query(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id) \
                     .distinct(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id) \
                     .join(db.ActivityRecordSubmissions,db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                     .filter(db.ActivityOffers.offer_type == offer_types[tipo]) \
                     .filter(db.CurricularActivities.code == ca) \
                     .filter(db.ActivityOffers.calendar_id == calendario) \
                     .filter(db.ActivityRecordSubmissions.submission_type == tipo) \
                     .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader')

    # ids de submissões que não têm 'grader' associados
    no_grader_ids = sess.query(db.ActivityRecordSubmissions.id).distinct(db.ActivityRecordSubmissions.id) \
                    .join(db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                    .filter(db.ActivityOffers.offer_type == offer_types[tipo]) \
                    .filter(db.CurricularActivities.code == ca) \
                    .filter(db.ActivityOffers.calendar_id == calendario) \
                    .filter(db.ActivityRecordSubmissions.submission_type == tipo) \
                    .filter(db.ActivityRecordSubmissions.id.notin_(has_grader_ids))

    ids_cnt = no_grader_ids.count()

    print( "Número de provas submetidas, sem corretor associado: ", ids_cnt )

    if ( commit ):
        print()
        print( "Associa corretores:" )

        # TO DO

    estatistica( ca )


def carrega_carga():
    global sess, tipo, calendario, pool

    carga =  sess.query(db.ActivityRecordSubmissionCorrectors.internal_user_id) \
                 .join(db.ActivityRecordSubmissions,db.ActivityRecords,db.ActivityOffers) \
                 .filter(db.ActivityOffers.offer_type == offer_types[tipo]) \
                 .filter(db.ActivityOffers.calendar_id == calendario) \
                 .filter(db.ActivityRecordSubmissions.submission_type == tipo)

    for code in pool:
        for iu in pool[code]:
            # corretor (internal_user)
            corrector = sess.query(db.InternalUsers) \
                            .filter(db.InternalUsers.email == iu[2]) \
                            .first()
            if corrector:
                iu[0] = carga.filter(db.ActivityRecordSubmissionCorrectors.internal_user_id == corrector.id).count()
                iu[1] = corrector.id

        pool[code].sort()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Associa corretores (internal_users) a provas de alunos'
                                                 ' no SGA de acordo com a carga atual de cada corretor')
    parser.add_argument('-a', '--arquivo', type=str, help='Arquivo CSV com os emails dos corretores')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')
    parser.add_argument('-d', '--disciplina', type=str, help='Código da disciplina')
    parser.add_argument('--commit', action='store_true', help='Efetiva associações no BD')

    args = parser.parse_args()

    disciplina = args.disciplina
    calendario = args.calendario
    tipo = args.tipo

    if args.tipo is not None:
        if args.tipo not in ['regular','dp','exam']:#acrescimo de exam
            print( 'Tipo de submissão deve ser regular, exam ou dp' )
            sys.exit(1)
        tipo = args.tipo

    ####################
    # Inicia Sessão 
    ####################
    sess = db.Session()
    sess.autoflush = True  # default

    arquivo = args.arquivo

    if arquivo is not None:
        if not os.path.isfile(arquivo):
            print( 'Arquivo ' + arquivo + ' não encontrado!' )
            sys.exit(1)

        ####################
        # percorre CSV
        ####################
        pool = {}

        with open(arquivo, newline='') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                ca_code  = row[0]  # str, Cód. da disciplina
                iu_email = row[1]  # str, Email do corretor (internal_user)

                if ca_code not in pool: pool[ca_code] = []
                pool[ca_code].append( [0,          # carga total
                                       0,          # id
                                       iu_email] ) # email

        if args.commit:
            carrega_carga()
            for code in pool:
                associa( code )

    sess.commit()
