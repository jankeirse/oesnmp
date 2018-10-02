#!/usr/bin/python -u
import ConfigParser
import inspect
import logging
import os.path
import sys
import time

import requests
from requests.auth import HTTPBasicAuth

import snmp_passpersist as snmp


class PasoeServer:
    def __init__(self, oemanager_url, application, user, password):
        self.oemanager_url = oemanager_url
        self.application = application
        self.user = user
        self.password = password
        self._auth = HTTPBasicAuth(user, password)

    def get_agents(self):
        response = requests.get("{0}/applications/{1}/agents/".format(self.oemanager_url, self.application), auth=self._auth)
        return response.json()["result"]["agents"]

    def add_session_details_to_agents(self, agents):
        for agent in agents:
            try:
                response = requests.get("{0}/applications/{1}/agents/{2}/sessions".format(
                    self.oemanager_url, self.application, agent["agentId"]),
                    auth=self._auth)
                agent["sessions"] = response.json()["result"]["AgentSession"]
            except ValueError as e:
                logging.warn("Unexpected return value {0} when getting session details for {1}: Resulting error was {1}",
                             response.text, agent, e.message)

    def get_sessions(self):
        response = requests.get("{0}/applications/{1}/sessions/".format(self.oemanager_url, self.application),
                                auth=self._auth)
        return response.json()["result"]["OEABLSession"]

    def get_clients(self):
        response = requests.get("{0}/applications/{1}/clients/".format(self.oemanager_url, self.application),
                                auth=self._auth)
        return response.json()["result"]["ClientConnection"]

    def get_requests(self):
        response = requests.get("{0}/applications/{1}/requests/".format(self.oemanager_url, self.application),
                                auth=self._auth)
        return response.json()["result"]["Request"]


class NumericMetric:
    def __init__(self):
        self._min = sys.maxint
        self.max = 0
        self.average = 0
        self.total = 0
        self._count = 0

    def add_value(self, value):
        self._min = min(self._min, value)
        self.max = max(self.max, value)
        self._count = self._count + 1
        self.total = self.total + value
        self.average = self.total / self._count

    def get_min(self):
        if self._count == 0:
            return 0
        else:
            return self._min

    def set_min(self, value):
        self._min = value

    min = property(get_min, set_min)


class RequestInfo:
    def __init__(self):
        self.requests = 0
        self.states = {"INIT": 0, "READY": 0, "READING": 0, "RUNNING": 0, "WRITING": 0, "DISCONNECT": 0}
        self.elapsedTime = NumericMetric()


class SessionInfo:
    def __init__(self):
        self.sessionStates = {"IDLE": 0,
                              "ACTIVE": 0,
                              "TERMINATED": 0}
        self.sessionMemory = NumericMetric()
        self.numSessions = 0
        self.externalSessions = 0  # External sessions are executing dll/so code or doing something else outside of the


class AgentInfo:
    def __init__(self):
        self.agentStates = {"INIT": 0,
                            "STARTING": 0,
                            "AVAILABLE": 0,
                            "RESERVED": 0,
                            "ERROR": 0,
                            "STOPPING": 0,
                            "STOPPED": 0}
        self.numAgents = 0


class ServerState:
    def __init__(self):
        self.agent_info = AgentInfo()
        self.session_info = SessionInfo()
        self.request_info = RequestInfo()


class ServerStateManager:
    def __init__(self):
        self.state = ServerState()

    def add_agent_and_their_session_states(self, agents):
        for agent in agents:
            self.state.agent_info.numAgents = self.state.agent_info.numAgents + 1
            self.state.agent_info.agentStates[agent["state"]] = self.state.agent_info.agentStates[agent["state"]] + 1
            for agent_session in agent["sessions"]:
                self._count_agent_session(agent_session)

    def _count_agent_session(self, agent_session):
        self.state.session_info.numSessions = self.state.session_info.numSessions + 1
        try:
            self.state.session_info.sessionStates[agent_session["SessionState"]] = self.state.session_info.sessionStates[agent_session["SessionState"]] + 1
        except ValueError as e:
            logging.warn("Unknown Session State {0}, error message was {1}".format(agent_session["SessionState"],
                                                                                   e.message))
        self.state.session_info.sessionMemory.add_value(agent_session["SessionMemory"])
        if agent_session["SessionExternalState"] == 1:
            self.state.session_info.externalSessions = self.state.session_info.externalSessions + 1

    def add_request_info(self, active_requests):
        for request in active_requests:
            self.state.request_info.states[request["requestState"]] = self.state.request_info.states[request["requestState"]] + 1
            self.state.request_info.requests = self.state.request_info.requests + 1
            self.state.request_info.elapsedTime.add_value(request["requestElapsedTime"])


