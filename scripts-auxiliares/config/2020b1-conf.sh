#!/bin/bash
#Arquivos de cofiguração

PERIODO="2020b1"
#Backup de csv anteriores (Caminho Completo)
BACKUP_CSV="/home/provas/dados/backup/$PERIODO"
#Isso é invariavel, é uma base de busca de string
BASE_STRING="Dashboard Provas UNIVESP"
#Caso o bimestre tenha sido consolidado preencher "sim", caso contrario deixar em branco
BIMESTRE_CONSOLIDADO=""
#Calendario SGA
CALENDARIO="49"
CALENDARIO_DP="53"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Destino de Dashboad
DESTINO_DASHBOARD="SGA/dashboard/$PERIODO"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="csv/$PERIODO/ausentes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_BASE_CORRECOES="csv/$PERIODO/baseCorrecoes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="csv/$PERIODO/corretores.csv"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_CSV="csv/$PERIODO"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_DASHBOARD="csv/$PERIODO/dashboard.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="SGA/$PERIODO/guias"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="csv/$PERIODO/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="csv/$PERIODO/GabaritoMultiplasEscolhas.csv"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Path para Home
HOME="/home/provas"
#Caminnho para Logs (caminho completo)
LOG="/home/provas/dados/log/$PERIODO"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_FIM="Script processaCorrecao 1o Bimestre de 2020 finalizado"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_INICIO="Iniciando o processamento de Correção 1o Bimestre de 2020"
#Mensagem do programa dashboard"
MSG_DASH_INICIO="Inicio da geração do DashBoard - 1o Bimestre 2020"
#Mensagem de fim do Full Insertion
MSG_FULLINSERTION_FIM="Fim de PopulaDB Full Insertion - 1o Bimestre 2020"
#Mensagem de inicio do Full Insertion
MSG_FULLINSERTION_INICIO="Inicio de PopulaDB Full Insertion - 1o Bimestre 2020"
#Mensagem final do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_FIM="Fim da geração do PopulaDB Automatico - 1o Bimestre 2020"
#Mensagem inicial do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_INICIO="Inicio da geração do PopulaDB Automatico - 1o Bimestre 2020"
#Mensagem inicial do programa populaDB
MSG_POPULADB_INICIO="Inicio da geração do PopulaDB - 1o Bimestre 2020"
#Caminho das provas
PATH_PROVAS="SGA/$PERIODO/provas"
#Agrega dois calendários (regular e dp)? sim ou vazio caso contrario
REGULAR_E_DP="sim"
#Path Completo de Saida (caminho completo)
SAIDA_CSV="/home/provas/dados/SGA/$PERIODO/provas/Saida"
#Personaliza com informações relativas ao periodo de referencia
SUBSTITUI_STRING=" - 1o Bimestre de 2020"
#Indicacao do tipo de prova (regular,dp)
TIPO_PROVA="regular"
TIPO_PROVA_DP="dp"
#Nome da pasta temporaria de trabalho
TRABALHO_TMP="d1BIM2020"
