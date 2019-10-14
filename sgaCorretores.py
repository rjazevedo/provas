#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Associa corretores (internal_users) a provas de alunos no SGA a partir de um CSV:
Cód. da disciplina,Cód. da prova,RA do aluno,Email do corretor"""

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

args = None

offer_types = { 'regular': 1, 'dp': 2, 'exam': 1 } #acrescentado o exam

####################
# Inicia Sessão 
####################
sess = db.Session()
sess.autoflush = True  # default


def erro( str ):
    print( "Erro: " + str )

def associaCorretor( 
                     ac,  # activity_code
                     tc,  # test_code
                     ar,  # academic_register
                     ce,  # corrector_email
                     st,  # submission_type
                     cid,  # calendar_id
                     incremental # Só inclui se não houver corretor.
                   ):

    """Associa um corretor a uma prova, de um aluno, no SGA"""

    print(  
            "Tenta associar corretor: ",
             ac,  # activity_code
             tc,  # test_code
             ar,  # academic_register
             ce,  # corrector_email
             st,  # submission_type
             cid,  # calendar_id
             incremental
          )

    # ####################
    # # Inicia Sessão 
    # ####################
    # sess = db.Session()
    # sess.autoflush = True  # default

    # corretor (internal_user)
    corrector = sess.query(db.InternalUsers) \
                    .filter(db.InternalUsers.email == ce) \
                    .first()

    if not corrector:
      erro( "Missing InternalUsers: %s" % (ce) )
      return

    # disciplina
    activity = sess.query(db.CurricularActivities) \
                   .filter(db.CurricularActivities.code == ac) \
                   .first()

    if not activity:
      erro( "Missing CurricularActivities: %s" % (ac) )
      return

    # oferta
    offer = sess.query(db.ActivityOffers) \
                .filter(db.ActivityOffers.curricular_activity_id == activity.id) \
                .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                .filter(db.ActivityOffers.calendar_id == cid) \
                .first()

    if not offer:
      erro( "Missing ActivityOffers: %d, %d" % (cid, offer_types[st]) )
      return

    # aluno
    student = sess.query(db.Students).filter(db.Students.academic_register == ar).first()

    if not student:
      erro( "Missing Students: %d" %(ar) )
      return

    # registro
    record = sess.query(db.ActivityRecords) \
                 .filter(db.ActivityRecords.student_id == student.id) \
                 .filter(db.ActivityRecords.curricular_activity_id == activity.id) \
                 .filter(db.ActivityRecords.activity_offer_id == offer.id) \
                 .first()

    if not record:
      erro( "Missing ActivityRecord: %d, %d, %d" % (student.id, activity.id, offer.id) )
      return

    # prova
    test = sess.query(db.ActivityTests) \
               .filter(db.ActivityTests.code == tc) \
               .filter(db.ActivityTests.curricular_activity_id == activity.id) \
               .first()

    if not test:
      erro( "Missing ActivityTests: %s, %d" % (tc, activity.id) )
      return

    # submissão
    submission = sess.query(db.ActivityRecordSubmissions) \
                     .filter(db.ActivityRecordSubmissions.activity_record_id == record.id) \
                     .filter(db.ActivityRecordSubmissions.submission_type == st) \
                     .first()

    if not submission:
      erro( "Missing ActivityRecordSubmissions: %d, %s, %d" % (record.id, st, test.id) )
      return

    submission_corrector = sess.query(db.ActivityRecordSubmissionCorrectors) \
                    .filter(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id == submission.id) \
                    .filter(db.ActivityRecordSubmissionCorrectors.internal_user_id == corrector.id) \
                    .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader') \
                    .first()

    if not submission_corrector:
        submission_corrector = sess.query(db.ActivityRecordSubmissionCorrectors) \
                  .filter(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id == submission.id) \
                  .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader') \
                  .first()

        if not submission_corrector or incremental:
          submission_corrector = db.ActivityRecordSubmissionCorrectors(
                                                      activity_record_submission_id = submission.id,
                                                      role = 'grader',
                                                      internal_user_id = corrector.id,
                                                      created_at = func.now(),
                                                      updated_at = func.now()
                                                    )
          sess.add(submission_corrector)

    sess.commit()

    print( "Sucesso!" )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Associa corretores (internal_users) a provas de alunos'
                                                 ' no SGA a partir de um CSV: Cód. da disciplina,Cód. da prova,'
                                                 'RA do aluno,Email do corretor')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV com os emails dos corretores')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')
    parser.add_argument('-i', '--incremental', action='store_true', required=False, default=False, help='Faz uma inserção incremental dos dados, sem sobrepor mais de um corretor por prova')

    args = parser.parse_args()

    arquivo = args.arquivo
    calendario = args.calendario
    tipo = args.tipo

    if args.tipo is not None:
        if args.tipo not in ['regular','dp','exam']:#acrescimo de exam
            print( 'Tipo de submissão deve ser regular, exam ou dp' )
            sys.exit(1)
        tipo = args.tipo

    if not os.path.isfile(arquivo):
        print( 'Arquivo ' + arquivo + ' não encontrado!' )
        sys.exit(1)

    ####################
    # percorre CSV
    ####################

    with open(arquivo, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            associaCorretor(
                             row[0],      # str, Cód. da disciplina
                             row[1],      # str, Cód. da prova
                             row[2],      # str, RA do aluno
                             row[3],      # str, Email do corretor (internal_user)
                             tipo,        ### str, Tipo da submissão
                             calendario,   ### int, ID do calendário
                             args.incremental # Somente adiciona corretores das provas que não tem ainda
                           )
