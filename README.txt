Installation:

python setup.py build
sudo python setup.py install

This will install pyFWI to the standard distribution location (/usr/local/lib/python2.6/dist-packages/) and FWI.py to a standard location on your path (/usWr/local/bin/FWI.py).

Usage:


pyFWI:

import pyFWI

or

from pyFWI import *

See pyFWI/FWIFunctions.py for more information or refer to the function doc strings.

 

Command Line:

FWI.py is a command line script that will run the FWI calculations on a CSV file, which must follow a specific format:

date format, latitude, FFMC init value, DMC init value, DC init value
date, temperature, relative humidity, wind speed, and rain
...

The script will add the results of the calculations to the end of each line so the output format will be:

date format, latitude, FFMC init value, DMC init value, DC init value
date, temperature, relative humidity, wind speed, and rain, FFMC, DMC, DC, ISI, BUI, FWI
...

It is perfectly acceptable to modify the starting parameters of a file and rerun it without removing the calculated values, they will simply overwritten.

Date format strings are the same as the python datetime format strings.
EX) %m/%d/%Y is month/day/Year
