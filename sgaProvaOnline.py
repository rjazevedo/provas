#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from sqlalchemy import func
import db
from sqlalchemy.orm.attributes import flag_modified
import csv
import os
import logging

logger = None
sess = db.Session()
sess.autoflush = True  # default
TEST_PATH = '/var/data/nfs/provas/' # está no .ENV no SGA
offer_types = {'regular': 1, 'dp': 2, 'exam': 1} # acrescentado o exam
offer_number = ['regular', 'regular', 'dp'] # colocado dois regulares para alinhar o índice do vetor ao dicionário acima


def QuestionType(t):
    lt = t.lower()
    if lt == 'objetiva': 
        return 'objective'
    if lt == 'dissertativa': 
        return 'essay'
    return ''


def BuscaCalendario(numero):
    """ Busca os dados do calendário ou retorna None se não encontrar."""
    
    calendarioDB = sess.query(db.Calendar) \
                       .filter(db.Calendar.id == numero) \
                       .first()
                       
    if not calendarioDB:
        logger.error(f'Calendário {numero} não encontrado.')
        return None
    
    return calendarioDB


def BuscaDisciplina(codigo):
    """ Busca a disciplina (db.CurricularActivities) na base e retorna o objeto dela. Caso contrário retorna None."""
    
    activity = sess.query(db.CurricularActivities).filter(db.CurricularActivities.code == codigo).first()

    if not activity: 
      logger.error(f'Faltando Disciplina (CurricularActivities): {codigo}')
      return None
  
    return activity


def BuscaOfertasDisciplina(disciplinaDB, calendario):
    """ Retorna as múltiplas ofertas da disciplina no calendário (db.ActivityOffers). Eu acho que deveria ter apenas uma mas tudo bem. 
        Retorna None se não encontrar. """
    
    ofertasDB = sess.query(db.ActivityOffers) \
                    .filter(db.ActivityOffers.curricular_activity_id == disciplinaDB.id) \
                    .filter(db.ActivityOffers.calendar_id == calendario) \
                    .all()
               
    if not ofertasDB:
        logger.error(f'Não há oferta da disciplina cadastrada: {disciplinaDB.code}')   
        return None
    
    else:
        return ofertasDB  
    

def BuscaOuCriaProva(disciplinaDB, codigo, nfolhas, fazCommit = True):
    """ Busca ou cria uma prova no sistema dado uma disciplina (db.ActivityTests). Note que a prova não está relacionada com nenhuma oferta."""
    
    test = sess.query(db.ActivityTests) \
               .filter(db.ActivityTests.code == codigo) \
               .filter(db.ActivityTests.curricular_activity_id == disciplinaDB.id) \
               .first()

    if not test:
        test = db.ActivityTests(code = codigo,
                                curricular_activity_id = disciplinaDB.id,
                                created_at = func.now(),
                                updated_at = func.now()
                               )
        sess.add(test)
    
    test.total_pages = nfolhas
    if fazCommit:
        sess.commit()
    
    return test

def BuscaAluno(ra):
    """ Busca um aluno no sistema dado o RA dele (db.Students). Retorna None se não encontrar."""
    
    alunoDB = sess.query(db.Students).filter(db.Students.academic_register == ra).first()
    
    if not alunoDB:
        logger.error(f'Faltando aluno na base de dados. RA: {ra}')
        return None
    
    return alunoDB


def BuscaAlunoEmail(email):
    """ Busca um aluno no sistema dado o email dele (db.Students). Retorna None se não encontrar."""
    
    alunoDB = sess.query(db.Students).filter(db.Students.email == email).first()
    
    if not alunoDB:
        logger.error(f'Faltando aluno na base de dados. RA: {email}')
        return None
    
    return alunoDB


def BuscaMatriculaAlunoDisciplina(alunoDB, disciplinaDB, ofertasDB):
    """ Busca por matrícula de um aluno em disciplina (db.AcrivityRecords). Retorna None se não encontrar. """
    
    for ofertaDB in ofertasDB:
        matriculaDB = sess.query(db.ActivityRecords) \
                    .filter(db.ActivityRecords.student_id == alunoDB.id) \
                    .filter(db.ActivityRecords.curricular_activity_id == disciplinaDB.id) \
                    .filter(db.ActivityRecords.activity_offer_id == ofertaDB.id) \
                    .first()
        if matriculaDB is not None:
            return matriculaDB
        
    logger.error(f'Não encontrei nenhuma matrícula do aluno {alunoDB.academic_register} na disciplina {disciplinaDB.code} nas ofertas solicitadas.')
    return None
                      
                      
