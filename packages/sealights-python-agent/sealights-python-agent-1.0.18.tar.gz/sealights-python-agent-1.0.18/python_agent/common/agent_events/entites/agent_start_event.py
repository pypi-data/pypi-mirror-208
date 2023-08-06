import socket
import platform
import datetime
import sys

from python_agent.common.agent_events.utils import get_utc_time_in_ms
from python_agent import __version__ as VERSION
from python_agent.common.constants import AGENT_EVENT_START
from python_agent.common.agent_events.env_vars import get_ci_env_vars


class AgentStartEvent(object):
    def __init__(self, config_data, agent_id, lab_id, agent_type, test_stage):
        self.agentId = agent_id
        self.buildSessionId = config_data.buildSessionId
        self.appName = config_data.appName
        self.events = [{
            "type": AGENT_EVENT_START,
            "utcTimestamp_ms": get_utc_time_in_ms(),
            "data": {
                "agentInfo": {
                    "technology": "python",
                    "agentVersion": VERSION,
                    "agentType": agent_type,
                    "testStage": test_stage,
                    "labId": lab_id,
                    "sendsPing": True,
                    "argv": sys.argv[1:],
                    "envVars": get_ci_env_vars(),
                    "tags": [],
                    "agentConfig": {},
                },
                "machineInfo": {
                    "machineName": socket.gethostname(),
                    "arch": platform.machine(),
                    "os": platform.system(),
                    "localDateTime": datetime.datetime.now().isoformat(),
                    "localDateTimeUnix_s": int(datetime.datetime.now().timestamp()),
                    "ipAddress": [socket.gethostbyname(socket.gethostname())]
                },
            }
        }]
