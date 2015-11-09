/*
    AdminServer.java - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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
package com.tvh.infrastructure.openedge;
import com.progress.chimera.adminserver.IAdminServer;
import com.progress.chimera.common.IChimeraRemoteCommand;
import com.progress.common.util.crypto;

import com.progress.ubroker.tools.UBRemoteObject_Stub;
import com.progress.ubroker.tools.UBTRemoteObject_Stub;
import java.rmi.RemoteException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author jankeir
 */
public class AdminServer extends com.progress.ubroker.tools.RemoteCommandClient  {

    
        
    public AdminServer(String hostname, String username, String password) {
        this(hostname, username, password, "20931", "/Chimera", "AppServer");
    }

    public AdminServer(String hostname, String username, String password, String rmiPort) {
        this(hostname, username, password, rmiPort, "/Chimera", "AppServer");
    }

    @Override
    public IChimeraRemoteCommand connect(String string) {
        return super.connect(string); 
    }
    
    
    public AdminServer(String hostname, String username, String password, String rmiPort, String rmiService, String rmiPersonality){
        
        this.m_host = hostname;
        
        this.m_rmiPort = rmiPort;
        this.m_rmiService = rmiService;
        this.m_personality = rmiPersonality;

        crypto crypto1 = new crypto();

        this.m_userName = crypto1.encrypt(username);
        this.m_password = crypto1.encrypt(password);

        IChimeraRemoteCommand remoteCmd;
        remoteCmd = this.connect(null);

        try {
            this.m_adminStub = this.m_adminConStub.connect(this.m_userName, this.m_password);
        } catch (RemoteException ex) {
            Logger.getLogger(AdminServer.class.getName()).log(Level.SEVERE, null, ex);
        }
        
    }
    
    public List<Broker> getBrokers(){
        List<Broker> brokers = new ArrayList<>();
        
        IAdminServer iAdminServer = this.m_adminStub;
        
        try {
            Vector pluginVector = iAdminServer.getPlugins("com.progress.ubroker.tools.UBRemoteObject"); 

            Enumeration plugins = pluginVector.elements();

            while (plugins.hasMoreElements()) {
                Object element = plugins.nextElement();
                UBRemoteObject_Stub stub = (UBRemoteObject_Stub) element;

                if ( stub.getDisplayName().equals("AppServer") || stub.getDisplayName().equals("WebSpeed")  ) {
                    Enumeration children = stub.getChildren();
                    if (children != null)
                        while (children.hasMoreElements()) {
                            Object child = children.nextElement();
                            UBTRemoteObject_Stub childStub = (UBTRemoteObject_Stub) child;
                            brokers.add(new Broker(this, childStub));
                        }
                }
            }
        } catch (RemoteException remoteException) {
            remoteException.printStackTrace();
        }
        
        return brokers;
    }
    
    
}
