#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Marca aluno como presente em uma prova no SGA a partir de um CSV com as colunas:
_, Polo, Cód. da disciplina, Cód. da prova,RA do aluno"""

###############################################
# Uso: sgaPresentes.py -a presentes.csv -c 38
#
# 38: é o calendário do bimestre 2019/2
#
# o arquivo dbpass.txt deve estar no diretório
###############################################

from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
import os
import sys
import argparse
import db
import csv

args = None

offer_types = { 'regular': 1, 'dp': 2, 'exam': 1, 'dpexam': 2 } #acrescentado o exam

####################
# Inicia Sessão 
####################
sess = db.Session()
sess.autoflush = True  # default

def erro( str ):
    print( "Erro: " + str )

def marcaAluno( 
                ac,         # activity_code
                tc,         # test_code
                ar,         # academic_register
                st,         # submission_type
                cid,        # calendar_id
                ed,         # forca a habilitacao do status corrigível reverte status de anulada, ausente
                ae,         # não altera status de presença e anulação, apenas torna editavel
                polo,       # número do polo
                decrescente # associa a presenca usando a segunda ocorrencia de uma mesma disciplina
              ):

    """Marca um aluno como presente em uma prova, no SGA"""

    print(  
            "Tenta marcar um aluno como presente: ",
            ac,  # activity_code
            tc,  # test_code
            ar,  # academic_register
            st,  # submission_type
            cid, # calendar_id
            polo # número do polo
          )

    # ####################
    # # Inicia Sessão 
    # ####################
    # sess = db.Session()
    # sess.autoflush = True  # default

    # disciplina
    activity = sess.query(db.CurricularActivities) \
                   .filter(db.CurricularActivities.code == ac) \
                   .first()

    if not activity: 
      erro( "Missing CurricularActivities: %s" % (ac) )
      return

    # oferta
    if decrescente:
        offer = sess.query(db.ActivityOffers) \
                    .filter(db.ActivityOffers.curricular_activity_id == activity.id) \
                    .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                    .filter(db.ActivityOffers.calendar_id == cid) \
                    .order_by(db.ActivityOffers.id.desc()) \
                    .first()
    else:    
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
    
    if not ae:
        if not test:
          test = sess.query(db.ActivityTests) \
                .filter(db.ActivityTests.code == tc + '-'+ polo) \
                .filter(db.ActivityTests.curricular_activity_id == activity.id) \
                .first()
          if not test:
            erro( "Missing ActivityTests: %s, %d" % (tc, activity.id) )
            return
    else:
        if not test:
            erro( "Missing ActivityTests: %s, %d" % (tc, activity.id) )
            
    if st == 'dpexam':
        st = 'exam'

    # submissão (cria uma caso não exista)
    submission = sess.query(db.ActivityRecordSubmissions) \
                     .filter(db.ActivityRecordSubmissions.activity_record_id == record.id) \
                     .filter(db.ActivityRecordSubmissions.submission_type == st) \
                     .first()

    if not submission:
        submission = db.ActivityRecordSubmissions(
                                                    activity_record_id = record.id,
                                                    submission_type = st,
                                                    activity_test_id = test.id,
                                                    created_at = func.now(),
                                                    updated_at = func.now()
                                                 )
        sess.add(submission)

    submission.activity_test_id = test.id
    
    if ae == False:
        submission.absent = False
        submission.annulled = False
    
    campo_editavel = {'editable': 'true'}
    if ed or ae:
        submission.complementary_data = campo_editavel
    flag_modified(submission, "complementary_data")  # Sqlalchemy JSON é imutável por default
    
    sess.commit()
    # sess.close()

    print( "Sucesso!" )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Marca aluno como presente em uma prova no SGA'
                                                 ' a partir de um CSV com as colunas: _, Polo, Cód. da disciplina,'
                                                 'Cód. da prova,RA do aluno')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV de alunos presentes')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')
    parser.add_argument('-e', '--editavel', action='store_true', help='Habilita para correção um registro que tenha sido bloqueado e reverte ausente e anuladas')
    parser.add_argument('-oe', '--apenaseditavel', action='store_true', help='Apenas Habilita para correção um registro que tenha sido bloqueado')
    parser.add_argument('-d', '--decrescente', action='store_true', help='Caso exista duas disciplinas com mesmo código, ao invés de inserir na primeira ocorrencia usa a segunda')
    
    args = parser.parse_args()

    arquivo = args.arquivo
    calendario = args.calendario
    tipo = args.tipo
    editavel = args.editavel
    apenaseditavel = args.apenaseditavel

    if args.tipo is not None:
        if args.tipo not in ['regular','dp','exam','dpexam']:#acrescimo de exam
            print( 'Tipo de submissão deve ser regular, exam ou dp' )
            sys.exit(1)
        tipo = args.tipo

    if not os.path.isfile(arquivo):
        print( 'Arquivo ' + arquivo + ' não encontrado!' )
        sys.exit(1)

    ####################
    # percorre CSV
    #
    # 0,       1,   2,     3,   4
    # 20190417,0103,MCA503,P001,1801725
    ####################

    with open(arquivo, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            marcaAluno(
                        row[2],          # str, Cód. da disciplina
                        row[3],          # str, Cód. da prova
                        row[4],          # str, RA do aluno
                        tipo,            ### str, Tipo da submissão
                        calendario,      ### int, ID do calendário
                        editavel,        # bool, faz com que uma prova se torne corrigível e reverte todos os status de ausente e anulada
                        apenaseditavel,  # bool, apenas libera a edição
                        row[1],          # str, código do polo
                        args.decrescente # associa a presenca usando a segunda ocorrencia de uma mesma disciplina
                      )
