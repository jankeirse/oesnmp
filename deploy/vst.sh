#!/bin/bash
# vst.sh - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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

# your DLC
export DLC=/usr/dlc
# your connection strings, comma seperated
export CONNECTIONSTRINGS="-db /usr/wrk/sports2000.db"

# Determine the folder we are in: 
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
${DLC}/bin/_progres -h 20 -b -E -d dmy -h 20 -Mm 16000 -tmpbsize 8 -t -cpinternal iso8859-15 -cpstream utf-8 -rereadnolock -T /ramdisk2 -nosavepoint -param "${CONNECTIONSTRINGS}" -p ${DIR}/pexportvst.p -debugalert | cat