def BuscaOuCriaRespostaProva(matriculaDB, provaDB, tipo, folha, fazCommit = True):
    """ Busca por uma resposta para prova que o aluno realizou (db.ActivityRecordSubmissions). Se não encontrar, cria e coloca as folhas. """

    submission = sess.query(db.ActivityRecordSubmissions) \
                     .filter(db.ActivityRecordSubmissions.activity_record_id == matriculaDB.id) \
                     .filter(db.ActivityRecordSubmissions.submission_type == tipo) \
                     .filter(db.ActivityRecordSubmissions.activity_test_id == provaDB.id) \
                     .first()

    if not submission:
        submission = db.ActivityRecordSubmissions(activity_record_id = matriculaDB.id,
                                                  submission_type = tipo,
                                                  activity_test_id = provaDB.id,
                                                  created_at = func.now(),
                                                  updated_at = func.now()
                                                 )
        sess.add(submission)

    attach = sess.query(db.Attachments) \
                 .filter(db.Attachments.attach_reference_id == submission.id) \
                 .filter(db.Attachments.attach_reference_type == 'ActivityRecordSubmission') \
                 .filter(db.Attachments.attach_type == 'response_sheets') \
                 .first()

    if not attach:
        attach = db.Attachments(attach_reference_id = submission.id,
                                attach_reference_type = 'ActivityRecordSubmission',
                                attach_type = 'response_sheets',
                                created_at = func.now(),
                                updated_at = func.now()
                               )
        sess.add(attach)
        
        
    # Estou considerando apenas um arquivo como anexo. Por isso simplifiquei o código comentado abaixo
    n = 1
    sheet_link = {'number': 1, 'path': TEST_PATH + folha}
    attach.sheets_data = [sheet_link]
    
    # if not attach.sheets_data: 
    #     attach.sheets_data = []

    # has_sheet_n = False
    # sheet_n_i = 0
    # for i in range(len(attach.sheets_data)):
    #     e = attach.sheets_data[i]
    #     if e['number'] == n:
    #         has_sheet_n = True
    #         sheet_n_i = i

    # sheet_link = {'number': n, 'path': TEST_PATH + ls}

    # if not has_sheet_n:
    #     attach.sheets_data.append(sheet_link)
    #     #
    flag_modified(attach, "sheets_data")  # Sqlalchemy JSON é imutável por default

    if fazCommit:
        sess.commit()
        
    return submission

    
def BuscaOuCriaGuiaCorrecao(provaDB, link, fazCommit = True):
    """ Cria um anexo para uma prova e coloca o gabarito nele (db.Attachments)."""
    
    attach = sess.query(db.Attachments) \
                 .filter(db.Attachments.attach_reference_id == provaDB.id) \
                 .filter(db.Attachments.attach_reference_type == 'ActivityTest') \
                 .filter(db.Attachments.attach_type == 'correction_guide') \
                 .first()

    if not attach:
        attach = db.Attachments(attach_reference_id = provaDB.id,
                                attach_reference_type = 'ActivityTest',
                                attach_type = 'correction_guide',
                                created_at = func.now(),
                                updated_at = func.now()
                               )
        sess.add(attach)

    attach.attach_path = TEST_PATH + link
    
    if fazCommit:
        sess.commit()
        
    return attach
    

def BuscaOuCriaQuestao(provaDB, nquestao, tipo, peso, fazCommit = True):
    """ Cria uma questão para uma prova na base. Se já existir, atualiza os parâmetros dela."""
    
    questionDB = sess.query(db.ActivityTestQuestions) \
                   .filter(db.ActivityTestQuestions.activity_test_id == provaDB.id) \
                   .filter(db.ActivityTestQuestions.number == nquestao) \
                   .first()
                   
    if not questionDB:
        questionDB = db.ActivityTestQuestions(
                                            activity_test_id = provaDB.id, 
                                            number = nquestao,
                                            created_at = func.now(),
                                            updated_at = func.now()
                                           )
        sess.add(questionDB)

    questionDB.question_type = QuestionType(tipo)
    questionDB.weight = peso
    questionDB.annulled = False
    
    if fazCommit:
        sess.commit()
        
    return questionDB
        

def BuscaOuCriaNota(respostaProvaDB, questaoDB, nota, comentario, fazCommit = True):
    """ Cria uma nota para uma questão de uma prova (db.ActivityRecordSubmissionCorrections), ou atualiza o valor."""
    
    correction = sess.query(db.ActivityRecordSubmissionCorrections) \
                     .filter(db.ActivityRecordSubmissionCorrections.activity_record_submission_id == respostaProvaDB.id) \
                     .filter(db.ActivityRecordSubmissionCorrections.activity_test_question_id == questaoDB.id) \
                     .first()

    if not correction:
        correction = db.ActivityRecordSubmissionCorrections(
                                                    activity_record_submission_id = respostaProvaDB.id,
                                                    activity_test_question_id = questaoDB.id,
                                                    created_at = func.now(),
                                                    updated_at = func.now()
                                                 )
        sess.add(correction)

    correction.grade = nota
    corrector_data = { 'comments': comentario }

    correction.corrector_data = corrector_data

    flag_modified(correction, "corrector_data")  # Sqlalchemy JSON é imutável por default

    if fazCommit:
        sess.commit()
        
    return correction


