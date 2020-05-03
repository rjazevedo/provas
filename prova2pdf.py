#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 1802258 
from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.errors import HttpError
from pylatexenc.latexencode import unicode_to_latex
import sys
import os
import argparse
import drive
import re
#import db
import yaml
import shutil

def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
        '´': r"'",
        '°': r'$^o$',
        '¨': r'\textasciitilde{}',
        '→': r'$\rightarrow$',
        '½': r'1/2',
        '≤': r'$\leq$',
        'π': r'$\pi$',
        '²': r'$^2$',
        '⁴': r'$^4$',
        '⅓': r'1/3',
        'α': r'$\alpha$',
    }
    
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


def BaixaArquivos(DRIVE, linha, id):
    resposta = {}
    contador = 1
    for l in linha:
        if l.startswith('https://drive.google.com/'):
            id_arquivo = l[-33:]
            arquivo = DRIVE.files().get(fileId=id_arquivo).execute()
            extensao = arquivo['mimeType'].split('/')[1]
            nomeArquivo = 'cache/arq-{}-{:02d}.{}'.format(id, contador, extensao)
            contador += 1

            if not os.path.isfile(nomeArquivo):
                try:
                    saida = open(nomeArquivo, 'wb')
                    request = DRIVE.files().get_media(fileId=id_arquivo)
                    downloader = MediaIoBaseDownload(saida, request)
                    done = False

                    while not done:
                        status, done = downloader.next_chunk()
                                
                except HttpError as err:
                    continue
                
                saida.close()
            resposta[l] = nomeArquivo

    return resposta


def LeNota(linha):
    if linha[2] != '':
        quebrada = linha[2].split(' / ')
        nota = int(quebrada[0])
        total = int(quebrada[1])
        return nota * 10.0 / total
    else:
        return 0.0

def LeAluno(linha, alunos):
    email = linha[1]
    if email in alunos:
        aluno = alunos[email]
        ra = aluno[0]
        nome = aluno[1]
        return (ra, nome)
    else:
        return (email.split('@')[0].replace('.', '-'), email)

def ProcessaProva(DRIVE, prova, cabecalho, resposta, alunos, forca):
    (ra, nome) = LeAluno(resposta, alunos)
    
    print('***** Prova', prova, 'de:', ra)
    provaAluno = os.path.join('provas', prova, prova + '-' + ra + '.pdf')
    if os.path.isfile(provaAluno) and not forca:
        return []
    
    config = open('config.tex', 'wt')
    conteudo = '\\newcommand{\\prova}{' + prova + \
               '}\n\\newcommand{\\data}{' + resposta[0] + \
               '}\n\\newcommand{\\aluno}{' + ra + ' - ' + nome + '}\n'
               
    config.write(conteudo)
    config.close()
    
    arquivos = BaixaArquivos(DRIVE, resposta, prova + '-' + ra)
    conteudo = open('conteudo.tex', 'wt')
    
    pontuacao = LeNota(resposta)
    conteudo.write('\\section*{Pontuação apenas das questões objetivas}\n\n')
    conteudo.write(str(pontuacao) + ' / 10.0 (Veja o peso de cada questão no guia de correção e a fórmula do cálculo da nota no PDA ou na disciplina no AVA.)\n\n')
    
    #for (titulo, texto) in zip(cabecalho[3:], resposta[3:]):
    for i in range(len(cabecalho) - 3):
        titulo = cabecalho[i + 3]
        if i + 3 < len(resposta):
            texto = resposta[i + 3]
        else:
            texto = 'Em branco'
        
        conteudo.write('\\section*{' + tex_escape(titulo,) + '}\n\n')
        if texto in arquivos:
            nomeArquivo = arquivos[texto]
            if nomeArquivo.endswith('pdf'):
                conteudo.write('\\includepdf[pages=1-]{' + nomeArquivo + '}\n\n')
            else:
                conteudo.write('\\includegraphics[width=\\linewidth]{' + nomeArquivo + '}\n\n')
        else:
            conteudo.write(tex_escape(texto.replace('\n', '\n\n')) + '\n\n')

    conteudo.close()
    
    os.system('lualatex extrato')
    
    
    shutil.move('extrato.pdf', provaAluno)
    # for key in arquivos:
    #     os.remove(arquivos[key])  
        
    os.remove('conteudo.tex')      
    os.remove('config.tex')
    
    return [ra, pontuacao]
    
    
