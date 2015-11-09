#!/usr/bin/python
'''
Created on 22-jan.-2014

This uses pyzabbix, obtained from https://github.com/lukecyca/pyzabbix/wiki

@author: jankeir
'''

from pyzabbix import ZabbixAPI
import ConfigParser, os, random

config = ConfigParser.ConfigParser()
config.read( "{0}/settings.cfg".format(os.path.dirname(os.path.abspath(__file__))))

server = config.get("settings", "server")
user = config.get("settings","user")
password = config.get("settings","password")

zapi= ZabbixAPI(server)
# Enable HTTP auth
zapi.session.auth = (user, password)

# Disable SSL certificate verification
zapi.session.verify = False

# Specify a timeout (in seconds)
zapi.timeout = 5.1

zapi.login(user,password)

def createScreenWithAllGraphsOfAType(screenname, graphname,graphheight):
    print "creating screens {0} with all graphs of type {1}".format(screenname, graphname)
    screens = zapi.screen.get(output="extend",filter={"name": screenname })
    graphs = zapi.graph.get(output="extend",search={"name": graphname},selectGraphItems=True);
    items = []
    i = 0
    
    graphs = sorted(graphs, key=lambda graph: graph["name"].lower())
    for graph in graphs:
        items.append({"resourcetype": 0, 
                      "resourceid":graph["graphid"],
                      "rowspan": 1,
                      "colspan":1,
                      "height": graphheight,
                      "width":900,
                      "x": 0,
                      "y": i})
        i = i + 1
    
    if len(screens) > 0 :
        zapi.screen.update(screenid=screens[0]["screenid"],
                           name=screenname,
                           vsize=len(graphs),
                           hsize=1,
                           screenitems=items)
    else:
        zapi.screen.create(name=screenname,vsize=len(graphs),hsize=1,screenitems=items)
        
def createScreenPerHostWithAllGraphsOfAType(screenname, graphname, graphheight):
    print "creating screens {0} per host with all graphs of type {1}".format(screenname, graphname)
    hosts = zapi.host.get(output="extend")
    for host in hosts:
        screens = zapi.screen.get(output="extend",filter={"name": screenname.format(host["name"]) })
        graphs = zapi.graph.get(output="extend",search={"name": graphname, "hostid": host["hostid"]},filter={"hostid":host["hostid"]}, selectGraphItems=True);
        if len(graphs) > 0:
            items = []
            i = 0
            graphs = sorted(graphs, key=lambda graph: graph["name"].lower())
            for graph in graphs:
                items.append({"resourcetype": 0, 
                              "resourceid":graph["graphid"],
                              "rowspan": 1,
                              "colspan":1,
                              "height": graphheight,
                              "width":900,
                              "x": 0,
                              "y": i})
                i = i + 1
        
            if len(screens) > 0 :
                zapi.screen.update(screenid=screens[0]["screenid"],
                                   name=screenname.format(host["name"]),
                                   vsize=len(graphs),
                                   hsize=1,
                                   screenitems=items)
            else:
                zapi.screen.create(name=screenname.format(host["name"]),vsize=len(graphs),hsize=1,screenitems=items)        

def allItemsOfATypeOnAGraphPerHost(itemtype,graphname):
    print "creating graph {0} with all items of type {1}".format(graphname, itemtype)
    r = lambda: random.randint(0,255)    
    hosts = zapi.host.get(output="extend")
    for host in hosts:
        items = zapi.item.get(filter={"hostid": host["hostid"]},search={"name": itemtype},output="extend")
        if len(items) > 0 :
            graphitems = []
            items = sorted(items,key=lambda item: item["name"].lower(), reverse=True)
            sortOrder = 1
            for item in items:
                graphitems.append({"itemid": item["itemid"], "color" : '%02X%02X%02X' % (r(),r(),r()), "sortorder": sortOrder })
                sortOrder = sortOrder + 1;
                
            currentgraph = zapi.graph.get(filter={"hostid":host["hostid"], "name":graphname.format(host["name"])})
            if len(currentgraph) > 0:
                zapi.graph.update(graphid=currentgraph[0]["graphid"],
                                  hostid=host["hostid"],
                                  graphtype=1,
                                  width=900,
                                  height=600,
                                  name=graphname.format(host["name"]),
                                  gitems=graphitems)
            else:
                zapi.graph.create(hostid=host["hostid"],
                                  width=900,
                                  height=600,
                                  graphtype=1,
                                  name=graphname.format(host["name"]),
                                  gitems=graphitems)
                
                
def createAppserverScreen():
    print "Creating appserver screen"
    # Search all Client queue Depth Graphs, this will allow to search all appserver names and as a result all graphs for those appservers
    graphs = zapi.graph.get(search={"name": "Client Queue Depth on " },  output="extend")
    appservers = []
    for graph in graphs:
        graphName = graph["name"]
        appserverName = graphName[22:]
        if not appserverName in appservers:
            appservers.append(appserverName)
            
    for appserver in appservers:
        graphs = zapi.graph.get(search={ "name": appserver}, output="extend")
        graphs = sorted(graphs, key=lambda graph:graph["name"].lower())
        graphsForScreen = []
        i = 0
        for graph in graphs:
            if graph["name"].endswith(appserver):
                graphsForScreen.append( {"resourcetype": 0, 
                                          "resourceid":graph["graphid"],
                                          "rowspan": 1,
                                          "colspan":1,
                                          "height": 200,
                                          "width":900,
                                          "x": 0,
                                          "y": i})
                i = i + 1
        if len(graphsForScreen) > 0 :
            screenName = "Appserver information for {0}".format(appserver)
            screens = zapi.screen.get(output="extend",filter={"name": screenName })
            if len(screens) > 0 :
                #print 'Updating {0}'.format(screenName)
                zapi.screen.update(screenid=screens[0]["screenid"],
                                   name=screenName,
                                   vsize=len(graphsForScreen),
                                   hsize=1,
                                   screenitems=graphsForScreen)
            else:
                #print 'Creating {0}'.format(screenName)
                zapi.screen.create(name=screenName,vsize=len(graphsForScreen),hsize=1,screenitems=graphsForScreen)
                
