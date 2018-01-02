import subprocess
import sys, os
from bs4 import BeautifulSoup
from datascience import *
from urllib.request import urlopen
import re
import numpy as np

mainoutdirname = './baileyfiles/'
    
def wget_files(start, end, num_files):
    wgets = ''
    for x in range(0,num_files,10):
        getline = 'http://www.oldbaileyonline.org/obapi/ob?term0=fromdate_' + start \
                        + '0114&term1=todate_' + end + '1216&count=10&start=' \
                        + str(x+1) + '&return=zip\n'
        wgets += getline
    filename = mainoutdirname + 'wget' + start + 's.txt'
    with open(filename,'w') as f:
        f.write(wgets)

def make_table(decade):
    path = mainoutdirname + decade + "-trialxmls/"
    xmls = os.listdir(path)
    rows = []
    for file in xmls:
        row_info = dict()
        with open(path + file, 'r') as html:
            html_file = html.read()
            soup = BeautifulSoup(html_file, 'html.parser')
            
            for tag in soup.find_all('rs'):
                if len(tag.contents) > 1:
                    for child in tag.children:
                        if type(child) == type(tag):
                            if child.has_attr('type'):
                                row_info[child['type']] = child['value']                         
            
            for tag in soup.find_all('persname'):
                if tag.has_attr('type'):
                    for child in tag.children:
                        if type(child) == type(tag):
                            if child.has_attr('type') and child['type'] == 'gender':
                                gender = child['value']                                
                    name = tag.text.replace('\n', '').split()
                    tagName = tag['type'].replace('Name', '')
                    row_info[tagName + ' given'] = name[0]
                    row_info[tagName + ' surname'] = name[1]
                    row_info[tagName + ' gender'] = gender    

            for tag in soup.find_all('interp')[:4]:
                row_info[tag['type']] = tag['value']
            
            row_info['file name'] = file[:-4]
            row_info['trial summary'] = re.sub(r'\s+', ' ', soup.p.text.replace('\n', ''))
        
        rows.append(row_info)

    table = Table.from_records(rows)
    return table