def BuscaCorretor(email):
    """ Busca um corretor de provas baseado no email. Retorna None se não encontrar.""" 
    
    corretorDB = sess.query(db.InternalUsers) \
                     .filter(db.InternalUsers.email == email) \
                     .first()

    return corretorDB


def AtribuiCorretorTarefaCorrecao(corretorDB, respostaDB, fazCommit = True):
    tarefaDB = sess.query(db.ActivityRecordSubmissionCorrectors) \
                    .filter(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id == respostaDB.id) \
                    .filter(db.ActivityRecordSubmissionCorrectors.internal_user_id == corretorDB.id) \
                    .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader') \
                    .first()

    if not tarefaDB:
        tarefaDB = sess.query(db.ActivityRecordSubmissionCorrectors) \
                  .filter(db.ActivityRecordSubmissionCorrectors.activity_record_submission_id == respostaDB.id) \
                  .filter(db.ActivityRecordSubmissionCorrectors.role == 'grader') \
                  .first()

        if not tarefaDB:
          tarefaDB = db.ActivityRecordSubmissionCorrectors(
                            activity_record_submission_id = respostaDB.id,
                            role = 'grader',
                            internal_user_id = corretorDB.id,
                            created_at = func.now(),
                            updated_at = func.now())
          sess.add(tarefaDB)
          
        tarefaDB.internal_user_id = corretorDB.id
    
    if fazCommit:
        sess.commit()

    return tarefaDB


def LeCorretores(nomeArquivo):
    lista = csv.reader(open(nomeArquivo))
    todosCorretores = {}
    disciplinas = {}
    
    for l in lista:
        disciplina = l[0]
        email = l[1]
        nome = l[2]
        if email not in todosCorretores:
            corretorDB = BuscaCorretor(email)
            if corretorDB == None:
                logger.warning(f'Corretor não encontrado: {disciplina} - {email} - {nome}')
                continue
            elif corretorDB.status == 'active':
                    todosCorretores[email] = True
            else:
                alunoDB = BuscaAlunoEmail(email)
                if alunoDB.current_status == 'enrolled':
                    corretorDB.status = 'active'
                    sess.commit()
                    todosCorretores[email] = True
                    logger.info(f'Ativado corretor que estava inativo: {disciplina} - {email} - {nome}')
                else:
                    logger.info(f'Ignorando corretor inativo: {disciplina} - {email} - {nome}')
                    continue
                
        if disciplina not in disciplinas:
            disciplinas[disciplina] = [email]
        else:
            disciplinas[disciplina].append(email)
            
    logger.info('Corretores Lidos')
    for disciplina in disciplinas:
        logger.info('*** ' + disciplina)
        for email in disciplinas[disciplina]:
            logger.info(email)
    return disciplinas


def CarregaGuia(activity_code, test_code, number_of_sheets, link):
    """Cria registros de provas e guias de correção no SGA"""

    logger.info('%s %s %d %s', activity_code, test_code, number_of_sheets, link)
        
    disciplinaDB = BuscaDisciplina(activity_code)
    if disciplinaDB is None:
        return False
    
    provaDB = BuscaOuCriaProva(disciplinaDB, test_code, number_of_sheets)
    guia = BuscaOuCriaGuiaCorrecao(provaDB, link)
    
    logger.info('Incluída guia de correção da disciplina %s prova %s', activity_code,  test_code)


