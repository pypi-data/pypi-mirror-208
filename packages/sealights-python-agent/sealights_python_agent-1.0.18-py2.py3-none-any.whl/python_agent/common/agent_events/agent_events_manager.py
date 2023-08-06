import logging
import uuid

from apscheduler.schedulers.background import BackgroundScheduler

from python_agent.common.agent_events.entites.agent_build_scan_error_event import AgentBuildScanErrorEvent
from python_agent.common.agent_events.entites.agent_footprints_submission_error_event import \
    AgentFootprintsSubmissionErrorEvent
from python_agent.common.agent_events.entites.agent_heartbeat_event import AgentHeartbeatEvent
from python_agent.common.agent_events.entites.agent_tests_submission_error_event import AgentTestsSubmissionErrorEvent
from python_agent.common.http.backend_proxy import BackendProxy
from python_agent.common.config_data import ConfigData
from python_agent.common.agent_events.entites.agent_start_event import AgentStartEvent
from python_agent.common.agent_events.entites.agent_stop_event import AgentStopEvent
from python_agent.utils import retries
from python_agent.common.constants import AGENT_TYPE_BUILD_SCANNER, AGENT_TYPE_TEST_LISTENER, \
    AGENT_EVENT_HEARTBEAT_INTERVAL
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.triggers import interval

log = logging.getLogger(__name__)
kwargs = {
    "executors": {'processpool': ProcessPoolExecutor(1)}
}


class AgentEventsManager(object):
    def __init__(self, config_data: ConfigData, agent_type: str, agent_id: str):
        if not config_data:
            raise Exception("'config_data' must be provided")
        self.config_data = config_data

        if not agent_id:
            agent_id = f'{uuid.uuid4()}'
        self.agent_id = agent_id

        if (agent_type != AGENT_TYPE_BUILD_SCANNER) and (agent_type != AGENT_TYPE_TEST_LISTENER):
            raise Exception("'agent_type' must be AGENT_TYPE_BUILD_SCANNER or AGENT_TYPE_TEST_LISTENER")
        self.agent_type = agent_type
        self.backend_proxy = BackendProxy(config_data)
        self.watchdog = BackgroundScheduler(**kwargs)
        self.watchdog.add_job(self.send_agent_heartbeat, interval.IntervalTrigger(seconds=AGENT_EVENT_HEARTBEAT_INTERVAL))
        self.started_lab_id = ""

    def send_agent_start(self, lab_id: str, test_stage: str):
        try:
            agent_start_event = AgentStartEvent(config_data=self.config_data, agent_id=self.agent_id, lab_id=lab_id,
                                                agent_type=self.agent_type, test_stage=test_stage)
            self._send_event(agent_start_event)
            self.started_lab_id = lab_id
            self.watchdog.start()
        except Exception as e:
            log.exception("Failed Sending Start Event. Error: %s" % str(e))

    def send_agent_stop(self):
        try:
            agent_stop_event = AgentStopEvent(config_data=self.config_data, agent_id=self.agent_id)
            self._send_event(agent_stop_event)
            self.watchdog.shutdown()
        except Exception as e:
            log.exception("Failed Sending Stop Event. Error: %s" % str(e))

    def send_agent_heartbeat(self):
        try:
            agent_heartbeat_event = AgentHeartbeatEvent(config_data=self.config_data, agent_id=self.agent_id,
                                                        lab_id=self.started_lab_id)
            self._send_event(agent_heartbeat_event)
        except Exception as e:
            log.exception("Failed Sending Heartbeat Event. Error: %s" % str(e))

    def send_agent_footprint_error(self, err: Exception):
        try:
            agent_footprints_submission_error_event = AgentFootprintsSubmissionErrorEvent(config_data=self.config_data,
                                                                                          agent_id=self.agent_id,
                                                                                          err=err)
            self._send_event(agent_footprints_submission_error_event)

        except Exception as e:
            log.exception("Failed Sending Footprint Error Event. Error: %s" % str(e))

    def send_agent_test_event_error(self, err: Exception):
        try:
            agent_test_event_error_event = AgentTestsSubmissionErrorEvent(config_data=self.config_data,
                                                                          agent_id=self.agent_id, err=err)
            self._send_event(agent_test_event_error_event)
        except Exception as e:
            log.exception("Failed Sending Test Event Error. Error: %s" % str(e))

    #
    def send_agent_build_scan_error(self, err: Exception):
        try:
            agent_build_scan_error_event = AgentBuildScanErrorEvent(config_data=self.config_data,
                                                                    agent_id=self.agent_id, err=err)
            self._send_event(agent_build_scan_error_event)
        except Exception as e:
            log.exception("Failed Sending Build Scan Error. Error: %s" % str(e))

    @retries(log)
    def _send_event(self, event):
        self.backend_proxy.send_agent_event(event)
