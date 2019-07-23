#! /bin/bash


assets='10547|10548|10550|10790|10789|10788|11076|21945|10849|10927|11655|22241'

find /home/drode/recycle-01-2014 -type f -exec egrep  $assets /dev/null {} \; | grep -v summarize-ganglia
