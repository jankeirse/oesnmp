#!/bin/bash
# promon.sh - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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
# redirect /dev/zero as input to exepct, otherwise 
# expect will 'steal' stdin from the calling python 
# process

# Determine the folder we are in: 
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

${DIR}/promon.exp  $1 < /dev/zero   2>&1 
