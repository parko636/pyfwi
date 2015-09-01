__author__ = 'Alex Parkinson, Matt van Breugel'
#==============================================================================
global version
version = 'v0.3'

print('>>> FIRE WEATHER <<<').center(80, ' ')

#==============================================================================
import urllib2
from lxml import html
from datetime import datetime, date, timedelta
import pytz
import pyFWI.FWIFunctions as FWI
import sqlite3
import os
import numpy as np
import requests as rq
from bs4 import BeautifulSoup as bs
#==============================================================================
def simpFDI(temp, humd, wind, df):
    """
        Description
        -----------
                Calculates the mk5 FDI via a simple formula.
                
        Parameters
        ----------
                temp  : float
                humid : float
                wind  : float
                df    : integer
        
        Returns
        -------
                FDI : float
        
        Notes
        -----
                Formula from the CFA 4WD Club: http://www.cfa4wd.org/information/Forest_FDI.htm
    """
    return 2*(np.exp((0.987*np.log(df+0.001))-.45-(.0345*humd)+(.0338*temp)+(.0234*wind))) # simply calculated FDI

def ratingFDI(FDI):
    """
        Description
        -----------
                Fetches a descriptor for the FDI based on NSW RFS standards.
        
        Parameters
        ----------
                FDI : float
        
        Returns
        -------
                descriptor : string
    """    
    
    if (FDI >= 0) and (FDI < 12):
        descriptor = 'LOW / MODERATE'
    elif (FDI >= 12) and (FDI < 25):
        descriptor = 'HIGH'
    elif (FDI >= 25) and (FDI < 50):
        descriptor = 'VERY HIGH'
    elif (FDI >= 50) and (FDI < 75):
        descriptor = 'SEVERE'
    elif (FDI >= 75) and (FDI <100):
        descriptor = 'EXTREME'
    elif (FDI >= 100):
        descriptor = 'CATASTROPHIC'
    
    return descriptor

def ratingFWI(FWI):
    """
        Description
        -----------
                Fetches a descriptor for the FWI.
        
        Parameters
        ----------
                FDI : float
        
        Returns
        -------
                descriptor : string
    """
    if (FWI >= 0) and (FWI < 5):
        descriptor = 'LOW'
    elif (FWI >= 5) and (FWI < 14):
        descriptor = 'MODERATE'
    elif (FWI >= 14) and (FWI < 21):
        descriptor = 'HIGH'
    elif (FWI >= 21) and (FWI < 33):
        descriptor = 'VERY HIGH'
    elif (FWI >= 33):
        descriptor = 'EXTREME'
    
    return descriptor

#today = date.today()
#yesterday = today + timedelta(days=-1)

#conn = sqlite3.connect(r".\weatherLog.db") # added 'r' - makes the file if it is not there?
#conn = sqlite3.connect(os.path.join('.', weatherLog.db)) # added 'r' - makes the file if it is not there?


def initDatabase(yesterday):
    """
        Decription
        ----------
                Will create the SQL table of observations if an existing copy 
                is not found.
                
        Parameters
        ----------
                None.
                
        Returns
        -------
                None however may create a SQL table.
    """
    
    conn = sqlite3.connect(r".\weatherLog.db") # added 'r' - makes the file if it is not there?
    cur = conn.cursor()

    cur.execute("CREATE TABLE observations ( date STRING, temp FLOAT, humid FLOAT, wind FLOAT, rain FLOAT )") # makes table of assumed requirments
    cur.execute("CREATE TABLE calculations ( date STRING, ffmc FLOAT, dmc FLOAT, dc FLOAT, isi FLOAT, bui FLOAT, fwi FLOAT )") # makes table of assumed requirments
    cur.execute("INSERT INTO calculations VALUES ('%s', 60, 25, 250, 0, 0, 0)"%(yesterday.strftime('%Y-%m-%d'))) # initial values
    conn.commit()
    
    conn.close()

def is_dst(zonename):
    """
        Description
        -----------
                Returns TRUE if zonename is in DST. False otherwise.
                
        Parameters
        ----------
                zonename : string
        
        Returns
        -------
                bool
    """
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)

def searchTimes():
    """
        Description
        -----------
                Searches through the document for midday.
                
        Parameters
        ----------
                None.
        
        Returns
        -------
                search_now : string
                search_9am : string
                search_yesterday : string
    """
    print today.strftime('%Y-%m-%d')
    search = today.strftime("%d") + '/'
    search_yesterday = yesterday.strftime("%d") + '/'
    if is_dst('Australia/Sydney'):
        search_now = search + '11:00am'
        search_yesterday = search_yesterday + '11:00am'
    else:
        search_now = search + '12:00pm'
