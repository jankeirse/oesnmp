#!/usr/bin/python -u
# promon.py - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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
# Make sure to populate promon.cfg in the same folder as promon.py like this:
# [settings]
# logfile = logfilepath
# basenode = .1.3.6.1.4.1.42674.2 
# # Log the snmp tree in the logfile: 
# logsnmptree=true 
#
# [database:randomName]
# db = /some/db.db
#
# [database:randomName2]
# db = /some/db2.db
# ...

import logging
import ConfigParser
import time
import snmp_passpersist as snmp
import sys, os, os.path, inspect, subprocess, csv

#make check_output available in python 2.6:
def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs) 
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output
subprocess.check_output = check_output

if '__file__' not in locals():
    __file__ = inspect.getframeinfo(inspect.currentframe())[0]

mydir = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser.ConfigParser()
config.read( "{0}/promon.cfg".format(mydir))

# set up logging
logging.basicConfig( filename = config.get("settings","logfile"), level=logging.INFO,format='%(asctime)s:' + logging.BASIC_FORMAT)

dbs = config.sections()

# We keep the snmp tree in this file to be able to maintain the same order if new information becomes available. 
# The SNMP OID's for existing information shouldn't change if progress decides to add more information or if we decide to expose more information 
snmpTree = [["Commits","int64"],
            ["Undos","int64"],
            ["Record Updates","int64"],
            ["Record Reads","int64"],
            ["Record Creates","int64"],
            ["Record Deletes","int64"],
            ["DB Writes","int64"],
            ["DB Reads","int64"],
            ["BI Writes","int64"],
            ["BI Reads","int64"],
            ["AI Writes","int64"],
            ["Record Locks","int64"],
            ["Record Waits","int64"],
            ["Checkpoints","int64"],
            ["Buffs Flushed","int64"],
            ["Rec Lock Waits","int"],
            ["BI Buf Waits","int"],
            ["AI Buf Waits","int"],
            ["Writes by APW","int"],
            ["Writes by BIW","int"],
            ["Writes by AIW","int"],
            ["Buffer Hits","int"],
            ["Primary Hits","int"],
            ["Alternate Hits","int"],
            ["DB Size","int64"],
            ["BI Size","int64"],
            ["AI Size","int64"],
            ["FR chain","int"],
            ["RM chain","int"],
            ["Shared Memory","int64"],
            ["Segments","int"],
            ["Servers","int"],
            ["Users","int"],
            ["Local","int"],
            ["Remote","int"],
            ["Batch","int"],
            ["Apws","int"],
            ["Maximum number of users (-n)","int"],
            ["Current size of locking table (-L)","int"],
            ["Locking table high water mark","int"],
            ["Locking table entries in use","int"],
            ["latchtimeouts","int"]]

def getNumericValue(inputString):
    if not isinstance(inputString, basestring) :
        return inputString
    if inputString.endswith("%") :
        return int(inputString.rstrip(' %'))
    if inputString.endswith(" GB") :
        return int(inputString.rstrip(' GB')) * 1024 * 1024
    if inputString.endswith(" MB" ) :
        return int(inputString.rstrip(' MB')) * 1024
    if inputString.endswith(" KB" ) :
        return int(inputString.rstrip(' KB'))
    if inputString.endswith("G") :
        return int(inputString.rstrip(' G')) * 1024 * 1024
    if inputString.endswith("M" ) :
        return int(inputString.rstrip(' M')) * 1024
    if inputString.endswith("K" ) :
        return int(inputString.rstrip(' K'))
    if inputString.endswith(" blocks" ) :
        return int(inputString.rstrip(' blocks'))
    try: 
        val = int(inputString)
        return val
    except :
        return inputString

def obtainInformation () :
    global config, dbs, mydir
    information = {}
    for db in dbs:
        if db.find("db:")  != 0 :
            continue
        dbfile = config.get(db, "db")
        # we check if the .lk file exists, if it does not, no server is running, so it's pointless to run promon 
        lkfile = "{0}lk".format(dbfile[:-2])
        if os.path.isfile(lkfile) :
            try:
                csvOutput = subprocess.check_output(["{0}/promon.sh".format(mydir),dbfile])
                
                properties = {}
                for row in csv.reader(csvOutput.splitlines(), delimiter=':'):
                    properties[row[0]] = getNumericValue(row[1])
                information[db[3:]] = properties
                  
            except subprocess.CalledProcessError as e:
                logging.warn( "No results obtaining checkpoints for {0}!".format(db))
    return information


               
def updateSnmp ():
    global snmpTree, logsnmptree
    
    thetime = str(time.time()).split('.')[0]
    iProperty = 1
    
    pp.add_str("{0}.0".format(iProperty),"TVH Custom Information database agent running")
    pp.add_int("{0}.1".format(iProperty),thetime)
    if logsnmptree  :
        logging.info("{0}.0 : {1}".format(iProperty, "TVH Custom database Information is running status message"))
        logging.info("{0}.1 : {1}".format(iProperty, "TVH Custom database Information last updated timestamp"))
    
    information = obtainInformation() 
    iProperty = iProperty + 1
    
    if logsnmptree :
        logging.info("{0} : {1}".format(iProperty, "Database Names"))
    
    iIdx = 0  
    for name, info in information.items():
        iIdx = iIdx + 1 
        pp.add_str("{0}.{1}".format(iProperty, iIdx) , "{0}".format(name))

                
    for propertyIdx in range(len(snmpTree)):
        propkey=snmpTree[propertyIdx][0]
        proptype=snmpTree[propertyIdx][1]
        iProperty = iProperty + 1
           
        if logsnmptree :
            logging.info("{0} : {1}".format(iProperty,propkey))
        pp.add_int("{0}.{1}".format(iProperty,iIdx),thetime)
        for name, info in information.items():
            try:
                propval=info[propkey]
            except KeyError:
                propval = None 
            if not propval is None :
                propval = getNumericValue(propval)
                if isinstance(propval, (int,long)):
                    if proptype == "int64" :
                        pp.add_cnt_64bit("{0}.{1}".format(iProperty, snmp.PassPersist.encode(name)), propval)
                    else:
                        pp.add_int("{0}.{1}".format(iProperty, snmp.PassPersist.encode(name)), propval) 
                else :
                    pp.add_str("{0}.{1}".format(iProperty, snmp.PassPersist.encode(name)), propval)
    logsnmptree  = False
    
basenode = config.get("settings","basenode")
logsnmptree = config.getboolean("settings", "logsnmptree")
pp = snmp.PassPersist (basenode)
pp.start(updateSnmp, 60)
    