/*
    TestAdminServer.java - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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
package com.tvh.infrastructure.openedge.test;

import com.tvh.infrastructure.openedge.AdminServer;
import com.tvh.infrastructure.openedge.Broker;
import com.tvh.infrastructure.openedge.BrokerStatus;
import java.rmi.RemoteException;
import java.util.List;

public class TestAdminServer {

    public static void main(String[] args) throws RemoteException {
        
        AdminServer srv = new AdminServer("somehost", "someuser", "somepw");
        List<Broker> brokers = srv.getBrokers();
        
        for(Broker b: brokers ) {
            BrokerStatus status = b.getStatus();
            if (b.getBrokerName().equals( "someappservername"))
                System.out.println(status.getMaxAgents());
        }
        
    }
}
