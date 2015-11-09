/*************************************************
    pexportvst.p - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
    This file is part of OESNMP.

    OESNMP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OESNMP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OESNMP.  If not, see <http://www.gnu.org/licenses/>.  
 */
DEFINE VARIABLE hBuffer    AS HANDLE      NO-UNDO.
DEFINE VARIABLE hQuery     AS HANDLE      NO-UNDO.
DEFINE VARIABLE iDb        AS INTEGER     NO-UNDO.
DEFINE VARIABLE cWaittype  AS CHARACTER  NO-UNDO.
DEFINE VARIABLE iWaitcount AS INTEGER    NO-UNDO.

connect-dbs:
DO iDb = 1 TO NUM-ENTRIES(SESSION:PARAMETER):
  timouter:
  DO STOP-AFTER 1 
    ON ERROR UNDO timouter, LEAVE timouter
    ON STOP  UNDO timouter, LEAVE timouter:
    CONNECT VALUE(ENTRY(iDb,SESSION:PARAMETER)) NO-ERROR.
  END. /* timouter */ 
END. /* connect-dbs */

iterate-dbs:
DO iDb = 1 TO NUM-DBS:
  processing:
  DO 
    ON ERROR UNDO processing, LEAVE processing
    ON STOP  UNDO processing, LEAVE processing:

    /* Statistics about latches */
    CREATE BUFFER hBuffer FOR TABLE LDBNAME(iDb) + '._latch'.
    CREATE QUERY hQuery .

    hQuery:SET-BUFFERS(hBuffer).
    hQuery:QUERY-PREPARE("FOR EACH _latch WHERE _Latch-Name <> '0'").
    hQuery:QUERY-OPEN().

    iterate-latch:
    DO WHILE hQuery:GET-NEXT():
      PUT UNFORMATTED
        "latch" ";"
        LDBNAME(iDb) ";" 
        hBuffer::_Latch-Id ";" 
        hBuffer::_Latch-Name ";" 
        hBuffer::_Latch-Hold ";" 
        hBuffer::_Latch-Qhold ";" 
        hBuffer::_Latch-Type ";" 
        hBuffer::_Latch-Wait ";" 
        hBuffer::_Latch-Lock ";" 
        hBuffer::_Latch-Spin ";" 
        hBuffer::_Latch-Busy ";" 
        hBuffer::_Latch-LockedT ";" 
        hBuffer::_Latch-LockT ";" 
        hBuffer::_Latch-WaitT SKIP.
    END. /* iterate-latch */

    DELETE OBJECT hQuery.
    DELETE OBJECT hBuffer.

    /* statistics about buffer activity */
    CREATE BUFFER hBuffer FOR TABLE LDBNAME(iDb) + "._ActBuffer".
    CREATE QUERY hQuery.
    hQuery:SET-BUFFERS(hBuffer).
    hQuery:QUERY-PREPARE("FOR EACH _ActBuffer").
    hQuery:QUERY-OPEN().
    iterate-actbuffer:
    DO WHILE hQuery:GET-NEXT():
        PUT UNFORMATTED "bufferactivity" ";" 
                        LDBNAME(iDb) ";" 
                        hBuffer::_Buffer-Id ";"
                        hBuffer::_Buffer-LogicRds ";" 
                        hBuffer::_Buffer-LogicWrts ";" 
                        hBuffer::_Buffer-OSWrts ";"
                        hBuffer::_Buffer-OsRds ";"
                        hBuffer::_Buffer-Trans SKIP .
    END. /* iterate-actbuffer */

    DELETE OBJECT hQuery.
    DELETE OBJECT hBuffer.

    /* skip _connect-wait for now, we have reason to believe it causes db crashes */
    IF TRUE THEN
      NEXT iterate-dbs.
    /* Statistics about blocked sessions and what they are waiting for (record lock vs transaction vs ...(is there another possible value for _connect-wait?) */

    ASSIGN cWaittype  = ? 
           iWaitcount = 0.
    CREATE BUFFER hBuffer FOR TABLE LDBNAME(iDb) + '._Connect'.
    CREATE QUERY hQuery.
    hQuery:SET-BUFFERS(hBuffer).
    hQuery:QUERY-PREPARE("FOR EACH _Connect WHERE _Connect._Connect-Wait <> ' -- ' AND _Connect._Connect-Wait <> ? BY _Connect._Connect-Wait").
    hQuery:QUERY-OPEN().
    iterate-connect:
    DO WHILE hQuery:GET-NEXT():
      IF cWaittype = ? THEN /* first record */
        ASSIGN cWaittype = hBuffer::_Connect-Wait.
      IF cWaittype <> hBuffer::_Connect-Wait THEN DO:
        PUT UNFORMATTED "wait" ";" LDBNAME(iDb) ";" TRIM(cWaittype) ";" iWaitcount SKIP.
        ASSIGN cWaittype  = hBuffer::_Connect-Wait
               iWaitcount = 0 .
      END.

      ASSIGN iWaitcount = iWaitcount + 1.  

    END. /* iterate-connect */

    /* The last type won't be logged by the above query because there's no next record with another wait type */
    IF cWaittype <> ? THEN
      PUT UNFORMATTED "wait" ";" LDBNAME(iDb) ";" TRIM(cWaittype) ";" iWaitcount SKIP.
    
    FINALLY:
      IF VALID-HANDLE(hBuffer) THEN
        DELETE OBJECT hBuffer.
      IF VALID-HANDLE(hQuery) THEN
        DELETE OBJECT hQuery.

    END. /* finally */
  END. /* processing */ 
END. /* iterate-dbs */
QUIT.