def LeTodosAlunos():
    # alunos = db.session.query(db.Students).all()
    
    # retorno = {}
    # for aluno in alunos:
    #   if aluno.academic_register == 1833305:
    #       continue
    #   if aluno.user is not None:
    #       retorno[aluno.email] = (str(aluno.academic_register), aluno.user.name)
        
    return yaml.safe_load(open('alunos.yml'))

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gera as versões das provas online em em PDF')
    parser.add_argument('-p', '--prova', type=str, nargs='+', required=True, help='Indica a prova para converter')
    parser.add_argument('-v', '--verbose',  action='store_true', required=False, help='Mostra as informações de status')
    parser.add_argument('-n', '--notas', action='store_true', required=False, help='Coleta apenas as notas das provas')
    parser.add_argument('-f', '--forca', action='store_true', required=False, help='Força regerar os arquivos')
    parser.add_argument('-c', '--cabecalho', action='store_true', required=False, help='Apenas imprime os cabeçalhos das provas')

    args = parser.parse_args()
    
    verbose = args.verbose
    provas = args.prova
    soNotas = args.notas
    forca = args.forca
    leCabecalho = args.cabecalho
    
    totalProvas = 0

    (DRIVE, SHEET) = drive.GetTokens(verbose)
        
    if not leCabecalho:
        alunos = LeTodosAlunos()

    for prova in provas:
        print('\n*** Prova:', prova)
        (id_planilha, planilha) = drive.GetPlanilhaRespostas(DRIVE, SHEET, prova, verbose)
        if planilha is None:
            sys.exit(1)
            
        aba = planilha['sheets'][0]
        titulo = aba['properties']['title']
        nLinhas = aba['properties']['gridProperties']['rowCount']
        nColunas = linhas = aba['properties']['gridProperties']['columnCount']
        
        print('Planilha com', nLinhas, 'linhas.')

        faixa="'" + titulo + "'!A1:" + chr(nColunas + 65) + '1'
        cabecalho = SHEET.values().get(spreadsheetId=id_planilha, range=faixa).execute().get('values', [])[0]
        
        if leCabecalho:
            print('** Cabeçalho:')
            for item in cabecalho:
                print('*', item)
            continue
        
        nColunas = len(cabecalho[0])
        linha = 2
        passo = 100
        quantidade = 0
        arquivoNotas = open(os.path.join('provas', prova + '-notas.csv'), 'at')
        if not os.path.isdir(os.path.join('provas', prova)):
            os.mkdir(os.path.join('provas', prova))
            
        while linha < nLinhas:
            faixa = "'" + titulo + "'!A" + str(linha) + ":" + chr(nColunas + 65) + str(linha + passo)
            linhas = SHEET.values().get(spreadsheetId=id_planilha, range=faixa).execute().get('values', [])
            for l in linhas:
                if not soNotas:
                    notas = ProcessaProva(DRIVE, prova, cabecalho, l, alunos, forca)
                    if len(notas) == 2:
                        arquivoNotas.write('{},{}\n'.format(notas[0], notas[1]))
                else:
                    arquivoNotas.write('{},{}\n'.format(LeAluno(l), LeNota(l)))
                quantidade += 1
            linha += passo
            
        arquivoNotas.close()
        print(quantidade, 'provas processadas.')
        totalProvas += quantidade
        
    print(totalProvas, 'provas processadas no total.')
            