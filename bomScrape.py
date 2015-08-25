__author__ = 'AP+MVBedit'

import urllib2
from lxml import html
from datetime import datetime, date, timedelta
import pytz
import pyFWI.FWIFunctions as FWI
import sqlite3
import os

#

today = date.today()
yesterday = today + timedelta(days=-1)

conn = sqlite3.connect(r"D:\code\fireWeather\weatherLog.db") # added 'r' - makes the file if it is not there?
#conn = sqlite3.connect(os.path.join('.', weatherLog.db)) # added 'r' - makes the file if it is not there?
cur = conn.cursor()

#cur.execute("CREATE TABLE observations ( date STRING, temp FLOAT, humid FLOAT, wind FLOAT, rain FLOAT )") # makes table of assumed requirments
#cur.execute("CREATE TABLE calculations ( date STRING, ffmc FLOAT, dmc FLOAT, dc FLOAT, isi FLOAT, bui FLOAT, fwi FLOAT )") # makes table of assumed requirments
#cur.execute("INSERT INTO calculations VALUES ('%s', 60, 25, 250, 0, 0, 0)"%(yesterday.strftime('%Y-%m-%d'))) # init values

def is_dst(zonename):
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)

tree = html.fromstring(urllib2.urlopen("http://www.bom.gov.au/products/IDN60801/IDN60801.95753.shtml").read())
#today = date.today()
#yesterday = today + timedelta(days=-1)
print today.strftime('%Y-%m-%d')
search = today.strftime("%d") + '/'
search_yesterday = yesterday.strftime("%d") + '/'
if is_dst('Australia/Sydney'):
    search_now = search + '11:00am'
    search_yesterday = search_yesterday + '11:00am'
else:
    search_now = search + '12:00pm'
#    search_now = search + '06:00am'
    search_yesterday = search_yesterday + '12:00pm'
search_9am = date.today().strftime("%d") + '/09:00am'

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
cur.execute("INSERT INTO calculations VALUES ('%s', %f, %f, %f, %f, %f, %f)"%(today.strftime('%Y-%m-%d'), ffmc, dmc, dc, isi, bui, fwi))
conn.commit()
print "FFMC: %.2f"%ffmc
print "DMC : %.2f"%dmc
print "DC  : %.2f"%dc
print "ISI : %.2f"%isi
print "BUI : %.2f"%bui
print "FWI : %.2f"%fwi
print "\r\n-----------------------------\r\n"