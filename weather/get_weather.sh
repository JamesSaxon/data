#!/bin/bash 

# with thanks and apologies to weather underground...

# MDW
for w in JFK PHL PDX LAX BOS PHX DEN SFO DFW; do 

  mkdir -p ${w}
  for y in $(seq 2000 2016); do 
    for m in $(seq -w 1 12); do 
      for d in $(seq -w 1 31); do 
        echo ${w} ${y}-${m}-${d}
        curl https://www.wunderground.com/history/airport/K${w}/${y}/${m}/${d}/DailyHistory.html?format=0 \
             -s -o ${w}/${y}${m}${d}
      done
    done
  done

  # cat ${w}/2* | sed "s/<br \/>//" | sort | uniq | sort -k 14 -t"," > weather_${w}.csv
  # rm ${w}/

done

sed -i -e "s/<br \/>//" -e "/^$/d" */*

for f in $(grep "No .*data available" */* | sed "s/:.*//"); do rm $f; done
for f in $(wc -l */* | grep " 1 " | tr -s ' ' | cut -f3 -d" "); do rm $f; done

./merge.py
 
