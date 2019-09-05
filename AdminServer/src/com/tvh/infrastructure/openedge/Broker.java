/*
    Broker.java - Copyleft 2013-2019 TVH Parts Holding NV. <jan.keirse@tvh.com>
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

import com.progress.chimera.common.IChimeraRemoteCommand;
import com.progress.ubroker.tools.UBTRemoteObject_Stub;
import com.progress.ubroker.util.ToolRemoteCmdDescriptor;
import com.progress.ubroker.util.ToolRemoteCmdStatus;
import java.io.PrintStream;
import java.rmi.RemoteException;
import java.util.Enumeration;
import java.util.HashMap;
import org.apache.commons.io.output.NullOutputStream;

public class Broker {
    public enum BrokerType {
        ASBROKER, WSBROKER
    };
    
    private AdminServer server ;
    private UBTRemoteObject_Stub remoteStub;
    private BrokerType type;
    
    public Broker(AdminServer server, UBTRemoteObject_Stub remoteStub) throws RemoteException {
        this.server = server;
        this.remoteStub = remoteStub;
        this.type = "UBroker.AS".equals(remoteStub.getDisplayName()) ? BrokerType.ASBROKER : BrokerType.WSBROKER;        
    }

    public AdminServer getServer() {
        return server;
    }

    public String getBrokerName() throws RemoteException {
        return remoteStub.getDisplayName();
    }

    public BrokerType getType() {
        return type;
    }
    
    public BrokerStatus getStatus() throws RemoteException {
        PrintStream nulloutput = new PrintStream(new NullOutputStream());
        PrintStream out = System.out;
        PrintStream err = System.err;
        int maxAgents  = 0;
        int maxClients = 0;
        try{ 
            System.setOut(nulloutput);
            System.setErr(nulloutput);

            IChimeraRemoteCommand connect = server.connect(getBrokerName());
            int result = connect.runIt(new String[]{(type == BrokerType.ASBROKER ? "AS" : "WS"),"q"});
            if (connect.getSystemOutput().contains("(8313)")){
                return new BrokerStatus(BrokerStatus.RunningStatus.STOPPED);
            }
            connect.runIt(new String[]{(type == BrokerType.ASBROKER ? "AS" : "WS"),"z", "maxSrvrInstance"});
            maxAgents = Integer.parseInt(connect.getStructuredSystemOutput().get("maxSrvrInstance").toString());
            connect.runIt(new String[]{(type == BrokerType.ASBROKER ? "AS" : "WS"),"z", "maxClientInstance"});
            maxClients = Integer.parseInt(connect.getStructuredSystemOutput().get("maxClientInstance").toString());
            
        } finally {
            System.setOut(out);
            System.setErr(err);
        }
        
        HashMap<Integer,String> labels = new HashMap<>(15);
        HashMap<String,String> values = new HashMap<>(15);
        ToolRemoteCmdDescriptor cmd = new ToolRemoteCmdDescriptor();
        
        cmd.makeGetSummaryStatusLblPkt("Ubroker." +  (type == BrokerType.ASBROKER ? "AS." : "WS.") + getBrokerName());
        ToolRemoteCmdStatus labelFetcher = remoteStub.getRemoteManageObject().doRemoteToolCmd(cmd);
        Enumeration summaryLabels = labelFetcher.fetchGetSummaryStatuslblStatus();
        if (summaryLabels != null) {

            int i = 0 ;
            while(summaryLabels.hasMoreElements()) {
                String label = (String)summaryLabels.nextElement();
                labels.put(i, label.trim());
                i++;
            }
            
            cmd.makeGetSummaryStatusDataPkt( (type == BrokerType.ASBROKER ? "AS." : "WS.") + getBrokerName() );
            ToolRemoteCmdStatus statusFetcher = remoteStub.getRemoteManageObject().doRemoteToolCmd(cmd);
            Enumeration summaryValues = statusFetcher.fetchGetSummaryStatusDataStatus();
            i = 0;
            while ( summaryValues.hasMoreElements() ){
                String value = (String)summaryValues.nextElement();
                values.put(labels.get(i), value.trim());
                i++;
            }
        }
        return new BrokerStatus(values, maxAgents, maxClients);
        
    }
    
}
