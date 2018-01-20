# -*- coding: utf-8 -*-
###############################################################################
## This script processes XML files (each containing one day's court session)  #
## ... into text files, each containing all the trials in a particular        #
## ... offense category (e.g. theft-simplelarceny); the offense category is   #
## ... used as the file name.                                                 #
## In addition, each trial is saved.                                          #
## Also we create two json files, trialdict and offensedict, which make it    #
## ... easy to look up a trial's category or to look up all trials in a       #
## ... particular category.                                                   #
## We also save the text of each trial separately, since it may be useful to  #
## ... have access to those when examining the results of the classification, #
## and a clean text file is more readable than the XML markup.                #
###############################################################################
## (REMEMBER TO REMOVE OLD CATEGORY FILES BEFOE RUNNING THIS SCRIPT)          #
###############################################################################

# THIS IS UNTESTED FOR NOW


import os, re, sys, json
from bs4 import BeautifulSoup


# this bit helps us sort the trial ids in a useful way
# without resorting to the natsort library
# credit: Claudiu at stackoverflow
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]
                

# First, define directory where XML files reside:
indirname = '../baileyfiles/1830s-trialxmls/'

# Then, define directories to write to
mainoutdirname = '../baileyfiles/'
if os.path.exists(mainoutdirname) == 0:
    os.mkdir(mainoutdirname)
    
indvtrialdirname = '../baileyfiles/1830s-trialtxts/'
if os.path.exists(indvtrialdirname) == 0:
    os.mkdir(indvtrialdirname)

txtoutdirname = '../baileyfiles/1830s-trialsbycategory/'
if os.path.exists(txtoutdirname) != 0:
    fileList = os.listdir(txtoutdirname)
    for fileName in fileList:
        os.remove(txtoutdirname+"/"+fileName)
else:
    os.mkdir(txtoutdirname)

# Create two lists into which to save trial ids and id/category pairs
# ... for later use
# ... (printed to file at end)  

trial_ids = []
trial_offense_list = []

# Next, start processing trial xml files from directory 
# ... and outputting text files for each category  

for fn in sorted(os.listdir(indirname)):

    print 'Processing ' + fn
    sys.stdout.flush()
    
    # read XML file and parse it
    # extract trial id (div.get('id')) and the xml for the trial (str(div))
    # make trial xml into soup and extract non-marked-up text from it
    # eliminate spaces and punctuation from text
    # note that the text isn't lowercased, stopwords aren't removed, etc.
    currentfile = indirname + fn 
    with open(currentfile) as f0:
        #lbtag = re.compile('\s+<lb/>') 
        #newfile = lbtag.sub('',f0.read()) #this shouldn't be necessary any more
        newfile = f0.read()
    soup = BeautifulSoup(newfile,"xml")
    div = soup.find('div1',type='trialAccount')
    trialid = div.get('id')
    trial_ids.append(trialid)
    trialxml = str(div)
    trialsoup = BeautifulSoup(trialxml,"xml")
    # Get offense category and subcategory;
    # Note: we simplify here - only a small percentage of trials have
    # ... several offense categories, and when they do, it is nearly always
    # ... various subcategories of theft.
    # So we only save the first offense-suboffense we encounter for each trial.
    # We also guard ourselves against somebody having forgotten to mark the category.
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
                   
# This bit saves the trial ids in a text file
# ... since we need them later to create cross-validation samples etc.
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

                
                

        
    

