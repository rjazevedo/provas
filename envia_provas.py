#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Automatiza o envio de provas
Criado em: 10-dez-2019
Modificado: 11-dez-2019
"""

import csv
import sys
import argparse
import os
import datetime

#Arquivo entrada provas.csv
# Cabeçalho
# 0 Nome
# 1 RA
# 2 Cod Polo
# 3 Polo
# 4 Data
# 5 Curso
# 6 Turma
# 7 Bimestre
# 8 Codigo Discpl
# 9 Disciplina
# 10 Variante
# 11 Objetivas
# 12 Dissertativas

#Arquivo datas
# Cabeçalho
# 0 Data (DD/MM/AAAA)
# 1 Caminho da pasta (Inciar sem barra)

def DataInvertida(dataStr):
    return dataStr[6:10] + dataStr[3:5] + dataStr[0:2]

class LinhaProva:
    def __init__(self, campos):
        self.polo = campos[2]
        self.data = campos[4]
        self.disciplina = campos[8]
        self.prova = campos[10]
        self.dataStr = DataInvertida(self.data)
        self.indice = self.dataStr + '-' + self.disciplina + '-' + self.prova + '-' + self.polo
        return
    def idProva(self):
        return self.dataStr + '-' + self.disciplina + '-' + self.prova + '-' + self.polo
    def mostraPolo(self):
        return self.polo
    def mostraIndice(self):
        return self.indice
    def mostraData(self):
        return self.data
        
class LinhaPastaDrive:
    def __init__(self,campos):
        self.data=campos[0]
        self.pasta=campos[1]
        self.dataStr = DataInvertida(self.data)
        return
    def mostraData(self):
        return self.data
    def mostraPasta(self):
        return self.pasta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Le arquivo de provas para popular o DB')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com a descrição das provas.csv')
    parser.add_argument('-d', '--datas', type=str, required=True, help='Arquivo com as datas e pasta de datas formato csv')
    parser.add_argument('-o', '--origem', type=str, required=True, help='Pasta com a origem das provas a serem enviadas')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Raiz da saida no Drive')
    parser.add_argument('-p', '--periodo', type=str, required=True, help='Data formato DD/MM/AAAA de referencia para mover provas')
    parser.add_argument('-t', '--testa', action='store_true', help='Testa se arquivos existem, sem enviar ao destino')

    args = parser.parse_args()
    


    print('Abrindo arquivo de referencia Base de aplicação de provas')
    entrada = list(csv.reader(open(args.entrada)))
    datas = list(csv.reader(open(args.datas)))

    print('Analisando dados...')
    linhasProvas = [LinhaProva(x) for x in entrada[1:]]
    linhasDatas = [LinhaPastaDrive(x) for x in datas[1:]]
        
    provas = {}
    pastas = {}
    
    for l in linhasProvas:
        if l.mostraData() == args.periodo:
            provas[l.idProva()] = l.mostraData()
        
    for p in linhasDatas:
        pastas[p.mostraData()] = p.mostraPasta()
 
    itens = len(provas)
    contador = 1

    if args.testa:
        regulares = open( datetime.datetime.now().strftime("%d%m%Y_%H-%M") + "_Erros-provas-regulares" + "_teste" + ".txt", "a")
        baixa_visao = open( datetime.datetime.now().strftime("%d%m%Y_%H-%M") + "_Erros-provas-baixa-visao" + "_teste" + ".txt", "a")
    
        for x, y in provas.items():
            if os.path.isfile( os.path.join(args.origem, x + "-prova.pdf" ) ):
                print("Arquivo " + x + "-prova.pdf encontrado - Progresso " + str(contador) + " de " + str(itens) )
            else:
                print("Erro, arquivo: " + os.path.join(args.origem, x + "-prova.pdf" ) + "não encontrado" )
                regulares.write("Erro no arquivo : " + os.path.join(args.origem, x + "-prova.pdf" + "\n" ) )
            contador += 1
        
        print("\nProvas regulares verificadas! \nIniciando verificação de provas de baixa-visao..\n")
        contador = 1
        
        for x, y in provas.items():
            if os.path.isfile( os.path.join(args.origem, x + "-baixa-visao.pdf" ) ):
                print("Arquivo " + x + "-baixa-visao.pdf encontrado - Progresso " + str(contador) + " de " + str(itens) )
            else:
                print("Erro, arquivo: " + os.path.join(args.origem, x + "-baixa-visao.pdf" ) + " não encontrado" )
                baixa_visao.write("Erro no arquivo : " + os.path.join(args.origem, x + "-baixa-visao.pdf" + "\n" ) )
            contador += 1
        print("Todas as provas foram verificadas")
    else:    
        regulares = open( datetime.datetime.now().strftime("%d%m%Y_%H-%M") + "_Erros-provas-regulares.txt", "a")
        baixa_visao = open( datetime.datetime.now().strftime("%d%m%Y_%H-%M") + "_Erros-provas-baixa-visao.txt", "a")
    
        for x, y in provas.items():
            print( "cp " + os.path.join(args.origem, x + "-prova.pdf" ) + " " + os.path.join(args.saida, x[21:] + "*/" + pastas[y]) )       
            if os.system( "cp " + os.path.join(args.origem, x + "-prova.pdf" ) + " " + os.path.join(args.saida, x[21:] + "*/" + pastas[y]) ) != 0 :
                print("Erro no arquivo : " + os.path.join(args.origem, x + "-prova.pdf" ) )
                regulares.write("Erro no arquivo : " + os.path.join(args.origem, x + "-prova.pdf" + "\n" ) )
            else:
                print("Arquivo " + x + "-prova.pdf copiado - Progresso " + str(contador) + " de " + str(itens) )
            contador += 1
        print("\nProvas regulares copiadas! \nIniciando provas de baixa-visao..\n")
        
        contador = 1
        for x, y in provas.items():
            print( "cp " + os.path.join(args.origem, x + "-baixa-visao.pdf" ) + " " + os.path.join(args.saida, x[21:] + "*/" + pastas[y]) )       
            if os.system( "cp " + os.path.join(args.origem, x + "-baixa-visao.pdf" ) + " " + os.path.join(args.saida, x[21:] + "*/" + pastas[y]) ) != 0 :
                print("Erro no arquivo : " + os.path.join(args.origem, x + "-baixa-visao.pdf" ) )
                baixa_visao.write("Erro no arquivo : " + os.path.join(args.origem, x + "-baixa-visao.pdf" + "\n" ) )
            else:
                print("Arquivo " + x + "-baixa-visao.pdf copiado - Progresso " + str(contador) + " de " + str(itens) )
            contador += 1
        print("Todas as provas foram copiadas")


    regulares.close()
    baixa_visao.close()

