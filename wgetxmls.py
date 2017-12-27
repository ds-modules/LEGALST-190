import subprocess

mainoutdirname = '../baileyfiles/'
    
def wget_files(start, end, num_files):
    wgets = ''
    for x in range(0,num_files,10):
        getline = 'http://www.oldbaileyonline.org/obapi/ob?term0=fromdate_' + str(start) + '0114&term1=todate_' + str(end) + '1216&count=10&start=' + str(x+1) + '&return=zip\n'
        wgets += getline
    filename = mainoutdirname + 'wget' + str(start) + 's.txt'
    with open(filename,'w') as f:
        f.write(wgets)
        
"""cd ../baileyfiles
mkdir trialzips
cd trialzips
wget -w 2 -i ../wget1830s.txt"""