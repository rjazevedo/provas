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
# 2) sgaCarrossel.py -c calendario -d codigo_da_disciplina --commit
#    sgaCarrossel.py -c 37 -d AAG001 --commit
# 
#    Lista estatísticas de submissões da disciplina e
#    de corretores atualmente associados; roda o carrossel para
#    todas as submissões sem 'grader' associado; lista a
#    estatística de corretores associados
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

def estatistica(
                ca,   # Cód. da disciplina
                cid,  # ID do calendário
                st,   # Tipo da submissão
                sess  # DB sesssion
                ):
    # ids (internal_users) dos 'grader's atualmente associados às submissões
    graders =  sess.query(db.ActivityRecordSubmissionCorrectors.internal_user_id) \
                     .distinct(db.ActivityRecordSubmissionCorrectors.internal_user_id) \
                     .join(db.ActivityRecordSubmissions,db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                     .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                     .filter(db.CurricularActivities.code == ca) \
                     .filter(db.ActivityOffers.calendar_id == cid) \
                     .filter(db.ActivityRecordSubmissions.submission_type == st) \
                     .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader')

    print( "Número de corretores atualmente associados: ", graders.count() )

    print( "Carga atual total associada a cada corretor (qualquer disciplina deste calendario):" )

    carga =  sess.query(db.ActivityRecordSubmissionCorrectors.internal_user_id) \
                     .join(db.ActivityRecordSubmissions,db.ActivityRecords,db.ActivityOffers) \
                     .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                     .filter(db.ActivityOffers.calendar_id == cid) \
                     .filter(db.ActivityRecordSubmissions.submission_type == st)

    go = []

    for g in graders:
        c = sess.query(db.InternalUsers).filter(db.InternalUsers.id == g.internal_user_id).first()
        cnt = carga.filter(db.ActivityRecordSubmissionCorrectors.internal_user_id == g.internal_user_id).count()
        go.append( [cnt,c.name,c.email,c.role] )

    go.sort(reverse=True)

    for g in go:
        print( "[", g[0], "]", g[1], ",", g[2], ",", g[3] )


def associa( 
            ca,    # Cód. da disciplina
            cid,   # ID do calendário
            st,    # Tipo da submissão
            sess,  # DB sesssion
            commit # efetiva carrossel no BD
            ):
    """Associa corretores a provas de uma disciplina de acordo com a carga dos corretos no SGA"""

    print( "Calendário: ", cid )
    print( "Disciplina: ", ca )

    # todas as submissões da disciplina/calendario/tipo
    submissions = sess.query(db.ActivityRecordSubmissions.id) \
                      .join(db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                      .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                      .filter(db.CurricularActivities.code == ca) \
                      .filter(db.ActivityOffers.calendar_id == cid) \
                      .filter(db.ActivityRecordSubmissions.submission_type == st)

    print( "Número de provas submetidas: ", submissions.count() )

    # ids de submissões que já têm 'grader' associados
    has_grader_ids = sess.query(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id) \
                     .distinct(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id) \
                     .join(db.ActivityRecordSubmissions,db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                     .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                     .filter(db.CurricularActivities.code == ca) \
                     .filter(db.ActivityOffers.calendar_id == cid) \
                     .filter(db.ActivityRecordSubmissions.submission_type == st) \
                     .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader')

    # ids de submissões que não têm 'grader' associados
    no_grader_ids = sess.query(db.ActivityRecordSubmissions.id).distinct(db.ActivityRecordSubmissions.id) \
                    .join(db.ActivityRecords,db.ActivityOffers,db.CurricularActivities) \
                    .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                    .filter(db.CurricularActivities.code == ca) \
                    .filter(db.ActivityOffers.calendar_id == cid) \
                    .filter(db.ActivityRecordSubmissions.submission_type == st) \
                    .filter(db.ActivityRecordSubmissions.id.notin_(has_grader_ids))

    ids_cnt = no_grader_ids.count()

    print( "Número de provas submetidas, sem corretor associado: ", ids_cnt )

    estatistica( ca, cid, st, sess )

    if ( commit ):
        print()
        print( "Associa corretores:" )

                




#        submission_corrector = db.ActivityRecordSubmissionCorrectors(
#                                                    activity_record_submission_id = submission.id,
#                                                    role = 'grader',
#                                                    internal_user_id = corrector.id,
#                                                    created_at = func.now(),
#                                                    updated_at = func.now()
#                                                   )
#        sess.add(submission_corrector)





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Associa corretores (internal_users) a provas de alunos'
                                                 ' no SGA de acordo com a carga atual de cada corretor')
    parser.add_argument('-a', '--arquivo', type=str, help='Arquivo CSV com os emails dos corretores')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')
    parser.add_argument('-d', '--disciplina', type=str, required=True, help='Código da disciplina')
    parser.add_argument('--commit', action='store_true', help='Efetiva associações no BD')

    args = parser.parse_args()

    disciplina = args.disciplina
    calendario = args.calendario
    tipo = args.tipo

    if args.tipo is not None:
        if args.tipo not in ['regular','dp']:
            print( 'Tipo de submissão deve ser regular ou dp' )
            sys.exit(1)
        tipo = args.tipo

    ####################
    # Inicia Sessão 
    ####################
    sess = db.Session()
    sess.autoflush = True  # default

    associa( 
             disciplina, 
             calendario,
             tipo,
             sess,
             args.commit
           )

#    if not os.path.isfile(arquivo):
#        print( 'Arquivo ' + arquivo + ' não encontrado!' )
#        sys.exit(1)

    ####################
    # percorre CSV
    ####################

#    pool = {}

#    with open(arquivo, newline='') as f:
#        reader = csv.reader(f, delimiter=',')
#        for row in reader:
#            ca_code  = row[0]  # str, Cód. da disciplina
#            iu_email = row[1]  # str, Email do corretor (internal_user)


#    sess.commit()

#    if args.commit:

