#!/usr/local/bin/python3

import csv
import os
import os.path
import string
import sys
import tempfile
import string

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import code128
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as rpImage
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

tradius = 6
vspace = 17
hspace = 17
width, height = A4

def DataInvertida(dataStr):
    return dataStr[6:10] + dataStr[3:5] + dataStr[0:2]

class Aluno:
    def __init__(self, campos):
        self.nome = campos[0]
        self.ra = campos[1]
        self.polo = campos[2]
        self.nomePolo = campos[3]
        self.data = campos[4]
        self.curso = campos[5]
        self.turma = campos[6]
        self.bimestre = campos[7]
        self.disciplina = campos[8]
        self.nomeDisciplina = campos[9]
        self.prova = campos[10]
        self.questoesObjetivas = int(campos[11])
        self.folhasDissertativas = int(campos[12])
        self.dataStr = DataInvertida(self.data)
        self.codigo = ''
        return

    def GeraCodigo(self):
        self.codigo = self.dataStr + '-' + \
                      self.polo + '-' + self.disciplina + '-' + \
                      self.prova + '-' + self.ra

        return self.codigo

    def Esvazia(self, ra):
        self.nome = '__________________________________________________'
        self.curso = '_________________________'
        self.turma = '_______________'
        self.bimestre = '___'
        self.ra = ra
        self.GeraCodigo()
        self.ra = '__________'
        return


def Grid(myCanvas):
    myCanvas.setStrokeColorRGB(0.9, 0.9, 0.9)
    myCanvas.setFont('Helvetica', 8)

    linha = 0
    while linha < height:
        myCanvas.line(0, linha, width, linha)
        myCanvas.drawString(0, linha, str(int(linha / cm + 0.5)))
        linha += cm

    coluna = 0
    while coluna < width:
        myCanvas.line(coluna, 0, coluna, height)
        myCanvas.drawString(coluna, height - 20, str(int(coluna / cm + 0.5)))
        coluna += cm

    myCanvas.setStrokeColorRGB(0, 0, 0)
    return

def draw_option_mark(myCanvas, x, y, carac, fill):
    '''Draws the option mark circle'''
    DISP_LETTER = {'A':1.0, 'B':1.0, 'C':0.6, 'D':1.0, 'E':1.0, 'F':1.2, 'G':0.2, 'H':0.6, 'I':1.9, 'J':1.3}
    myCanvas.setLineWidth(0.6) 
    myCanvas.setFont("Helvetica", 6.5) 
    myCanvas.setFillColorRGB(0.2,0.2,0.2)
    if carac in string.digits:
        myCanvas.drawString(1.2+x-tradius/2, y+0.5-tradius/2, "%s" % carac)
    else:
        myCanvas.drawString(DISP_LETTER[carac]+x-tradius/2, y+0.5-tradius/2, "%s" % carac)
    if fill==0:
        myCanvas.setFillColorRGB(0.2,0.2,0.2)
        myCanvas.circle(x, y-0.3, tradius, stroke=1, fill=fill)
    else:
        # to test errors, faded marks
        #from random import randint
        #if randint(0,100)>70:
        #    r=1.0*randint(0,100)/100
        #    g=1.0*randint(0,100)/100
        #    b=1.0*randint(0,100)/100
        #    myCanvas.setFillColorRGB(r,g,b)
        #else:
        #    myCanvas.setFillColorRGB(0,0,0)
        myCanvas.setFillColorRGB(0,0,0)
        myCanvas.circle(x, y-0.3, tradius, stroke=1, fill=fill)
        myCanvas.setFillColorRGB(0,0,0)

    return

def draw_option_list_hor(myCanvas, x,y,i,n,options):
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(0,0,0)
    if n >= 100:
        myCanvas.drawString(x-4.2*tradius, y-3-vspace*i, "%02d" % n)
    else:
        myCanvas.drawString(x-3.5*tradius, y-3-vspace*i, "%02d" % n)
    myCanvas.setFont("Helvetica", 8) 
    # to test errors
    #from random import randint
    #if randint(0,100)>90:
    #    chosen = [] # error, blank
    #else:
    #    chosen = [randint(0,4)]
    #if randint(0,100)>90:
    #    chosen.append(randint(0,4)) # error, more than one chosen
    #if randint(0,100)>95:
    #    chosen.append(randint(0,4)) # error, more than one chosen
    for j in range(len(options)):
        #if j in chosen:
        #    draw_option_mark(myCanvas, x+j*hspace, y-vspace*i, options[j],1)
        #else:
            draw_option_mark(myCanvas, x+j*hspace, y-vspace*i, options[j],0)
            
def FolhaRespostaBase(myCanvas, pagina, totalPaginas):
    margin = 2 * cm
    marginleft = margin
    marginright = width - margin
    margintop = height - 1.1 * margin

    # Coloca um grid quadriculado em cinza claro para ajudar o posicionamento.
    #Grid(myCanvas)

    # Coloca o logotipo no canto superior esquerdo
    logo = rpImage('univesp.png', 956/8, 346/8)
    logo.drawOn(myCanvas, marginleft, margintop - 18)

    # Textos
    myCanvas.setFont('Helvetica', 16) 
    myCanvas.drawString(8.3 * cm, margintop + 12, 'FOLHA DE RESPOSTA')

    myCanvas.setFont('Helvetica', 10)
    myCanvas.circle(8.6 * cm, 27.1 * cm, tradius, stroke=1)
    myCanvas.drawString(9.3 * cm, 27 * cm, 'Ausente')

    myCanvas.circle(12.3 * cm, 27.1 * cm, tradius, stroke=1)
    myCanvas.drawString(13 * cm, 27 * cm, 'Anulada')

    # Linha
    myCanvas.line(marginleft, 26 * cm, 15.8 * cm, 26 * cm)

    # Texto de identificação
    # Rótulos
    myCanvas.setFont('Helvetica', 9)
    myCanvas.drawString(marginleft, 25.4 * cm, 'NOME:')
    myCanvas.drawString(marginleft, 24.8 * cm, 'RA:')
    myCanvas.drawString(marginleft + 5 * cm, 24.8 * cm, 'POLO:')
    myCanvas.drawString(marginleft + 10.9 * cm, 24.8 * cm, 'DATA:')
    myCanvas.drawString(marginleft, 24.2 * cm, 'CURSO:')
    myCanvas.drawString(marginleft + 8 * cm, 24.2 * cm, 'TURMA:')
    myCanvas.drawString(marginleft + 13 * cm, 24.2 * cm, 'BIM:')
    myCanvas.drawString(marginleft, 23.6 * cm, 'DISCIPLINA:')
    myCanvas.drawString(marginleft, 23 * cm, 'CÓDIGO DA PROVA:')
 
    # Rodapé
    myCanvas.setLineWidth(1)
    #myCanvas.rect(marginleft, 1 * cm, marginright - marginleft - 3 * cm, 1 * cm, stroke = 1, fill = 0)
    myCanvas.setFont('Helvetica', 10)
    myCanvas.drawString(marginleft + 0.2 * cm, 1.2 * cm, 'Assinatura:')
    myCanvas.line(marginleft + 2 * cm, 1.2 * cm, marginright - 0.2 * cm - 3 * cm, 1.2 * cm)

    #myCanvas.rect(marginright - 2.8 * cm, 1 * cm, 2.8 * cm, 1 * cm, stroke = 1, fill = 0)
    myCanvas.setFont('Helvetica', 10)
    myCanvas.drawString(marginright - 2.6 * cm, 1.2 * cm, 'Página {} de {}'.format(pagina, totalPaginas))
    #    myCanvas.line(marginright - 2.5 * cm, 1.2 * cm, marginright - 0.2 * cm, 1.2 * cm)

    return

def Identificacao(myCanvas, dados, pagina):
    margin = 2 * cm
    marginleft = margin
    margintop = height - 1.1 * margin

    myCanvas.setStrokeColorRGB(0, 0, 0)
    myCanvas.setFillColorRGB(0, 0, 0)

    # Dados do aluno e da prova
    myCanvas.setFont('Helvetica-Bold', 12)
    myCanvas.drawString(marginleft + 1.1 * cm, 25.4 * cm, dados.nome)
    myCanvas.drawString(marginleft + 0.7 * cm, 24.8 * cm, dados.ra)
    myCanvas.drawString(marginleft + 6.2 * cm, 24.8 * cm, dados.nomePolo)
    myCanvas.drawString(marginleft + 12 * cm, 24.8 * cm, dados.data)
    myCanvas.drawString(marginleft + 1.3 * cm, 24.2 * cm, dados.curso)
    myCanvas.drawString(marginleft + 9.3 * cm, 24.2 * cm, dados.turma)
    myCanvas.drawString(marginleft + 13.7 * cm, 24.2 * cm, dados.bimestre)
    myCanvas.drawString(marginleft + 2 * cm, 23.6 * cm, dados.disciplina + ' - ' + dados.nomeDisciplina)
    myCanvas.drawString(marginleft + 3.2 * cm, 23 * cm, dados.codigo)

    # Coloca QR-Code no canto superior direito
    qrw = QrCodeWidget(dados.codigo + '-' + format(pagina, '02d'))
    qrsize = 100.0
    b = qrw.getBounds()
    w = b[2] - b[0]
    h = b[3] - b[1]
    d = Drawing(qrsize, qrsize, transform=[qrsize/w, 0, 0, qrsize/h, 0, 0])
    d.add(qrw)
    renderPDF.draw(d, myCanvas, 16 * cm, margintop - h + 28)

    return

def MultiplaEscolha(myCanvas, nQuestoes):
    margin = 2 * cm
    marginleft = margin
    marginright = width - margin
    margintop = height - 1.1 * margin
    marginbottom = margin
    offset = (width - 500) / 2

    # Instruções
    myCanvas.line(marginleft, 22.6 * cm, marginright, 22.6 * cm)

    myCanvas.setFont('Helvetica-Bold', 12)
    myCanvas.drawString(marginleft, 22 * cm, 'Questões objetivas')
    myCanvas.setFont('Helvetica', 10)
    myCanvas.drawString(marginleft, 21 * cm, 'Marque as respostas com caneta de tinta preta ou azul escuro.')
    myCanvas.drawString(marginleft, 20.4 * cm, 'Preencha completamente a marca correspondente à resposta, conforme o modelo:')
    myCanvas.drawString(marginleft, 19.8 * cm, 'Marque apenas uma resposta por questão. Mais de uma marcação anula a questão.')
    myCanvas.drawString(marginleft, 19.2 * cm, 'Escreva apenas nas áreas demarcadas.')
    myCanvas.drawString(marginleft, 18.6 * cm, 'Assine todas as folhas de prova.')

    myCanvas.setFillColorRGB(0, 0, 0)
    myCanvas.circle(15.3 * cm, 20.5 * cm, tradius, stroke=1, fill=1)

    # Respostas
    myCanvas.setLineWidth(2)
    myCanvas.setFont("Helvetica", 10) 
    bottom = marginbottom+65
    myCanvas.rect(marginleft + 2 * cm, 10 * cm, marginright - marginleft - 4 * cm, 8 * cm, stroke=1, fill=0)
    myCanvas.setLineWidth(1)
    option_letters = ['A', 'B', 'C', 'D', 'E']
    for i in range(1, nQuestoes + 1):
        draw_option_list_hor(myCanvas, 9.5 * cm, 14.8 * cm, i-1, i, option_letters)

    return

def Dissertativa(myCanvas):
    margin = 2 * cm
    marginleft = margin
    marginright = width - margin
    margintop = height - 1.1 * margin
    marginbottom = margin
    offset = (width - 500) / 2

    # Instruções
    myCanvas.line(marginleft, 22.6 * cm, marginright, 22.6 * cm)

    myCanvas.setFont('Helvetica-Bold', 12)
    myCanvas.drawString(marginleft, 22 * cm, 'Questões dissertativas')
    myCanvas.setFont('Helvetica', 10)
    myCanvas.drawString(marginleft, 21 * cm, 'Escreva as respostas com caneta de tinta preta ou azul escuro.')
    myCanvas.drawString(marginleft, 20.4 * cm, 'Escreva apenas nas áreas demarcadas.')
    myCanvas.drawString(marginleft, 19.8 * cm, 'Assine todas as folhas de prova.')

    myCanvas.rect(marginleft, 2.2 * cm, marginright - marginleft, (19.2 - 2.2) * cm, stroke = 1, fill = 0)

    i =  18.4 * cm
    while i > 2.2 * cm:   
        myCanvas.line(marginleft + 0.2 * cm, i, marginright - 0.2 * cm, i)
        i -= 0.8 * cm

    return

def FolhaResposta(myCanvas, dados, objetivas, dissertativas):

    if objetivas != 0:
        totalPaginas = 1 + dissertativas
        FolhaRespostaBase(myCanvas, 1, totalPaginas)
        Identificacao(myCanvas, dados, 1)
        MultiplaEscolha(myCanvas, objetivas)
        myCanvas.showPage()
        pagina = 2
    else:
        totalPaginas = dissertativas
        pagina = 1

    while pagina <= totalPaginas:
        FolhaRespostaBase(myCanvas, pagina, totalPaginas)
        Identificacao(myCanvas, dados, pagina)
        Dissertativa(myCanvas)
        myCanvas.showPage()
        pagina += 1

    return pagina - 1


def ListaPresencaBase(myCanvas, pagina, totalPaginas):
    margin = 2 * cm
    marginleft = margin
    marginright = width - margin
    margintop = height - 1.1 * margin

    # Coloca um grid quadriculado em cinza claro para ajudar o posicionamento.
    Grid(myCanvas)

    # Coloca o logotipo no canto superior esquerdo
    logo = rpImage('univesp.png', 956/8, 346/8)
    logo.drawOn(myCanvas, marginleft, margintop - 18)

    # Textos
    myCanvas.setFont('Helvetica', 16) 
    myCanvas.drawString(8.3 * cm, margintop + 12, 'LISTA DE PRESENÇA')

    # Linha
    myCanvas.line(marginleft, 26 * cm, 15.8 * cm, 26 * cm)

    # Texto de identificação
    # Disciplina
    myCanvas.setFont('Helvetica', 9)
    myCanvas.drawString(marginleft, 25.4 * cm, 'POLO:')
    myCanvas.drawString(marginleft + 10.9 * cm, 25.4 * cm, 'DATA:')
    myCanvas.drawString(marginleft, 24.8 * cm, 'DISCIPLINA:')

    myCanvas.line(marginleft, 24.4 * cm, 15.8 * cm, 24.4 * cm)

    myCanvas.drawString(marginleft, 23.3 * cm, 'APLICADOR: ___________________________________ ')
    myCanvas.drawString(marginleft + 8.5 * cm, 23.3 * cm, 'ASSINATURA: ___________________________________ ')

    myCanvas.rect(marginleft, 2 * cm, marginright - marginleft, (22.6 - 2) * cm, stroke = 1, fill = 0)

    myCanvas.setFont('Helvetica', 9)
    myCanvas.drawString(marginleft + 0.1 * cm, 22.2 * cm, 'Ausente')
    myCanvas.line(marginleft + 1.4 * cm, 22.6 * cm, marginleft + 1.4 * cm, 2 * cm)

    myCanvas.drawString(marginleft + 1.5 * cm, 22.2 * cm, 'Devolveu')
    myCanvas.line(marginleft + 2.9 * cm, 22.6 * cm, marginleft + 2.9 * cm, 2 * cm)

    myCanvas.drawString(marginleft + 3 * cm, 22.2 * cm, 'Nome')
    myCanvas.line(marginleft + 10 * cm, 22.6 * cm, marginleft + 10 * cm, 2 * cm)

    myCanvas.drawString(marginleft + 10.1 * cm, 22.2 * cm, 'RA')
    myCanvas.line(marginleft + 11.5 * cm, 22.6 * cm, marginleft + 11.5 * cm, 2 * cm)

    myCanvas.drawString(marginleft + 11.6 * cm, 22.2 * cm, 'Assinatura')

    myCanvas.line(marginleft, 22 * cm, marginright, 22 * cm)

    for i in range(3, 22):
        myCanvas.line(marginleft, i * cm, marginright, i * cm)

    myCanvas.setFont('Helvetica', 10)
    myCanvas.drawString(marginright - 2.6 * cm, 1.2 * cm, 'Página {} de {}'.format(pagina, totalPaginas))

    return


