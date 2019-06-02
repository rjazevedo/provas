#!/bin/bash

echo "Ignore todas as mensagens de erro a seguir..."

for a in `seq -f "%04.0f" 0 336`
do 
  mkdir -p $a
  mv lista_presenca_${a}* $a 2> /dev/null
  mv folha_resposta_${a}* $a 2> /dev/null
  mv folha_ocorrencia_${a}* $a 2> /dev/null
  rmdir $a 2> /dev/null
done
