/*
    BrokerStatus.java - Copyleft 2013-2015 TVH Group NV. <kalman.tiboldi@tvh.com>
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

import java.util.HashMap;
import java.util.Map.Entry;
import java.util.logging.Level;
import java.util.logging.Logger;

    
public class BrokerStatus {
    public enum OperatingMode  {STATELESS, STATEAWARE, STATERESET, STATEFREE};
    public enum RunningStatus { ACTIVE, STARTING, STOPPING, STOPPED};
    
    private OperatingMode  operatingMode = null ;
    private RunningStatus status = null;
    private Integer brokerPort = null;
    private Long rqWaitMax = null;
    private Long rqWaitAvg = null;
    private Long clientQueueDepthCur = null;
    private Long clientQueueDepthMax = null;
    private Long rqDurationMax = null;
    private Long rqDurationAvg = null;
    private Long activeServers = null;
    private Long activeClientsNow = null;
    private Long activeClientsPeak = null;
    private Integer brokerPid = null;
    private Long busyServers = null;
    private Long availableServers = null;
    private Long lockedServers = null;
    private Long totalRequests = null;
    private Integer maxAgents = null;
    private Integer maxClients = null;

    public BrokerStatus(RunningStatus status){
        this.status = status;
    }
    
    public BrokerStatus(HashMap<String,String> properties, int maxAgents, int maxClients) {
        this.maxAgents = maxAgents;
        this.maxClients = maxClients;
        for(Entry<String,String> entry : properties.entrySet()){
            String[] vals;
            switch (entry.getKey()){
                case "Broker Port": 
                    brokerPort = Integer.parseInt(entry.getValue());
                    break;
                case "Rq Wait (max, avg)": 
                    vals = entry.getValue().split(",");
                    rqWaitMax = Long.parseLong(vals[0].substring(1,vals[0].length() - 3));
                    rqWaitAvg = Long.parseLong(vals[1].substring(1,vals[1].length() - 4));
                    break;
                case "Broker Name": break; // ignore, we know that already
                case "Client Queue Depth (cur, max)": 
                    vals = entry.getValue().split(",");
                    clientQueueDepthCur = Long.parseLong(vals[0].substring(1,vals[0].length()));
                    clientQueueDepthMax = Long.parseLong(vals[1].substring(1,vals[1].length() -1));
                    break;
                case "Rq Duration (max, avg)": 
                    vals = entry.getValue().split(",");
                    rqDurationMax = Long.parseLong(vals[0].substring(1,vals[0].length() - 3));
                    rqDurationAvg = Long.parseLong(vals[1].substring(1,vals[1].length() - 4));
                    break;
                case "Active Agents":
                case "Active Servers" :
                    activeServers = Long.parseLong(entry.getValue());
                    break;
                case "Broker PID":
                    brokerPid = Integer.parseInt(entry.getValue());
                    break;
                case "Total Requests": 
                    totalRequests = Long.parseLong(entry.getValue());
                    break;
                case "Operating Mode": 
                    String mode = entry.getValue();
                    if ("Stateless".equals(mode))
                        operatingMode = OperatingMode.STATELESS;
                    else if ("State-aware".equals(mode))
                        operatingMode = OperatingMode.STATEAWARE;
                    else if ("State-reset".equals(mode))
                        operatingMode = OperatingMode.STATERESET;
                    else if ("State-free".equals(mode))
                         operatingMode = OperatingMode.STATEFREE;
                    else
                        Logger.getLogger(BrokerStatus.class.getName()).log(Level.WARNING, "Unknown operating mode " + mode);
                    break;
                case "Available Agents":
                case "Available Servers": 
                    availableServers = Long.parseLong(entry.getValue());
                    break;
                case "Active Clients (now, peak)": 
                    vals = entry.getValue().split(",");
                    activeClientsNow = Long.parseLong(vals[0].substring(1,vals[0].length()));
                    activeClientsPeak = Long.parseLong(vals[1].substring(1,vals[1].length() -1));
                    break;
                case "Broker Status": 
                    String stat = entry.getValue();
                    if ("ACTIVE".equals(stat))
                        status = RunningStatus.ACTIVE;
                    else if ( "STARTING".equals(stat))
                        status = RunningStatus.STARTING;
                    else if ( "STOPPED".equals(stat))
                        status = RunningStatus.STOPPED;
                    else if ( "STOPPING".equals(stat))
                        status = RunningStatus.STOPPING;
                    break;
                case "Busy Agents": 
                case "Busy Servers": 
                    busyServers = Long.parseLong(entry.getValue());
                    break;
                case "Locked Agents":
                case "Locked Servers": 
                    lockedServers = Long.parseLong(entry.getValue());
                    break;
                default :
                    Logger.getLogger(BrokerStatus.class.getName()).log(Level.WARNING, "Unknown key " + entry.getKey());
                    break;
                
            }
        }
            
    }

    @Override
    public String toString() {
        return "BrokerStatus{" + "operatingMode=" + operatingMode + ", status=" + status + ", brokerPort=" + brokerPort + ", rqWaitMax=" + rqWaitMax + ", rqWaitAvg=" + rqWaitAvg + ", clientQueueDepthCur=" + clientQueueDepthCur + ", clientQueueDepthMax=" + clientQueueDepthMax + ", rqDurationMax=" + rqDurationMax + ", rqDurationAvg=" + rqDurationAvg + ", activeServers=" + activeServers + ", activeClientsNow=" + activeClientsNow + ", activeClientsPeak=" + activeClientsPeak + ", brokerPid=" + brokerPid + ", busyServers=" + busyServers + ", availableServers=" + availableServers + ", lockedServers=" + lockedServers + ", totalRequests=" + totalRequests + '}';
    }

    public OperatingMode getOperatingMode() {
        return operatingMode;
    }

    public RunningStatus getStatus() {
        return status;
    }

    public Integer getBrokerPort() {
        return brokerPort;
    }

    public Long getRqWaitMax() {
        return rqWaitMax;
    }

    public Long getRqWaitAvg() {
        return rqWaitAvg;
    }

    public Long getClientQueueDepthCur() {
        return clientQueueDepthCur;
    }

    public Long getClientQueueDepthMax() {
        return clientQueueDepthMax;
    }

    public Long getRqDurationMax() {
        return rqDurationMax;
    }

    public Long getRqDurationAvg() {
        return rqDurationAvg;
    }

    public Long getActiveServers() {
        return activeServers;
    }

    public Long getActiveClientsNow() {
        return activeClientsNow;
    }

    public Long getActiveClientsPeak() {
        return activeClientsPeak;
    }

    public Integer getBrokerPid() {
        return brokerPid;
    }

    public Long getBusyServers() {
        return busyServers;
    }

    public Long getAvailableServers() {
        return availableServers;
    }

    public Long getLockedServers() {
        return lockedServers;
    }

    public Long getTotalRequests() {
        return totalRequests;
    }

    public Integer getMaxAgents() {
        return maxAgents;
    }

    public Integer getMaxClients() {
        return maxClients;
    }

}
