# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 15:37:21 2017

@author: Anike
"""

# Create URLs for search results pages and save the files
## Arguments: Key Words (query), "advanced" or "basic" parse, start year, start month, end year, end month, number of entries
def getSearchResults(query, kwparse, fromYear, fromMonth, toYear, toMonth, entries):
    # Import modules
    import os, re
    from urllib.request import urlopen
    # Add path to query
    cleanQuery = re.sub(r'\W+', '', query)

    #Create a new directory
    if not os.path.exists(cleanQuery):
        os.makedirs(cleanQuery)
    
    # Index starting at 0
    startValue = 0

    #determine how many files need to be downloaded.
    ## Divide number of entries by 10 b/c API returns 10 at a time
    pageCount = entries / 10
    ## Allow for an extra last page with less than 10 entries
    remainder = entries % 10
    if remainder > 0:
        pageCount += 1

    for pages in range(1, pageCount+1):

        # Each part of the URL. Split up to be easier to read.
        url = 'https://www.oldbaileyonline.org/search.jsp?gen=1&form=searchHomePage&_divs_fulltext='
        url += query
        url += '&kwparse=' + kwparse
        url += '&_divs_div0Type_div1Type=sessionsPaper_trialAccount'
        url += '&fromYear=' + fromYear
        url += '&fromMonth=' + fromMonth
        url += '&toYear=' + toYear
        url += '&toMonth=' + toMonth
        url += '&start=' + str(startValue)
        url += '&count=0'

        # Download the page and save the result.
        response = urlopen(url)
        webContent = response.read()

        # Save the result to the new directory
        filename = cleanQuery + '/' + 'search-result' + str(startValue)
        f = open(filename + ".html", 'w')
        f.write(webContent)
        f.close

        startValue = startValue + 10

# Blank query, can substitute with any search term
query = 'robbery'

# This returns an HTML page with links to each record
getSearchResults(query, "advanced", "1700", "00", "1750", "99", 964)

# Define a function to get the individual records and put them in their own files
def getIndivTrials(query):
    # Import modules
    import os, re, time, socket
    from urllib.request import urlopen

    failedAttempts = []

    #import built-in python functions for building file paths
    from os.path import join as pjoin

    cleanQuery = re.sub(r'\W+', '', query)
    searchResults = os.listdir(cleanQuery)

    urls = []

    # Find search-results pages
    for files in searchResults:
        if files.find("search-result") != -1:
            f = open(cleanQuery + "/" + files, 'r')
            text = f.read().split(" ")
            f.close()

            # look for trial IDs
            for words in text:
                if words.find("browse.jsp?id=") != -1:
                    # Isolate the id
                    urls.append(words[words.find("id=") +3: words.find("&")])

    # Click URLs and save the links to the folder
    for items in urls:
        # Generate the URL
        url = "http://www.oldbaileyonline.org/print.jsp?div=" + items

        # Download the page
        socket.setdefaulttimeout(10)
        try:
            response = urlopen(url)
            webContent = response.read()

            # Create the filename and place it in the new directory
            filename = items + '.html'
            filePath = pjoin(cleanQuery, filename)

            # Save the file
            f = open(filePath, 'wb')
            f.write(webContent)
            f.close
        except:
            failedAttempts.append(url)
        # Pause for 3 seconds
        time.sleep(3)
    print("failed to download: " + str(failedAttempts))

def newDir(newDir):
    import os

    dir = newDir

    if not os.path.exists(dir):
        os.makedirs(dir)

getIndivTrials(query)