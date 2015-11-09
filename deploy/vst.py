#!/usr/bin/python -u
# vst.py - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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
# Make sure that vst.sh is modified to start a progress session with the 
# appropriate databases connected.   
# Make sure to populate vst.cfg in the same folder as vst.py like this:
#
# [settings]
# logfile = logfilepath
# basenode = .1.3.6.1.4.1.42674.2 


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
config.read( "{0}/vst.cfg".format(mydir))

# set up logging
logging.basicConfig( filename = config.get("settings","logfile"), level=logging.INFO,format='%(asctime)s:' + logging.BASIC_FORMAT)

dbs = config.sections()

def obtainInformation () :
    global config, dbs, mydir
    information = {}
    try:
        csvOutput = subprocess.check_output(["{0}/vst.sh".format(mydir)])
        properties = {}
        information = csv.reader(csvOutput.splitlines(), delimiter=';')
    except subprocess.CalledProcessError as e:
        logging.warn( "No results obtaining vst information!")
    return information


                
def updateSnmp ():
    global snmpTree
    
    thetime = str(time.time()).split('.')[0]
    pp.add_str("{0}".format(0),"TVH Custom Information vst agent running")
    pp.add_int("{0}".format(1),thetime)
    
    information = obtainInformation() 
    iLatch = 0
    iWait = 0
    iBuffer = 0 
    for info in information:
        if info[0] == "latch":
            iLatch = iLatch + 1
            pp.add_str("2.{0}.{1}".format(2,iLatch), "{0}-{1}".format(info[1],info[3]) ) # db name - latch name
            latchNameOid = snmp.PassPersist.encode("{0}-{1}".format(info[1],info[3]))
            pp.add_int("2.{0}.{1}".format(3,latchNameOid), info[4] ) # _latch-Hold 
            pp.add_int("2.{0}.{1}".format(4,latchNameOid), info[5] ) # _latch-QHold
            pp.add_str("2.{0}.{1}".format(5,latchNameOid), info[6] ) # _latch-Type
            pp.add_int("2.{0}.{1}".format(6,latchNameOid), info[7] ) # _latch-Wait
            pp.add_int("2.{0}.{1}".format(7,latchNameOid), info[8] ) # _latch-Lock
            pp.add_int("2.{0}.{1}".format(8,latchNameOid), info[9] ) # _latch-Spin
            pp.add_int("2.{0}.{1}".format(9,latchNameOid), info[10] ) # _latch-Busy
            pp.add_int("2.{0}.{1}".format(10,latchNameOid), info[11] ) # _latch-LockedT
            pp.add_int("2.{0}.{1}".format(11,latchNameOid), info[12] ) # _latch-LockT
            pp.add_int("2.{0}.{1}".format(12,latchNameOid), info[13] ) # _latch-WaitT
        elif info[0] == "wait":
            iWait = iWait + 1
            waitNameOid = snmp.PassPersist.encode("{0}-{1}".format(info[1],info[2])) 
            pp.add_str("3.{0}.{1}".format(1,iWait),"{0}-{1}".format(info[1],info[2])) # DB name - type of wait
            pp.add_int("3.{0}.{1}".format(2,waitNameOid), int(info[3]))
        elif info[0] == "bufferactivity":
            iBuffer = iBuffer + 1
            bufferNameOid = snmp.PassPersist.encode("{0}-{1}".format(info[1],info[2]))
            pp.add_str("4.{0}.{1}".format(1,iBuffer), "{0}-{1}".format(info[1],info[2])) # Db name - buffer number
            pp.add_cnt_64bit("4.{0}.{1}".format(2,bufferNameOid), info[3]) # _Buffer-LogicRds 
            pp.add_cnt_64bit("4.{0}.{1}".format(3,bufferNameOid), info[4]) # _Buffer-LogicWrts
            pp.add_cnt_64bit("4.{0}.{1}".format(4,bufferNameOid), info[5]) # _Buffer-OSWrts
            pp.add_cnt_64bit("4.{0}.{1}".format(5,bufferNameOid), info[6]) # _Buffer-OsRds
            pp.add_cnt_64bit("4.{0}.{1}".format(6,bufferNameOid), info[7]) # _Buffer-Trans
            
            

basenode = config.get("settings","basenode")

pp = snmp.PassPersist (basenode)
pp.start(updateSnmp, 60)
    