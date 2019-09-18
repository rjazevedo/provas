#!/bin/bash
#Arquivos de cofiguração

#Backup de csv anteriores (Caminho Completo)
BACKUP_CSV="/home/provas/dados/backup/2019b1"
#Isso é invariavel, é uma base de busca de string
BASE_STRING="Dashboard Provas UNIVESP"
#Calendario no SGA
CALENDARIO="37"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Destino de Dashboad
DESTINO_DASHBOARD="SGA/dashboard/2019b1"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="csv/2019b1/ausentes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_BASE_CORRECOES="csv/2019b1/baseCorrecoes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="csv/2019b1/corretores.csv"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_CSV="csv/2019b1/"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_DASHBOARD="csv/2019b1/todasProvasJuntas.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="SGA/guias"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="csv/2019b1/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="csv/2019b1/GabaritoMultiplasEscolhas.csv"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Path para Home
HOME="/home/provas"
#Caminnho para Logs (caminho completo)
LOG="/home/provas/dados/log/2019b1"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_FIM="Script processaCorrecao 1o Bimestre de 2019 finalizado"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_INICIO="Iniciando o processamento de Correção 1o Bimestre de 2019"
#Mensagem do programa dashboard"
MSG_DASH_INICIO="Inicio da geração do DashBoard - 1o Bimestre 2019"
#Mensagem de fim do Full Insertion
MSG_FULLINSERTION_FIM="Fim de PopulaDB Full Insertion - 1o Bimestre"
#Mensagem de inicio do Full Insertion
MSG_FULLINSERTION_INICIO="Inicio de PopulaDB Full Insertion - 1o Bimestre"
#Mensagem final do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_FIM="Fim da geração do PopulaDB Automatico - 1o Bimestre 2019"
#Mensagem inicial do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_INICIO="Inicio da geração do PopulaDB Automatico - 1o Bimestre 2019"
#Mensagem inicial do programa populaDB
MSG_POPULADB_INICIO="Inicio da geração do PopulaDB - 1o Bimestre 2019"
#Caminho das provas
PATH_PROVAS="SGA/provas"
#Path Completo de Saida (caminho completo)
SAIDA_CSV="/home/provas/dados/SGA/provas/Saida"
#Personaliza com informações relativas ao periodo de referencia
SUBSTITUI_STRING=" - 1o Bimestre 2019"
#Indicacao do tipo de prova (regular,dp)
TIPO_PROVA="regular"
#Nome da pasta temporaria de trabalho
TRABALHO_TMP="d1BIM2019"
