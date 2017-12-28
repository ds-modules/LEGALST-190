#!/bin/bash

year=$1

cd baileyfiles
cd trialzips

txtname="wget"$year"s.txt"
wget -nc -q -w 1 -i ../"$txtname"

 
for f in * ; do
    if [ "${f:(-4)}" != ".zip" ]; then 
        mv $f $f.zip
    fi
done

mkdir ../"$year-trialxmls"
unzip -q -n "*.zip" -d ../"$year-trialxmls"/


cd ../..