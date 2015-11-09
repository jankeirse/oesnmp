#!/bin/bash
# asbmansnmp.sh - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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
export DLC=/usr/dlc
OEMGMT=/usr/oemgmt
JAVA_HOME=${DLC}/jdk
WRKDIR=/usr/wrk
JLIB=/opt/jlib
COMMONSIO=${JLIB}/commons-io/commons-io/1.4/commons-io-1.4.jar

JYTHON=${JLIB}/org/python/jython/2.7.0/jython-standalone-2.7.0.jar
export JYTHONPATH=/usr/lib/python2.7/site-packages
export PATH=${PATH}:${DLC}/bin:${DLC}/lib
export LD_LIBRARY_PATH=${DLC}/lib

# Determine the folder we are in: 
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

ADMSRV=${DIR}/AdminServer.jar

${JAVA_HOME}/bin/java -Dfile.encoding=UTF-8 -DInstall.Dir=${DLC} -DWork.Dir=${WRKDIR} \
	-Djava.security.policy=${DLC}/java/java.policy \
	-classpath ${JYTHON}:${DLC}/java/progress.jar:${DLC}/java/java/messages.jar:${OEMGMT}/jars/fathom.jar:${COMMONSIO}:${ADMSRV} \
	org.python.util.jython ${DIR}/AsbManSnmp.py

