from python_agent.test_listener.executors.anonymous_execution import AnonymousExecution
from python_agent.utils import disableable


class EndAnonymousExecution(AnonymousExecution):

    def __init__(self, config_data, labid):
        super(EndAnonymousExecution, self).__init__(config_data, labid)

    @disableable()
    def execute(self):
        self.backend_proxy.end_execution(self.labid)
