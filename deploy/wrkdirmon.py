#!/usr/bin/python -u
# wrkdirmon.py - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
#    This file is part of OESNMP.
#
#    OESNMP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OESNMP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OESNMP.  If not, see <http://www.gnu.org/licenses/>.
# 
# Make sure to populate wrkdirmon.cfg in the same folder as wrkdirmon.py like this:
# [settings]
# logfile = logfilepath
# basenode = .1.3.6.1.4.1.42674.4 
#
# [wrkdir:randomname]
# path = somefolder
#
# [wrkdir:randomName2]
# path = someotherfolder
# ...

import logging
import ConfigParser
import time
import snmp_passpersist as snmp
import sys, os, os.path, inspect, glob 

if '__file__' not in locals():
    __file__ = inspect.getframeinfo(inspect.currentframe())[0]

mydir = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser.ConfigParser()
config.read( "{0}/wrkdirmon.cfg".format(mydir))

# set up logging
logging.basicConfig( filename = config.get("settings","logfile"), level=logging.INFO,format='%(asctime)s:' + logging.BASIC_FORMAT)

wrkdirs = config.sections()

wrkfilepatterns = ["DBI*","lbi*","srt*"]

# We keep the snmp tree in this file to be able to maintain the same order if new information becomes available. 
# The SNMP OID's for existing information shouldn't change if progress decides to add more information or if we decide to expose more information 

class Unbuffered:
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

def obtainInformation(folderName, pattern):
    files = glob.glob("{0}/{1}".format(folderName,pattern))
    result = {"filecount": 0,
              "totalsize": 0,
              "avgsize": 0,
              "maxsize": 0,
              "oldest": int(str(time.time()).split('.')[0])
              }
    result["filecount"] = len(files) 
    for fileIdx in range(len(files)):
        fileinfo = os.stat(files[fileIdx])
        result["totalsize"] = result["totalsize"] +  fileinfo.st_size
        result["maxsize"] = max(result["maxsize"], fileinfo.st_size)
        result["oldest"] = min(result["oldest"], fileinfo.st_mtime)
    if result["filecount"] > 0 :
        result["avgsize"] = result["totalsize"] / result["filecount"]   
    return result

def updateSnmp ():
    global config, wrkdirs, wrkfilepatterns
    thetime = int(str(time.time()).split('.')[0])
    pp.add_int("1",thetime)
    iIdx = 0 
    for wrkdir in wrkdirs:
        if wrkdir.find("wrkdir:")  != 0 :
            continue
        iIdx = iIdx + 1
        folderName = config.get(wrkdir,"path")
        pp.add_str("2.{0}".format(iIdx),folderName)
        for patternidx in range(len(wrkfilepatterns)):
            information = obtainInformation(folderName,wrkfilepatterns[patternidx])
            pp.add_int("{0}.1.{1}".format(patternidx + 3, iIdx), information["filecount"])
            pp.add_cnt_64bit("{0}.2.{1}".format(patternidx + 3, iIdx), information["totalsize"])
            pp.add_int("{0}.3.{1}".format(patternidx + 3, iIdx), information["avgsize"])
            pp.add_int("{0}.4.{1}".format(patternidx + 3, iIdx), information["maxsize"])
            pp.add_int("{0}.5.{1}".format(patternidx + 3, iIdx), thetime - information["oldest"])
    
basenode = config.get("settings","basenode")

pp = snmp.PassPersist (basenode)
pp.start(updateSnmp, 60)
    