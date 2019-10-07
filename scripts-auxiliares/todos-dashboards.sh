#!/bin/bash
#Descricao: Gera todos os dashboards de uma única vez

for conf in config/*-conf.sh
do
    ./dashboard.sh $conf
done
