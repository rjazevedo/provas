#!/bin/bash
#Arquivos de cofiguração

#Backup de csv anteriores (Caminho Completo)
BACKUP_CSV="/home/provas/dados/backup/2020dp1"
#Isso é invariavel, é uma base de busca de string
BASE_STRING="Dashboard Provas UNIVESP"
#Caso o bimestre tenha sido consolidado preencher "sim", caso contrario deixar em branco
BIMESTRE_CONSOLIDADO=""
#Calendario Acadêmico no SGA
CALENDARIO="48"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Destino de Dashboad
DESTINO_DASHBOARD="SGA/dashboard/2020dp1"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="csv/2020dp1/ausentes.csv"
#Caminho do arquivo de estrutura base de Correções
ESTRUTURA_BASE_CORRECOES="csv/2020dp1/baseCorrecoes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="csv/2020dp1/corretores.csv"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_CSV="csv/2020dp1"
#Caminho do arquivo de estrutura de Provas Dashboad (Normalmente é igual estrutura provas)
ESTRUTURA_DASHBOARD="csv/2020dp1/dashboard.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="SGA/2020dp1/guias"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="csv/2020dp1/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="csv/2020dp1/GabaritoMultiplasEscolhas.csv"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Path para Home
HOME="/home/provas"
#Caminnho para Logs (caminho completo)
LOG="/home/provas/dados/log/2020dp1"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_FIM="Script processaCorrecao - DP 1o Semestre de 2020 finalizado"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_INICIO="Iniciando o processamento de Correção DP 1o Semestre  2020"
#Mensagem do programa dashboard"
MSG_DASH_INICIO="Inicio da geração do DashBoard - DP 1o Semestre 2020"
#Mensagem de fim do Full Insertion
MSG_FULLINSERTION_FIM="Fim de PopulaDB: Full Insertion - DP 1o Semestre 2020"
#Mensagem de inicio do Full Insertion
MSG_FULLINSERTION_INICIO="Inicio de PopulaDB: Full Insertion - DP 1o Semestre 2020"
#Mensagem final do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_FIM="Fim da geração do PopulaDB Automatico - DP 1o Semestre 2020"
#Mensagem inicial do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_INICIO="Inicio da geração do PopulaDB Automatico - DP 1o Semestre 2020"
#Mensagem inicial do programa populaDB
MSG_POPULADB_INICIO="Inicio da geração do PopulaDB - DP 1o Semestre 2020"
#Caminho das provas
PATH_PROVAS="SGA/2020dp1/provas"
#Agrega dois calendários (regular e dp)? sim ou vazio caso contrario
REGULAR_E_DP=""
#Path Completo de Saida (caminho completo)
SAIDA_CSV="/home/provas/dados/SGA/2020dp1/provas/Saida-DP"
#Personaliza com informações relativas ao periodo de referencia
SUBSTITUI_STRING=" - DP 1º Semestre 2020"
#Indicacao do tipo de prova (regular,dp)
TIPO_PROVA="dp"
#Nome da pasta temporaria de trabalho
TRABALHO_TMP="d1DPBIM2020"