import subprocess
import sys

mainoutdirname = './baileyfiles/'
    
def wget_files(start, end, num_files):
    wgets = ''
    for x in range(0,eval(num_files),10):
        getline = 'http://www.oldbaileyonline.org/obapi/ob?term0=fromdate_' + start + '0114&term1=todate_' + end + '1216&count=10&start=' + str(x+1) + '&return=zip\n'
        wgets += getline
    filename = mainoutdirname + 'wget' + start + 's.txt'
    with open(filename,'w') as f:
        f.write(wgets)
       
    
    
if __name__ == "__main__":
    
    
    subprocess.call(['mkdir', 'baileyfiles'])
    subprocess.call(['mkdir', 'baileyfiles/trialzips'])
    wget_files(sys.argv[1], sys.argv[2], sys.argv[3])
    
    subprocess.call(['chmod', 'a+x', 'pullFiles.sh'])
    subprocess.call(['./extractFiles.sh', sys.argv[1]])