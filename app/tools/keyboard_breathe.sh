#!/bin/bash
# keyboard_breathe.sh

while true; do

    for ((i=0; i<=100; i+=1)); do

    #sudo /usr/bin/ectool pwmsetkblight $i
    #sleep 0.05  # Adjust speed of breathing effect

    done

    for ((i=100; i>=0; i-=1)); do

    #sudo /usr/bin/ectool pwmsetkblight $i
    #sleep 0.05  # Adjust speed of breathing effect

    done

done
