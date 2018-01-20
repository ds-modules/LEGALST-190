import subprocess
import sys, os, io
from bs4 import BeautifulSoup
from datascience import *
from urllib.request import urlopen
import re, json
import numpy as np
import requests, zipfile
import time

mainoutdirname = './baileyfiles/'

# This function pulls all xml files for the date range specified by the user
# into a directory headed by that decade name, e.g. baileyfiles/1750s-trialxmls/ 
def get_xmls(start, end, outdirname, num_files=100, timeout=None):
    if os.path.exists(outdirname) == 0:
        os.mkdir(outdirname)
    
    indirname = outdirname + start + 's-trialxmls/'
    
    wgets = []
    for x in range(0,num_files,10):
        geturl = 'http://www.oldbaileyonline.org/obapi/ob?term0=fromdate_' + start \
                        + '0114&term1=todate_' + end + '1216&count=10&start=' \
                        + str(x+1) + '&return=zip\n'
        wgets.append(geturl)
    
    # old way - wget files from txt file, BAD
    #filename = mainoutdirname + 'wget' + start + 's.txt'
    #with open(filename,'w') as f:
    #   f.write(wgets)
    
    #broken -> not recognizing zip file
    for url in wgets:
        response = urlopen(url)
        with open("temp.zip", "wb") as f:
            f.write(response.read())
            
        with open("temp.zip", "rb") as f:
            z = zipfile.ZipFile(f)
            z.extractall(indirname)
            time.sleep(0.1)

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]

def process_xmls(decade, outdirname):
    #mainoutdirname = '../baileyfiles/'
    indirname = outdirname + decade + 's-trialxmls/'
   
    indvtrialdirname = outdirname + '/'+ decade +'s-trialtxts/'
    if os.path.exists(indvtrialdirname) == 0:
        os.mkdir(indvtrialdirname)

    txtoutdirname = outdirname + '/'+decade+'s-trialsbycategory/'
    if os.path.exists(txtoutdirname) != 0:
        fileList = os.listdir(txtoutdirname)
        for fileName in fileList:
            os.remove(txtoutdirname+"/"+fileName)
    else:
        os.mkdir(txtoutdirname)
     
    trial_ids = []
    trial_offense_list = []
        
    for fn in sorted(os.listdir(indirname)):
        print('Processing ' + fn)
        sys.stdout.flush()
        currentfile = indirname + fn 
        with open(currentfile) as f0:
            newfile = f0.read()
        soup = BeautifulSoup(newfile,"xml")
        div = soup.find('div1',type='trialAccount')
        trialid = div.get('id')
        trial_ids.append(trialid)
        trialxml = str(div)
        trialsoup = BeautifulSoup(trialxml,"xml")
        
        try:
            mainc = trialsoup.find('interp',type='offenceCategory').get('value')
            subc = trialsoup.find('interp',type='offenceSubcategory').get('value')
            offensecategory = '{0}-{1}'.format(mainc.lower().strip(), subc.lower().strip())
        except AttributeError:
            offensecategory = 'uncategorized-trials'
        
        # save trialid, offensecategory for writing into json dict later
        trialtuple = (trialid,offensecategory)
        trial_offense_list.append(trialtuple)
        # get raw text of trial, and make a copy to save one readable version            
        trialtxt = trialsoup.get_text()
        trialtxt_r = trialtxt
        # remove extra spaces and punctuation, with special treatment for '' and --
        dashes  = re.compile("--")
        quotes = re.compile("''")
        punct = re.compile("""[?!.,;:\]\[(){}`'"]""")
        extranewlines = re.compile('\n\s*\n')
        extraspaces = re.compile('\s\s+')
        trialtxt = dashes.sub(' - ',trialtxt)
        trialtxt = quotes.sub('',trialtxt)
        trialtxt = punct.sub(' ',trialtxt)
        trialtxt = extranewlines.sub('\n',trialtxt)
        trialtxt = extraspaces.sub(' ',trialtxt)
        
        # add trialid to beg. of trialtxt 
        trialtxt = trialid + ' ' + trialtxt
        #then save the text file containing this trial
        indvtrialfn = indvtrialdirname + trialid + '.txt'
        with open(indvtrialfn, 'w') as f1:
            f1.write(trialtxt_r)
        # then remove newlines from trial text, open file with offensecategory name
        # ... for appending and add the current trial as a new line 
        newlines = re.compile('\n')
        trialtxt = newlines.sub(' ', trialtxt)
        txtfilename = txtoutdirname + offensecategory + '.txt'
        with open(txtfilename, 'a') as f2:
            f2.write(trialtxt + '\n')
        
        trialidfile = mainoutdirname + 'trialids.txt'
    with open(trialidfile, 'w') as f2:
        trial_ids.sort(key=natural_sort_key)
        f2.write('\n'.join(map(str, trial_ids)))
        
    # This saves the list of trialid, offensecategory pairs into json dump dicts:
    # one dict has trial as key, the other has offense as key
    offense_dict = {}
    trial_dict = {}
    # Loop the list of trial-offense pairs and use the offense as a key for the 
    # ... offense-dict
    for trial, offensetype in trial_offense_list:
        offense_dict.setdefault(offensetype, []).append(trial)
        trial_dict.setdefault(trial,offensetype)
            
            
    offensedict_fn = mainoutdirname + 'offensedict.json'
    with open(offensedict_fn, 'w') as f2:
        json.dump(offense_dict,f2, sort_keys=True, indent=None,separators=(',', ': '))

    trialdict_fn = mainoutdirname + 'trialdict.json'
    with open(trialdict_fn, 'w') as f3:
        json.dump(trial_dict,f3, sort_keys=True, indent=None,separators=(',', ': '))