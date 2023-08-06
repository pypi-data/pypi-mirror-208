from urllib.parse import quote as quote

from python_agent import __package_name__ as PACKAGE_NAME


class SLRoutes(object):
    RECOMMENDED = "recommended"
    BUILD_SESSION = "buildsession"
    RECOMMENDATIONS = "test-recommendations"
    EXCLUSIONS = "test-exclusions"
    LAB_IDS = "lab-ids"

    @staticmethod
    def build_session_v2(build_session_id=""):
        return "/v2/agents/%s/%s" % SLRoutes.quote_value_or_empty([SLRoutes.BUILD_SESSION, build_session_id])

    @staticmethod
    def build_mapping_v3():
        return "/v3/agents/buildmapping"

    @staticmethod
    def build_mapping_v2():
        return "/v2/agents/buildmapping"

    @staticmethod
    def footprints_v2():
        return "/v2/testfootprints"

    @staticmethod
    def footprints_v5():
        return "/v5/agents/footprints"

    @staticmethod
    def events_v1():
        return "/v1/testevents"

    @staticmethod
    def events_v2():
        return "/v2/agents/events"

    @staticmethod
    def test_execution_v3():
        return "/v3/testExecution"

    @staticmethod
    def external_data_v3():
        return "/v3/externaldata"

    @staticmethod
    def logsubmission_v2():
        return "/v2/logsubmission"

    @staticmethod
    def recommended_v2():
        return "/v2/agents/%s/%s" % (PACKAGE_NAME, SLRoutes.RECOMMENDED)

    @staticmethod
    def test_exclusions_v3(build_session_id, test_stage):
        return "/v3/%s/%s/%s" % SLRoutes.quote_value_or_null([SLRoutes.EXCLUSIONS, build_session_id, test_stage])

    def test_exclusions_v4(build_session_id, test_stage, testGroupId):
        return "/v4/%s/%s/%s" % SLRoutes.quote_value_or_null(
            [SLRoutes.EXCLUSIONS, build_session_id, test_stage, testGroupId])

    @staticmethod
    def configuration_v2(customer_id, app_name, branch_name, test_stage, agent_name, agent_version):
        return "/v2/config/%s/%s/%s/%s/%s/%s" % SLRoutes.quote_value_or_null(
            [customer_id, app_name, branch_name, test_stage, agent_name, agent_version])

    @staticmethod
    def lab_ids_active_build_session_v1(labid):
        return "/v1/%s/%s/build-sessions/active" % SLRoutes.quote_value_or_null([SLRoutes.LAB_IDS, labid])

    @staticmethod
    def get_value_or_null(value):
        return quote(value or "null", safe="")

    @staticmethod
    def get_value_or_empty(value):
        return quote(value or "", safe="")

    @staticmethod
    def quote_value_or_null(params):
        return tuple(map(lambda p: SLRoutes.get_value_or_null(p), params))

    @staticmethod
    def quote_value_or_empty(params):
        return tuple(map(lambda p: SLRoutes.get_value_or_empty(p), params))

    @staticmethod
    def agent_events_v3():
        return "/v3/agents/agent-events"
