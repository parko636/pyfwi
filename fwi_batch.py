__author__ = 'Alex'

from datetime import date, timedelta
import pyFWI.FWIFunctions as FWI
import sqlite3

conn = sqlite3.connect('FWI.db')
cur = conn.cursor()
start = date(2015, 8, 19)
end = date(2015, 8, 22)

for i in range(1,(end-start).days+1):
    yesterday = start + timedelta(days=i-1)
    today = start + timedelta(days=i)
    cur.execute("SELECT temp, humidity, wind, rain FROM observations WHERE date = '%s'"%yesterday.strftime('%Y-%m-%d'))
    c = cur.fetchone()
    temp = c[0]
    humd = c[1]
    wind = c[2]
    rain = c[3]
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