#        search_now = search + '06:00am'
        search_yesterday = search_yesterday + '12:00pm'
    search_9am = date.today().strftime("%d") + '/09:00am'
    return search_now, search_9am, search_yesterday

def buildTable(text): # for use in getDF()
    """
        Description
        -----------
                Parse out the rows of an HTML table.
        
        Parameters
        ----------
                text : soup
                
        Returns
        -------
                table : list
    """
    "Parse out the rows of an HTML table."
    soup = text
    return [ [ col.renderContents() for col in row.findAll('td') ]
             for row in soup.find('table').find_all('tr') ]

def findRow(table): # for use in getDF()
    """
        Description
        -----------
                Finds the position of RICHMOND AP in the table.
        
        Parameters
        ----------
                table : list
                
        Returns
        -------
                row : int
                
        Notes
        -----
                table[155][0] = RICHMOND AP
                table[155][2] = df today
                table[155][5] = df yesterday
    """
    for row, lst in enumerate(table):
        for col in lst:
            if 'RICHMOND AP' in col:
                return row
def getDF():
    """
        Description
        -----------
                Fetched the drought factor from the BOM. 
                Note that this required authentication.
                
        Parameters
        ----------
                None.
        
        Returns
        -------
                df : float
                
        Notes
        -----
                URL  : http://reg.bom.gov.au/fwo/reg/IDN65053.html
                user : bomw0107
                pass : 50cLampe
    """
    r = rq.get('http://reg.bom.gov.au/fwo/reg/IDN65053.html', auth=('bomw0107', '50cLampe'))
    soup = bs(r.text)
    return float(buildTable(soup)[findRow(buildTable(soup))][2])

#==============================================================================

today = date.today()
yesterday = today + timedelta(days=-1)

if not os.path.exists("./weatherLog.db"):
    initDatabase(yesterday)

conn = sqlite3.connect(r".\weatherLog.db") # added 'r' - makes the file if it is not there?
cur = conn.cursor()

#==============================================================================

print 'BOM/RICHMOND_AP' 
tree = html.fromstring(urllib2.urlopen("http://www.bom.gov.au/products/IDN60801/IDN60801.95753.shtml").read())

search_now, search_9am, search_yesterday = searchTimes()

for e in tree.find_class('rowleftcolumn'):
    if e.getchildren()[0].text_content() == search_now:
        c = e.getchildren()
        temp = float(c[1].text_content())
        humd = float(c[4].text_content())
        wind = float(c[7].text_content())
        rainnow = float(c[13].text_content())
        print "Temp: %.2f"%temp
        print "Humd: %.2f"%humd
        print "Wind: %.2f"%wind
        print "Rain 12pm: %.2f"%rainnow
    if e.getchildren()[0].text_content() == search_9am:
        rain9am = float(e.getchildren()[13].text_content())
        print "Rain 9am: %.2f"%rain9am
    if e.getchildren()[0].text_content() == search_yesterday:
        rain_yesterday = float(e.getchildren()[13].text_content())
        print 'Rain Yesterday: %.2f'%rain_yesterday

rain = rainnow + rain9am - rain_yesterday
print "Rain Total: %.2f"%rain
cur.execute("INSERT INTO observations VALUES ('%s', %f, %f, %f, %f)"%(today.strftime('%Y-%m-%d'), temp, humd, wind, rain))
conn.commit()
cur.execute("SELECT ffmc, dmc, dc FROM calculations WHERE date = '%s'"%yesterday.strftime('%Y-%m-%d'))
c = cur.fetchone()
ffmc = FWI.FFMC(temp, humd, wind, rain, c[0])
dmc = FWI.DMC(temp, humd, rain, c[1], -33.60, today.month)
dc = FWI.DC(temp, rain, c[2], -33.60, today.month)
isi = FWI.ISI(wind, ffmc)
bui = FWI.BUI(dmc, dc)
fwi = FWI.FWI(isi, bui)
df = getDF()
FDI = simpFDI(temp, humd, wind, df)

#==============================================================================

cur.execute("INSERT INTO calculations VALUES ('%s', %f, %f, %f, %f, %f, %f)"%(today.strftime('%Y-%m-%d'), ffmc, dmc, dc, isi, bui, fwi))
conn.commit()
print "FFMC : %.2f"%ffmc
print "DMC  : %.2f"%dmc
print "DC   : %.2f"%dc
print "ISI  : %.2f"%isi
print "BUI  : %.2f"%bui
print "FWI  : %.2f %s"%(fwi, ratingFWI(fwi))
print "DF   : %.2f"%df
print "FDI  : %.2f %s"%(FDI, ratingFDI(FDI))
print "\r\n-----------------------------\r\n"

#raw_input('Holding')