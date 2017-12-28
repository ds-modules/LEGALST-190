#!/bin/sh

year=$1

cd baileyfiles
cd trialzips

txtname="wgets"+"$year"+".txt"
wget -w 2 -i ../"$txtname"

for f in * ; do mv $f $f.zip; done;

mkdir ../"$year-trialxmls"
unzip "*.zip" -d ../"$year-trialxmls"/


cd ../..