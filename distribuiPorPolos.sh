#!/bin/bash

echo "Ignore todas as mensagens de erro a seguir..."

for a in `seq -f "%04.0f" 0 336`
do 
  mkdir -p $a
  mv *-$a-* $a
  rmdir $a
done