def IdentificaListaPresenca(myCanvas, disciplina, pagina):
    margin = 2 * cm
    marginleft = margin
    margintop = height - 1.1 * margin

    # Dados do aluno e da prova
    myCanvas.setFont('Helvetica-Bold', 12)
    myCanvas.drawString(marginleft + 1.1 * cm, 25.4 * cm, disciplina['nomePolo'])
    myCanvas.drawString(marginleft + 12 * cm, 25.4 * cm, disciplina['data'])
    myCanvas.drawString(marginleft + 2 * cm, 24.8 * cm, disciplina['codigo'] + '-' + disciplina['nome'])

    codigo = DataInvertida(disciplina['data']) + '-' + disciplina['polo'] + \
             '-' + disciplina['codigo'] + '-' + disciplina['prova'] + '-' + \
             'presenca' + format(pagina, '02d')

    # Coloca QR-Code no canto superior direito
    qrw = QrCodeWidget(codigo)
    qrsize = 100.0
    b = qrw.getBounds()
    w = b[2] - b[0]
    h = b[3] - b[1]
    d = Drawing(qrsize, qrsize, transform=[qrsize/w, 0, 0, qrsize/h, 0, 0])
    d.add(qrw)
    renderPDF.draw(d, myCanvas, 16 * cm, margintop - h + 28)

    return

def PreencheListaPresenca(myCanvas, alunos):
    margin = 2 * cm
    marginleft = margin

    i = 20

    myCanvas.setFont('Helvetica-Bold', 10)

    while len(alunos) > 0 and i > 0:
        myCanvas.drawString(marginleft + 3 * cm, (i + 2.1) * cm, alunos[0].nome)
        myCanvas.drawString(marginleft + 10.2 * cm, (i + 2.1) * cm, alunos[0].ra)
        alunos.pop(0)
    return


def ListaPresenca(myCanvas, disciplina, alunos):
    ListaPresencaBase(myCanvas, 1, 1)
    return


def GeraFolhasResposta(arquivo):
    paginas = 0
    volume = 0

    disciplina = ''
    mCanvas = None
    entrada = list(csv.reader(open(arquivo)))
    # Pula a primeira linha do arquivo e processa as demais
    for linha in entrada[1:]:
        aluno = Aluno(linha)
        nomeDisciplina = aluno.polo + '-' + aluno.nomePolo + '-' + aluno.dataStr + '-' + aluno.disciplina + '-'+ aluno.prova

        # Sempre que trocar os dados da disciplina, fecha o arquivo e começa um novo
        if nomeDisciplina != disciplina:
            print(nomeDisciplina)
            disciplina = nomeDisciplina

            # Se não for a primeira fez
            if mCanvas != None:
                # Gera 3 conjuntos em branco no final, com códigos X, Y e Z
                oldAluno.Esvazia('XXXXXXX')
                FolhaResposta(mCanvas, oldAluno, oldAluno.questoesObjetivas, oldAluno.folhasDissertativas)
                oldAluno.Esvazia('YYYYYYY')
                FolhaResposta(mCanvas, oldAluno, oldAluno.questoesObjetivas, oldAluno.folhasDissertativas)
                oldAluno.Esvazia('ZZZZZZZ')
                FolhaResposta(mCanvas, oldAluno, oldAluno.questoesObjetivas, oldAluno.folhasDissertativas)
                mCanvas.save()

            # Cria um novo pacote de arquivos de provas
            mCanvas = canvas.Canvas('folha_resposta_' + nomeDisciplina + '.pdf', pagesize = A4)

        aluno.GeraCodigo()
        FolhaResposta(mCanvas, aluno, aluno.questoesObjetivas, aluno.folhasDissertativas)
        oldAluno = aluno

    mCanvas.save()
    return


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Uso: {} provas.csv'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    #c = canvas.Canvas('presenca.pdf', pagesize = A4)
    #ListaPresenca(c, 0, 0)
    #c.save()

    sys.exit(0)
    GeraFolhasResposta(sys.argv[1])
