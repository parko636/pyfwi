#! python
from pyFWI import *
import sys, re, datetime

def batchFWI(fileName):
    '''Given the path to a csv file, calculates FWI values for all lines of data

fileName - path to csv file to be processed

fwi values (ffmc,dmc,dc,isi,bui, and fwi) are added to each line in the file.

This function assumes the dates are consecutive.

The first line must contain the date format, latitude, ffmc, dmc, and dc values

Each line thereafter must contain date, temperature, relative humidity, wind speed, and rain

EX)
%m/%d/%Y,45.979999999999997,85,6,15
04/13/2000,17,42,25,0

-->

%m/%d/%Y,45.979999999999997,85,6,15
04/13/2000,17,42,25,0,87.692980092774448,8.5450511359999997,19.013999999999999,10.853661073655068,8.4904265358371838,10.096371392382368'''

    csv = open(fileName, 'r')

    results = []
    first = []
    format = ""

    rowNum = 0;
    for line in csv:
            stuff = re.split(',',line)

            #read start parameters
            if rowNum == 0:
                format = stuff[0]
                first=[eval(x.replace('\r','').replace('\n','')) for x in stuff[1:]]
                rowNum+=1

            #Read inputs
            else:
                results += [[datetime.datetime.strptime(stuff[0],format)]+[eval(x.replace('\r','').replace('\n','')) for x in stuff[1:5]]]

    rowNum = 0;

    #run calculations
    for row in results:
        if rowNum==0:
            ffmc = FFMC(row[1],row[2],row[3],row[4],first[1])#TEMP,RH,WIND,RAIN,FFMCPrev)
            dmc = DMC(row[1],row[2],row[4],first[2],first[0],int(row[0].strftime("%m")))#TEMP,RH,RAIN,DMCPrev,LAT,MONTH)
            dc = DC(row[1],row[4],first[3],first[0],int(row[0].strftime("%m")))#TEMP,RAIN,DCPrev,LAT,MONTH)
            isi = ISI(row[3],ffmc)#WIND, ffmc)
            bui = BUI(dmc,dc)#dmc,dc)
            fwi = FWI(isi,bui)#isi, bui)
            row += [ffmc,dmc,dc,isi,bui,fwi]
        else:
            ffmc = FFMC(row[1],row[2],row[3],row[4],results[rowNum-1][5])#TEMP,RH,WIND,RAIN,FFMCPrev)
            dmc = DMC(row[1],row[2],row[4],results[rowNum-1][6],first[0],int(row[0].strftime("%m")))#TEMP,RH,RAIN,DMCPrev,LAT,MONTH)
            dc = DC(row[1],row[4],results[rowNum-1][7],first[0],int(row[0].strftime("%m")))#TEMP,RAIN,DCPrev,LAT,MONTH)
            isi = ISI(row[3],ffmc)#WIND, ffmc)
            bui = BUI(dmc,dc)#dmc,dc)
            fwi = FWI(isi,bui)#isi, bui)
            row += [ffmc,dmc,dc,isi,bui,fwi]           
        rowNum+=1

    csv.close()
    csv = open(fileName, 'w')

    #write parameters back, allows file to be run again
    csv.write(format+",")
    for var in first[:-1]:
        csv.write(repr(var)+",")
    csv.write(repr(first[-1])+"\n")

    #write inputs and results
    for row in results:
        csv.write(row[0].strftime(format)+',')
        for var in row[1:-1]:
            csv.write(repr(var)+",")
        csv.write(repr(row[-1])+'\n')

    csv.close()

if __name__=="__main__":
    for arg in sys.argv[1:]:
        batchFWI(arg)