def createDatabaseScreen():
    print "Creating database screen"
    # Search all Record lock wait Graphs, this will allow to search all database names and as a result all graphs for those databases
    graphs = zapi.graph.get(search={"name": "Record lock waits on database " },  output="extend")
    databases = []
    for graph in graphs:
        graphName = graph["name"]
        databaseName = graphName[30:]
        if not databaseName in databases:
            databases.append(databaseName)
            
    for database in databases:
        graphs = zapi.graph.get(search={ "name": "database " + database}, output="extend")
        graphs = sorted(graphs, key=lambda graph:graph["name"].lower())
        graphsForScreen = []
        i = 0
        for graph in graphs:
            if graph["name"].endswith("database " + database):
                graphsForScreen.append( {"resourcetype": 0, 
                                          "resourceid":graph["graphid"],
                                          "rowspan": 1,
                                          "colspan":1,
                                          "height": 200,
                                          "width":900,
                                          "x": 0,
                                          "y": i})
                i = i + 1
        if len(graphsForScreen) > 0 :
            screenName = "Database information for {0}".format(database)
            screens = zapi.screen.get(output="extend",filter={"name": screenName })
            if len(screens) > 0 :
                #print 'Updating {0}'.format(screenName)
                zapi.screen.update(screenid=screens[0]["screenid"],
                                   name=screenName,
                                   vsize=len(graphsForScreen),
                                   hsize=1,
                                   screenitems=graphsForScreen)
            else:
                #print 'Creating {0}'.format(screenName)
                zapi.screen.create(name=screenName,vsize=len(graphsForScreen),hsize=1,screenitems=graphsForScreen)                
                

def listHasItemWithValue(thelist, itemid, value):
    for item in thelist:
        if item[itemid] == value:
            return True
    return False          
    
def createITService():
    triggers = zapi.trigger.get(output="extend",search={"description": "TVH Application general availability test"})
    services = zapi.service.get(output="extend")
    
    for trigger in triggers:
        if not listHasItemWithValue(services, "triggerid", trigger['triggerid']) :
            zapi.service.create(name=trigger["description"], parentid=1, triggerid=trigger["triggerid"], algorithm='1', goodsla='99.9000', showsla='1', sortorder='0')

          
createScreenWithAllGraphsOfAType("Database activity", "Database activity for ", 150)

allItemsOfATypeOnAGraphPerHost("Record Reads Rate for ", "Record read rate across all databases on {0}")
createScreenWithAllGraphsOfAType("Latch timeouts", "Latch timeouts on ", 150) 
allItemsOfATypeOnAGraphPerHost("Latch timeouts on ", "All latch timeouts on {0}") 
createScreenPerHostWithAllGraphsOfAType("IO Summaries for {0}", "IO Summary for ", 150)
createScreenPerHostWithAllGraphsOfAType("Disk space usage on {0}", "Disk space usage ", 150) 
createScreenPerHostWithAllGraphsOfAType("Volume space usage on {0}", "Netapp Volume ", 150)
allItemsOfATypeOnAGraphPerHost("Specific timeouts on latch ", "All specific latch timeouts on {0}") 
createScreenWithAllGraphsOfAType("Specific Latch timeouts", "Specific timeouts on latch ", 150) 
createAppserverScreen()
allItemsOfATypeOnAGraphPerHost("Commit rate for ", "All commit rates on {0}") 
allItemsOfATypeOnAGraphPerHost("Specific timeouts on latch sports2000-", "All specific latch timeouts at {0} on database sports2000")
createScreenWithAllGraphsOfAType("Latch timeouts", "All specific latch timeouts ", 150) 

allItemsOfATypeOnAGraphPerHost("DB Client connections waiting on a", "Number of DB CLients waiting on a record/transaction at {0}")
createScreenPerHostWithAllGraphsOfAType("Process Category CPU Usage on {0}", "Process Category CPU Usage for", 150)             
createScreenPerHostWithAllGraphsOfAType("Process Category Memory Usage on {0}", "Process Category Memory Usage for", 150)

createScreenPerHostWithAllGraphsOfAType("Locks across databases on {0}", "Locks only on database", 150) 
createScreenWithAllGraphsOfAType("CPU Usage (Raw) across all servers", "CPU Usage (Raw)", 100)                         
createScreenPerHostWithAllGraphsOfAType("Current buffer hit rates on {0}", "Current Buffer hit Rate ", 150)  
createScreenWithAllGraphsOfAType("Mail queues", "Mails in queue ", 150)  
createScreenWithAllGraphsOfAType("Latch timeouts", "All specific latch timeouts ", 150)  
createDatabaseScreen()   
createScreenPerHostWithAllGraphsOfAType("Disk space usage on {0}", "Disk space usage ", 150)

