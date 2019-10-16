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
    
    
    # Para todas as disciplinas
    disciplinas = sess.query(db.CurricularActivities).all()                
        
    for disciplina in disciplinas:
        # Busca as ofertas do período de avaliação atual
        oferta = sess.query(db.ActivityOffers) \
                     .filter(db.ActivityOffers.curricular_activity_id == disciplina.id) \
                     .filter(db.ActivityOffers.offer_type == offer_types[tipo]) \
                     .filter(db.ActivityOffers.calendar_id == calendario).first()
                    
        if not oferta:
            continue
        
        print(disciplina)
        
        # Busca cada prova
        provas = sess.query(db.ActivityTests) \
                     .filter(db.ActivityTests.curricular_activity_id == disciplina.id).all()

        for prova in provas:
            
            # Encontra os alunos matriculados
            matriculados = sess.query(db.ActivityRecords) \
                            .filter(db.ActivityRecords.curricular_activity_id == disciplina.id) \
                            .filter(db.ActivityRecords.activity_offer_id == oferta.id) \
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

        if not submission_corrector or not incremental:
          submission_corrector = db.ActivityRecordSubmissionCorrectors(
                                                      activity_record_submission_id = submission.id,
                                                      role = 'grader',
                                                      internal_user_id = corrector.id,
                                                      created_at = func.now(),
                                                      updated_at = func.now()
                                                    )
          sess.add(submission_corrector)
          print('Adicionado')
        else:
          print('Já existente')
    else:
      print('Adicionado anteriormente')

    sess.commit()

    # print( "Sucesso!" )

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

