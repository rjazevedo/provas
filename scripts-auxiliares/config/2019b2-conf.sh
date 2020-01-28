#!/bin/bash
#Arquivos de cofiguração

#Backup de csv anteriores (Caminho Completo)
BACKUP_CSV="/home/provas/dados/backup/2019b2"
#Isso é invariavel, é uma base de busca de string
BASE_STRING="Dashboard Provas UNIVESP"
#Caso o bimestre tenha sido consolidado preencher "sim", caso contrario deixar em branco
BIMESTRE_CONSOLIDADO="sim"
#Calendario SGA
CALENDARIO="38"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Destino de Dashboad 2 bimestre
DESTINO_DASHBOARD="SGA/dashboard/2bim"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="csv/2019b2/ausentes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_BASE_CORRECOES="csv/2019b2/baseCorrecoes-2BIM-2019.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="csv/2019b2/corretores-2BIM-2019.csv"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_CSV="csv/2019b2/"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_DASHBOARD="csv/2019b2/todasProvasJuntas.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="SGA/guias_2_bimestre_2019"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="csv/2019b2/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="csv/2019b2/GabaritoMultiplasEscolhas-2BIM-2019.csv"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Path para Home
HOME="/home/provas"
#Caminnho para Logs (caminho completo)
LOG="/home/provas/dados/log/2019b2"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_FIM="Script processaCorrecao 2 Bimestre de 2019 finalizado"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_INICIO="Iniciando o processamento de Correção 2 Bimestre de 2019"
#Mensagem do programa dashboard"
MSG_DASH_INICIO="Inicio da geração do DashBoard - 2 Bimestre 2019"
#Mensagem de fim do Full Insertion
MSG_FULLINSERTION_FIM="Fim de PopulaDB Full Insertion - 2o Bimestre"
#Mensagem de inicio do Full Insertion
MSG_FULLINSERTION_INICIO="Inicio de PopulaDB Full Insertion - 2o Bimestre"
#Mensagem final do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_FIM="Fim da geração do PopulaDB Automatico - 2 Bimestre 2019"
#Mensagem inicial do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_INICIO="Inicio da geração do PopulaDB Automatico - 2 Bimestre 2019"
#Mensagem inicial do programa populaDB
MSG_POPULADB_INICIO="Inicio da geração do PopulaDB - 2 Bimestre 2019"
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/provas_2_bimestre"
#Agrega dois calendários (regular e dp)? sim ou vazio
REGULAR_E_DP=""
#Path Completo de Saida (caminho completo)
SAIDA_CSV="/home/provas/dados/SGA/provas_2_bimestre/Saida"
#Personaliza com informações relativas ao periodo de referencia
SUBSTITUI_STRING=" - 2º Bimestre 2019"
#Indicacao do tipo de prova (regular,dp)
TIPO_PROVA="regular"
#Nome da pasta temporaria de trabalho 2 Bimestre
TRABALHO_TMP="d2BIM2019"
