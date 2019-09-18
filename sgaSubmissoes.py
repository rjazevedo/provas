#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Cria registros de submissão no SGA a partir de um CSV:
RA do aluno,Cód. da disciplina,Tipo da submissão,Link do anexo,Link do gabarito"""

###############################################
# Uso: sgaSubmissoes.py -a arquivo.csv -c 38
#
# 38: é o calendário do bimestre 2019/2
#
# o arquivo dbpass.txt deve estar no diretório
#
# corresponde à: CreateSubmissionsFromUploadsCSV (SGA)
###############################################

from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
import os
import sys
import argparse
import db
import csv

args = None

offer_types = { 'regular': 1, 'dp': 2, 'exam': 1 } #acrescentado o exam

def erro( str ):
    print( "Erro: " + str )

def carregaNota( 
                  ar,  # academic_register
                  ac,  # activity_code
                  st,  # submission_type
                  la,  # link do anexo
                  lg,  # link do gabarito
                  cid  # calendar_id
                ):

    """Cria um registro de submissão no SGA"""

    st = st.lower()

    print(  
            "Cria registros de submissão no SGA: ",
            ar,  # academic_register
            ac,  # activity_code
            st,  # submission_type
            la,  # link do anexo
            lg,  # link do gabarito
            cid  # calendar_id
          )

    ####################
    # Inicia Sessão 
    ####################
    sess = db.Session()
    sess.autoflush = True  # default

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

    # submissão (cria uma caso não exista)
    submission = sess.query(db.ActivityRecordSubmissions) \
                     .filter(db.ActivityRecordSubmissions.activity_record_id == record.id) \
                     .first()

    if not submission:
        submission = db.ActivityRecordSubmissions(
                                                  activity_record_id = record.id,
                                                  created_at = func.now(),
                                                  updated_at = func.now()
                                                 )
        sess.add(submission)

    submission.submission_type = st,
    submission.link_document = la,
    submission.complementary_data = { 'link_template': lg }

    flag_modified(correction, "complementary_data")  # Sqlalchemy JSON é imutável por default

    sess.commit()

    print( "Sucesso!" )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cria registros de submissão no SGA a partir de um CSV:'
                                                 'RA do aluno,Cód. da disciplina,Tipo da submissão,'
                                                 'Link do anexo,Link do gabarito')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV de submissoes')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')

    args = parser.parse_args()

    arquivo = args.arquivo
    calendario = args.calendario

    if not os.path.isfile(arquivo):
        print( 'Arquivo ' + arquivo + ' não encontrado!' )
        sys.exit(1)

    ####################
    # percorre CSV
    ####################

    with open(arquivo, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            carregaNota(
                          row[0],      # str, RA do aluno
                          row[1],      # str, Cód. da disciplina
                          row[2],      # str, Tipo da submissão
                          row[3],      # str, Link do anexo
                          row[4],      # str, Link do gabarito
                          calendario   ### int, ID do calendário
                       )