def ProcessaProvasArquivo(periodos, pasta):
    nomeEntrada = 'csv/{}/configuracoes.csv'.format(pasta)
    if not os.path.isfile(nomeEntrada):
        logger.error(f'Arquivo de configurações não existe: {nomeEntrada}')
        return
    
    entrada = csv.reader(open(nomeEntrada))
    next(entrada)
    
    nomeCorretores = 'csv/{}/corretores.csv'.format(pasta)
    if not os.path.isfile(nomeCorretores):
        logger.error(f'Arquivo de corretores não existe. Continuando sem ele: {nomeCorretores}.')
        corretoresPorDisciplina = {}
    else:
        corretoresPorDisciplina = LeCorretores(nomeCorretores)
    
    for linha in entrada:
        disciplina = linha[0]
        prova = linha[1]
        nquestoes = int(linha[2])
        questoes = []
        n = 1
        while n <= nquestoes:
            questoes.append([n, linha[n * 2 + 1], linha[n * 2 + 2]])
            n += 1
        corretores = corretoresPorDisciplina.get(disciplina, [])
        indiceCorretor = 0
        if len(corretores) == 0:
            logger.error(f'Não há corretores alocados para a discpilina: {disciplina}.')

        logger.info(f'*** {disciplina} - {prova}')
        logger.info('%s %s', nquestoes, str(questoes))
        logger.info('Corretores Disponiveis:')
        for email in corretores:
            logger.info(email)
            
        guia = 'SGA/{}/guias/{}-{}-guia.pdf'.format(pasta, disciplina, prova)
        folhaRespostaBase = 'SGA/{}/provas/{}-{}/{}-{}-'.format(pasta, disciplina, prova, disciplina, prova)
        arquivoAlunosNotas = 'SGA/{}/provas/{}-{}-notas.csv'.format(pasta, disciplina, prova)
        if not os.path.isfile(arquivoAlunosNotas):
            logger.error('Não encontrado arquivo de notas:', arquivoAlunosNotas)
            continue
        alunos = csv.reader(open(arquivoAlunosNotas))
        
        logger.info('Guia: %s', guia)
        logger.info('Folhas resposta começam aqui: %s', folhaRespostaBase)
        logger.info('Notas dos alunos aqui: %s', arquivoAlunosNotas)
                
        disciplinaDB = BuscaDisciplina(disciplina)
        provaDB = BuscaOuCriaProva(disciplinaDB, prova, 1)
        guiaDB = BuscaOuCriaGuiaCorrecao(provaDB, guia)
        questao1 = None
        lancaNota = True
        
        for q in questoes:
            numero = q[0]
            tipo = q[1]  # Todas são cadastradas como Dissertativas na base por causa da correção pelo Forms ter notas fracionárias
            peso = float(q[2])
            questaoDB = BuscaOuCriaQuestao(provaDB, numero, 'Dissertativa', peso)
            if questao1 is None:
                questao1 = questaoDB
                if tipo == 'Dissertativa':
                    lancaNota = False
                
        ofertasDB = []
        for p in periodos:
            o = BuscaOfertasDisciplina(disciplinaDB, p)
            if o is not None:
                ofertasDB.extend(o)
                
        for linha in alunos:
            if linha[0][0] not in '0123456789':
                logger.warning('Saltando aluno %s', linha[0])
                continue
            ra = int(linha[0])
            raStr = linha[0]
            nota = float(linha[1])
            
            logger.info(ra, nota)
                
            alunoDB = BuscaAluno(ra)
            if alunoDB is None:
                continue
            
            matriculaDB = BuscaMatriculaAlunoDisciplina(alunoDB, disciplinaDB, ofertasDB)
            if matriculaDB is None:
                continue
            
            folhaResposta = folhaRespostaBase + raStr + '.pdf'
            respostaDB = BuscaOuCriaRespostaProva(matriculaDB, provaDB, matriculaDB.activity_offer.calendar.calendar_type, folhaResposta, fazCommit = False)
            
            if lancaNota:
                BuscaOuCriaNota(respostaDB, questao1, nota, 'Veja o guia de correção com o peso e as respostas corretas de cada item.', fazCommit = False)    
                
            if len(corretores) > 0:
                corretorDB = BuscaCorretor(corretores[indiceCorretor])
                indiceCorretor = (indiceCorretor + 1) % len(corretores)
                
                AtribuiCorretorTarefaCorrecao(corretorDB, respostaDB, fazCommit = False)
                
            sess.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Importa as provas online no SGA para correção')
    # parser.add_argument('-p', '--prova', type=str, required=True, help='Indica a prova para converter')
    # parser.add_argument('-c', '--config', type=str, required=True, help='Indica o arquivo de configuração das provas')
    parser.add_argument('-n', '--nome', type=str, required=True, help='Indica o nome base da pasta de arquivos (ex.: 2020b1)')
    parser.add_argument('-p', '--periodos', type=int, nargs='+', required=True, help='Número de períodos de Avaliação')
    parser.add_argument('-v', '--verbose', action='store_true', required=False, help='Mostra as informações de status')

    args = parser.parse_args()
    
    verbose = args.verbose
    periodos = args.periodos
    nome = args.nome
    
    logger = logging.getLogger('sgaProvaOnline')
    telaLogger = logging.StreamHandler()
    arquivoLogger = logging.FileHandler('provas-online.log')
    
    telaLogger.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    arquivoLogger.setFormatter(logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s'))
    
    arquivoLogger.setLevel(logging.DEBUG)
    
    
    if verbose:
        telaLogger.setLevel(logging.DEBUG)
    else:
        telaLogger.setLevel(logging.WARNING)

    logger.addHandler(telaLogger)
    logger.addHandler(arquivoLogger)
    logger.info('Iniciando o processo de carga de provas online, corretores e notas no SGA.')
    ProcessaProvasArquivo(periodos, nome)
    logger.info('Processo de carga de provas encerrado.')