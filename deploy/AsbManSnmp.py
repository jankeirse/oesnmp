# AsbManSnmp.py - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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
# make sure to populate asbmansnmp.cfg in the same folder as AsbManSnmp.py like this:
# [settings]
# logfile = logfilepath
# timeout = 5
# basenode = .1.3.6.1.4.1.42674.0 
# # Log the snmp tree in the logfile: 
# logsnmptree=true 
#
# [server:randomName]
# servername = realHostname
# port = 20931
# username = userForAsbMan
# password = passwordForUserAbove 
#
# [server:randomName2]
# servername = realHostname2
# ...

from com.tvh.infrastructure.openedge import AdminServer
from com.tvh.infrastructure.openedge.BrokerStatus import RunningStatus
import logging
import ConfigParser
import time
import snmp_passpersist as snmp
import sys, os, os.path, inspect
from java.io import PrintStream
from java.lang import System as javasystem
from org.apache.commons.io.output import NullOutputStream
from java.lang import NullPointerException
from java.rmi import ServerException
 

if '__file__' not in locals():
    __file__ = inspect.getframeinfo(inspect.currentframe())[0]

config = ConfigParser.ConfigParser()
config.read( "{0}/asbmansnmp.cfg".format(os.path.dirname(os.path.abspath(__file__))))

# set up logging
logging.basicConfig( filename = config.get("settings","logfile"), level=logging.INFO,format='%(asctime)s:' + logging.BASIC_FORMAT)

servers = config.sections()
timeout = config.getint("settings","timeout")
debug  = config.getboolean("settings","debug")

#discard all java output, it would mess up pass_persist communication 
if not debug:
    nulloutput = PrintStream(NullOutputStream())
    javasystem.setErr(nulloutput)
    javasystem.setOut(nulloutput)

# list of information we want to write to files / snmp
properties = [ ['ActiveServers', 1], 
               ['RqDuration', ["Max","Avg"]], 
               ['RqWait', ["Max","Avg"]],
               ['ActiveClients', ['Now','Peak']],
               ['TotalRequests', 1],
               ['BusyServers', 1],
               ['AvailableServers', 1],
               ['ClientQueueDepth', ['Cur','Max']],
               ['LockedServers', 1],
               ['Status', 1],
               ['MaxAgents', 1],
               ['MaxClients', 1]               
             ]
statusses = { "ACTIVE": 3,
              "STARTING": 2,
              "STOPPING": 1,
              "STOPPED": 0
             }

class Unbuffered:
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)
    

def obtainInformation () :
    global config, servers, timeout
    information = {}
    for server in servers:
        if server.find("server:")  != 0 :
            continue
        servername = config.get(server, "servername")
        try:
            explorer = AdminServer(servername, config.get(server,"username"), config.get(server,"password"), config.get(server, "port"))
            brokers = explorer.getBrokers()
            information[servername] = {} 
            for broker in brokers:
                information[servername][broker.getBrokerName()] = broker.getStatus()
        except ServerException as e:
            logging.warn( "No results obtaining appserver status for {0}, possibly admin server has incompatible OE version!".format(servername))  
        except NullPointerException as e:
            logging.warn( "No results obtaining appserver status for {0}, possibly admin server is down!".format(servername))
    return information


                
def updateSnmp ():
    global properties, logsnmptree
    
    thetime = str(time.time()).split('.')[0]
    iProperty = 1
    
    pp.add_str("{0}.{1}".format(iProperty,0),"TVH Custom Information agent running")
    pp.add_str( "{0}.{1}".format(iProperty,1), thetime) 
    if logsnmptree  :
        logging.info("{0}.0 : {1}".format(iProperty, "TVH Custom Information"))
        logging.info("{0}.1 : {1}".format(iProperty, "time stamp"))
    
    information = obtainInformation() 
    iProperty = iProperty + 1
    iIdx = 1
    if logsnmptree :
        logging.info("{0} : {1}".format(iProperty, "Appserver Names"))
     
    for name, info in information.items():
        for appserverName, serverInfo in info.items():
            iIdx = iIdx + 1 
            pp.add_str("{0}.{1}".format(iProperty, iIdx) , "{0}.{1}".format(name, appserverName))

                
    for propertyIdx in range(len(properties)):
        propkey=properties[propertyIdx][0]
        values=properties[propertyIdx][1]
        iProperty = iProperty + 1
        
        if values == 1:
            if logsnmptree :
                logging.info("{0} : {1}".format(iProperty,propkey))
            for name, info in information.items():
                for appserverName, serverinfo in info.items():
                    # call method getWHATEVERISINPROPKEY on serverinfo object
                    propval = getattr(serverinfo,"get" + propkey)()
                    if not propval is None :
                        if propkey == "Status" :
                                propval = statusses["{0}".format(propval)]
                        if isinstance(propval, (int,long)):
                            pp.add_int("{0}.{1}".format(iProperty, snmp.PassPersist.encode("{0}.{1}".format(name,appserverName))), propval)
                        else :
                            pp.add_str("{0}.{1}".format(iProperty, snmp.PassPersist.encode("{0}.{1}".format(name,appserverName))), propval)
        else :
            for i in range(len(values)):
                if logsnmptree  :
                    logging.info("{0}.{1} : {2} {3}".format(iProperty, i, propkey,values[i] ))
                
                for name, info in information.items():
                    for appserverName, serverinfo in info.items():
                        # call method getWhateverisinpropkeyWhateverisinValues[i] on serverinfo object
                        propval =  getattr(serverinfo,"get" + propkey + values[i])() 
                        if not propval is None :
                            if isinstance(propval, (int,long)):
                                pp.add_int("{0}.{1}.{2}".format(iProperty,i, snmp.PassPersist.encode("{0}.{1}".format(name,appserverName))),propval)
                            else:
                                pp.add_str("{0}.{1}.{2}".format(iProperty,i, snmp.PassPersist.encode("{0}.{1}".format(name,appserverName))),propval)
    
    logsnmptree  = False
    
sys.stdout=Unbuffered(sys.stdout)
basenode = config.get("settings","basenode")
logsnmptree = config.getboolean("settings", "logsnmptree")
pp = snmp.PassPersist (basenode)
try:
    pp.start(updateSnmp, 60)
except SystemExit as e:
    os._exit(0)
    