def iterate_over_servers():
    server_count = 0
    for section in config.sections():
        if section.startswith("server:"):
            server_count = server_count + 1
            server_name = get_server_name_from_section(section)
            expose_server_name_in_ordered_list(server_count, server_name)
            process_server(server_name)


def expose_server_name_in_ordered_list(location, server_name):
    pp.add_str("1.{0}".format(location), server_name)


def get_server_name_from_section(section):
    return section[section.rindex(":") + 1:]


def process_server(server):
    server_information = obtain_information_for_server(server)
    expose_server_metrics(server, server_information)


def expose_server_metrics(server_name, server_information):
    oid_server_name = snmp.PassPersist.encode(server_name)
    pp.add_int("2.1.{0}".format(oid_server_name), server_information.agent_info.numAgents)
    pp.add_int("2.2.{0}".format(oid_server_name),
               server_information.agent_info.agentStates["AVAILABLE"])
    pp.add_int("2.3.{0}".format(oid_server_name),
               server_information.agent_info.agentStates["ERROR"])
    pp.add_int("2.4.{0}".format(oid_server_name),
               server_information.agent_info.agentStates["INIT"])
    pp.add_int("2.5.{0}".format(oid_server_name),
               server_information.agent_info.agentStates["RESERVED"])
    pp.add_int("2.6.{0}".format(oid_server_name),
               server_information.agent_info.agentStates["STARTING"])
    pp.add_int("2.7.{0}".format(oid_server_name),
               server_information.agent_info.agentStates["STOPPED"])
    pp.add_int("2.8.{0}".format(oid_server_name),
               server_information.agent_info.agentStates["STOPPING"])
    pp.add_int("3.1.{0}".format(oid_server_name),
               server_information.request_info.requests)
    pp.add_int("3.2.{0}".format(oid_server_name),
               server_information.request_info.elapsedTime.min)
    pp.add_int("3.3.{0}".format(oid_server_name),
               server_information.request_info.elapsedTime.max)
    pp.add_int("3.4.{0}".format(oid_server_name),
               server_information.request_info.elapsedTime.average)
    pp.add_int("3.5.{0}".format(oid_server_name),
               server_information.request_info.elapsedTime.total)
    pp.add_int("4.1.{0}".format(oid_server_name),
               server_information.session_info.numSessions)
    pp.add_cnt_64bit("4.2.{0}".format(oid_server_name),
               server_information.session_info.sessionMemory.min)
    pp.add_cnt_64bit("4.3.{0}".format(oid_server_name),
               server_information.session_info.sessionMemory.max)
    pp.add_cnt_64bit("4.4.{0}".format(oid_server_name),
               server_information.session_info.sessionMemory.average)
    pp.add_cnt_64bit("4.5.{0}".format(oid_server_name),
               server_information.session_info.sessionMemory.total)
    pp.add_int("4.6.{0}".format(oid_server_name),
               server_information.session_info.externalSessions)
    pp.add_int("4.7.{0}".format(oid_server_name),
               server_information.session_info.sessionStates["ACTIVE"])
    pp.add_int("4.8.{0}".format(oid_server_name),
               server_information.session_info.sessionStates["IDLE"])
    pp.add_int("4.9.{0}".format(oid_server_name),
               server_information.session_info.sessionStates["TERMINATED"])


def obtain_information_for_server(server):
    state_manager = ServerStateManager()

    try:
        section_name = "server:{0}".format(server)
        pasoe_server = PasoeServer(config.get(section_name, "oemanager"),
                         config.get(section_name, "application"),
                         config.get(section_name, "user"),
                         config.get(section_name, "password"))
        agents = pasoe_server.get_agents()
        pasoe_server.add_session_details_to_agents(agents)
        state_manager.add_agent_and_their_session_states(agents)

        active_requests = pasoe_server.get_requests()
        state_manager.add_request_info(active_requests)

        # not exposed for now
        # clients = pasoe_server.get_clients()
        # sessions = pasoe_server.get_sessions()

    except ValueError as e:
        logging.warn("Couldn't handle server {0}, error was {1}".format(server, e.message))

    return state_manager.state


def update_snmp():
    pp.add_int("0", int(str(time.time()).split('.')[0]))
    iterate_over_servers()


if '__file__' not in locals():
    __file__ = inspect.getframeinfo(inspect.currentframe())[0]

myDir = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser.ConfigParser()
config.read("{0}/pasoe.cfg".format(myDir))
# set up logging
logging.basicConfig(filename=config.get("settings", "logfile"), level=logging.WARNING,
                    format='%(asctime)s:' + logging.BASIC_FORMAT)
base_node = config.get("settings", "basenode")

pp = snmp.PassPersist(base_node)
pp.start(update_snmp, 60)

