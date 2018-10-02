# oesnmp
Expose OpenEdge infrastructure to *any* monitoring platform

OESNMP is a set of utilites to expose information about OpenEdge Appservers, Databases and related infrastructure to Monitoring systems supporting SNMP. This allows you to notice unusual behaviour, verify performance tuning has the desired results, warn you before problems result in downtime,... 

Tools like Promon/ProTop are great for real time monitoring, looking at changes and problems in real time, but they don't allow you to find out how the current trends compare to yesterday, last week, last month, last year,... One of the purposes of OESNMP is to fill that gap (but NOT to replace them, for realtime monitoring while resolving issues, the instant updating nature of protop/promon remains indispensible!)

OESNMP was initially developed with OpenEdge 10.2B and is currently tested on 11.3. 

![Screenshot of resulting graphs in zabbix](https://raw.githubusercontent.com/jankeirse/oesnmp/master/support/screenshot.png)

## Requirements
### net-snmp
All OESNMP scripts are started from net-snmp.  More information at [http://www.net-snmp.org/](http://www.net-snmp.org/)

All scripts are added to net-snmp under OID .1.3.6.1.4.1.42674 , this is an OID assigned by [IANA](http://www.iana.org/) to TVH. If you want to contribute to OESNMP and add more information to the OID tree please do not invent new numbers to avoid collisions. You can contact jan <dot> keirse <at> tvh <dot> com to get a unique number under this OID.

### SNMP_PASSPERSIST
[snmp_passpersist](https://github.com/nagius/snmp_passpersist) is used for the communication between the scripts and net-snmp

### OpenEdge
You need OpenEdge installed to run most tools, some parts need to run on the actual database server, others can be run on a remote server used for monitoring, or on the actual server.

## Components
![Image of the oesnmp components](https://raw.githubusercontent.com/jankeirse/oesnmp/master/support/structure.png)

### asbmansnmp.sh
This is used to monitor AppServers and Webspeed Brokers.  It does not have to run on the server that runs the appservers, but does need an OpenEdge Installation that can run asbman. 

### promon.py
This is used to expose information about your database obtained from promon. This must be run on the same server that runs the database. The intent is to eventually replace it with vst.py entirely. 

### vst.py
Some information we wanted to expose wat not available in promon, so we started exposing information by dumping data from the vst's. 

### wrkdirmon.py
This script can be used to monitor working directory contents. It provides information about the size of DBI, LBI and srt files and filesizes. 

### pasoe.py
This script can be used to expose the metrics that are accesible through the REST api with SNMP. It is usefull for monitoring systems that don't allow to interpret REST api's for determining metrics.

### zabbix template
the support folder contains an export of some templates that can be used in [Zabbix](http://www.zabbix.com/) to monitor your servers.

## Installation
Copy the contents of the deploy folder to /opt/pyprogram/oesnmp. Set the proper executeable bits:
chmod +x asbmansnmp.sh promon.exp promon.py promon.sh vst.py vst.sh wrkdirmon.py

Install and configure net-snmp. As long as you can not run 
```
snmpwalk -v2c -c <yourcommunitystring> localhost 
```

and get some output, you should not expect oesnmp to work and should read up on net-snmp first. 

Also make sure that  .1.3.6.1.4.1.42674 is exposed, to your community string. On a standard centos 7 installation this will need something like this in /etc/snmp/snmpd.conf: 
```
view    systemview    included   .1.3.6.1.4.1.42674
```

Install snmp_passpersist. IE on CentOS 7. with EPEL added:
```shell
sudo yum install pip
sudo pip install snmp_passpersist
```

If you don't want to install pip, you can also copy the snmp_passpersist.py script toe /opt/pyprogram/oesnmp/


Next configure the following components as desired. If you want to test a component, you can run it from the shell and run the DUMPALL command to see if you get proper output (OID's with values) or error messages.


### asbmansnmp.sh
Add the following line to /etc/snmp/snmpd.conf:

```
pass_persist .1.3.6.1.4.1.42674.0 /bin/sh /opt/pyprogram/oesnmp/asbmansnmp.sh
```

In /opt/jlib/commons-io/commons-io/1.4/ put [http://central.maven.org/maven2/commons-io/commons-io/1.4/commons-io-1.4.jar](http://central.maven.org/maven2/commons-io/commons-io/1.4/commons-io-1.4.jar)

In /opt/jlib/org/python/jython/2.7.0/ put [http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7.0/jython-standalone-2.7.0.jar](http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7.0/jython-standalone-2.7.0.jar)

In /opt/pyprogram/oesnmp/asbmansnmp.sh update DLC, OEMGMT and WRKDIR to match your system. If you have an older Progress Version like 10.2B you will need a java 1.7+ installation and update JAVA_HOME. 

Now update /opt/pyprogram/oesnmp/asbmansnmp.cfg, you typically only need to add one or more server sections.
As of 2015-10-20 you need the latest unreleased version of snmp_passpersist because it contains a fix to work on windows that is also required for jython. You could just download https://github.com/nagius/snmp_passpersist/blob/master/snmp_passpersist.py and put it in the /opt/pyprogram/oesnmp folder if you don't want to install it systemwide.   

### promon.py

Expect must be installed on your system to run this.  sudo yum install expect on Centos/Redhat. 

Add the following line to /etc/snmp/snmpd.conf

'''
pass_persist .1.3.6.1.4.1.42674.2 /opt/pyprogram/oesnmp/promon.py
'''

In promon.exp update the following line to match your installation:
```tcl
set dlc "/usr/dlc" 
```

In promon.cfg list the databases you want to monitor.


### vst.py

Add the following line to /etc/snmp/snmpd.conf
```
pass_persist .1.3.6.1.4.1.42674.3 /opt/pyprogram/oesnmp/vst.py
```

Update at least the following lines in /opt/pyprogram/oesnmp/vst.sh:
```shell
export DLC=/usr/dlc
# your connection strings, comma seperated
export CONNECTIONSTRINGS="-db /usr/wrk/sports2000.db"
```
You may also have to update the _progres command line at the end of the file to match your desired startup parameters. 

### wrkdirmon.py
Add the following line to /etc/snmp/snmpd.conf
```
pass_persist .1.3.6.1.4.1.42674.4 /opt/pyprogram/oesnmp/wrkdirmon.py
```
Add working dir sections as required to /opt/pyprogram/oesnmp/wrkdirmon.cfg

### pasoe.py
Add the following line to /etc/snmp/snmpd.conf
```
pass_persist .1.3.6.1.4.1.42674.13 /opt/pyprogram/oesnmp/pasoe.py
```
Configure the servers you want to monitor in /opt/pyprogram/oesnmp/pasoe.cfg. The script has been tested with only one application per server and only with webhandler.

### 
## Todo

### Selinux support
Document how to configure selinux to support oesnmp, it can be done but requires some policies. 

### Better Averages
Currently some averages like request duration are based on the request duration since server start. It would be better to have request duration for the last minute, but this requires extra data to be exposed by PSC. 

Vote here if you want this: https://community.progress.com/community_groups/products_enhancements/i/openedge/visibility_of_total_request_duration_on_appserver


### promon replacement
It would be better to merge everything from promon.py into vst.py and determine it with the VST's. This could lift the expect requirement. 

### per table/index statistics
I don't know how to handle this properly in our monitoring system for thousands of tables, so I haven't implemented it yet, but it should be easy for smaller databases.

### Pacific Application server for OpenEdge
This will not be added to OESNMP: Use JMX monitoring for PAS instead.


###
## Additional documentation
There's a google document showing the various OID's here: https://goo.gl/Zi8qHx

A presentation about the product is available here: https://goo.gl/rfUmPX 
