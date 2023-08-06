import logging
import sys
from distutils.util import strtobool

from coverage.cmdline import Opts, unshell_list

from python_agent.build_scanner.executors.build import Build
from python_agent.build_scanner.executors.config import Config
from python_agent.common import constants
from python_agent.common.constants import TOKEN_FILE, BUILD_SESSION_ID_FILE, TEST_RECOMMENDATION, DEFAULT_BRANCH_NAME
from python_agent.common.config_data import ScmConfigArgs
from python_agent.common.configuration_manager import ConfigurationManager
from python_agent.common.constants import DEFAULT_WORKSPACEPATH
from python_agent.packages import click
from python_agent.test_listener.executors.end_execution import EndAnonymousExecution
from python_agent.test_listener.executors.run import Run
from python_agent.test_listener.executors.send_footprints import SendFootprintsAnonymousExecution
from python_agent.test_listener.executors.start_execution import StartAnonymousExecution
from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution
from python_agent.test_listener.executors.test_frameworks.nose_execution import NoseAgentExecution
from python_agent.test_listener.executors.test_frameworks.pytest_execution import PytestAgentExecution
from python_agent.test_listener.executors.test_frameworks.unittest_execution import UnittestAgentExecution
from python_agent.test_listener.executors.upload_reports import UploadReports
from python_agent.utils import CommandType, generate_random_build_name

log = logging.getLogger(__name__)

CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower(), ignore_unknown_options=True, allow_extra_args=True)

_common_options = [
    click.option("--token", help="Token (mandatory. Can also be provided by 'tokenfile' argument). Case-sensitive."),
    click.option("--tokenfile", default=TOKEN_FILE, help="A path to a file where the program can find the token. Case-sensitive."),
    click.option("--proxy", help="Proxy. Must be of the form: http[s]://<server>")
]

_build_session_options = [
    click.option("--buildsessionid", help="Provide build session id manually, case-sensitive."),
    click.option("--buildsessionidfile", default=BUILD_SESSION_ID_FILE,
                 help="Path to a file to save the build session id in (default: <user.dir>/buildSessionId.txt)."),
]

_scm_options_defs = [
    ("--scmprovider",
     "The provider name of your Source Control Management (SCM) tool. "
     "Supported values are 'Github', 'Bitbucket' and 'Gitlab'. "
     "If not used, 'Github' is assumed."),
    ("--scmversion",
     "The version of your Source Control Management (SCM) tool. "
     "If left blank, cloud version is assumed. "
     "Otherwise, specify the version of your on-premise server."),
    ("--scmbaseurl",
     "The URL to the repository which contains the code. "
     "If left blank, the url of the remote GIT origin is being used."),
    ("--scm",
     "The name of your Source Control Management (SCM) tool. "
     "Supported values are 'git' and 'none'. If not used, 'git' is assumed."),
]


def common_options(f):
    options = _common_options if f.__name__ == "config" else _common_options + _build_session_options
    for option in options:
        f = option(f)
    return f


def get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, labid, scm_args=None):
    configuration_manager = ConfigurationManager()
    command_type = getattr(ctx, "command_type", CommandType.OTHER)
    config_data = configuration_manager.init_configuration(command_type, token, buildsessionid, labid, tokenfile, buildsessionidfile, proxy, scm_args)
    return config_data


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    # entry point for the CLI. Reference from below and from setup.py -> console_scripts
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--appname", required=True, help="Application name, case-sensitive.")
@click.option("--branchname", help="Branch name, case-sensitive.", default=DEFAULT_BRANCH_NAME)
@click.option("--buildname", help="Build id, case-sensitive. Should be unique between builds.", default=generate_random_build_name())
@click.option("--buildsessionid", required=False, help="Provide build session id manually, case-sensitive.")
@click.option("--workspacepath", help="Path to the workspace where the source code exists", default=DEFAULT_WORKSPACEPATH)
@click.option("--include", help=Opts.include.help, default=None, type=unshell_list)
@click.option("--exclude", help=Opts.omit.help, default='*venv*', type=unshell_list)
@click.pass_context
def config(ctx, token, tokenfile, proxy, appname, branchname, buildname, buildsessionid, workspacepath, include, exclude):
    ctx.command_type = CommandType.CONFIG
    config_data = get_config_data(ctx, token, tokenfile, None, None, proxy, None)
    Config(config_data, appname, branchname, buildname, buildsessionid, workspacepath, include, exclude).execute()
    log.info("Configuration completed successfully")


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option(_scm_options_defs[0][0], required=False, help=_scm_options_defs[0][1])
@click.option(_scm_options_defs[1][0], required=False, help=_scm_options_defs[1][1])
@click.option(_scm_options_defs[2][0], required=False, help=_scm_options_defs[2][1])
@click.option(_scm_options_defs[3][0], required=False, help=_scm_options_defs[3][1])
@click.pass_context
def build(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, scmprovider, scmversion, scmbaseurl, scm):
    scm_args = ScmConfigArgs(scmprovider, scmversion, scmbaseurl, scm)
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, None, scm_args=scm_args)
    Build(config_data).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV, help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.option("--cov-report", type=click.Path(writable=True), help="generate xml coverage report")
@click.option("--per-test", default="true", type=strtobool, help="collect coverage per test")
@click.option("--interval", default=constants.INTERVAL_IN_MILLISECONDS, type=int, help="interval in milliseconds to send data")
@click.option("-tsd", "--test-selection-disable", is_flag=True, help='A flag to disable the test selection otherwise enable')
@click.option("-tsri", "--test-selection-retry-interval", default=TEST_RECOMMENDATION.interval_sec, help='Test recommendation retry interval in sec')
@click.option("-tsrt", "--test-selection-retry-timeout", default=TEST_RECOMMENDATION.timeout_sec, help='Test recommendation retry timeout in sec')
@click.option("--testgroupid", required=False, default="", help="The Test Group Id")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def pytest(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, labid, teststage, cov_report, per_test, interval,
           test_selection_disable, test_selection_retry_interval, test_selection_retry_timeout, testgroupid, args):
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, labid)
    config_data.testSelection.update({"enable": not test_selection_disable, "interval": test_selection_retry_interval,
                                     "timeout": test_selection_retry_timeout})
    PytestAgentExecution(config_data, labid, teststage, cov_report, per_test, interval, testgroupid, args).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV, help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.option("--cov-report", type=click.Path(writable=True), help="generate xml coverage report")
@click.option("--per-test", default="true", type=strtobool, help="collect coverage per test")
@click.option("--interval", default=constants.INTERVAL_IN_MILLISECONDS, type=int, help="interval in milliseconds to send data")
@click.option("--testgroupid", required=False, default="", help="The Test Group Id")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def nose(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, labid, teststage, cov_report, per_test, interval, testgroupid, args):
    # click framework make the args a tuple
    # This creates an error in the parser since it expects a list.
    args = list(args)
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, labid)
    NoseAgentExecution(config_data, labid, teststage, cov_report, per_test, interval, testgroupid, args).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV, help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.option("--cov-report", type=click.Path(writable=True), help="generate xml coverage report")
@click.option("--per-test", default="true", type=strtobool, help="collect coverage per test")
@click.option("--interval", default=constants.INTERVAL_IN_MILLISECONDS, type=int, help="interval in milliseconds to send data")
@click.option("--testgroupid", required=False, default="", help="The Test Group Id")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def unittest(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, labid, teststage, cov_report, per_test, interval, testgroupid, args):
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, labid)
    UnittestAgentExecution(config_data, labid, teststage, cov_report, per_test, interval, testgroupid, args).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--teststage", required=True, default=constants.DEFAULT_ENV,
              help="The tests stage (e.g 'integration tests', 'regression'). The default will be 'Unit Tests'")
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--testgroupid", required=False, default="", help="The Test Group Id")
@click.pass_context
def start(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, teststage, labid, testgroupid):
    ctx.command_type = CommandType.START
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, labid)
    StartAnonymousExecution(config_data, teststage, labid, testgroupid).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--testgroupid", required=False, default="", help="The Test Group Id")
@click.pass_context
def end(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, labid, testgroupid):
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, labid)
    EndAnonymousExecution(config_data, labid, testgroupid).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--reportfile", type=unshell_list,
              help="Report files. This argument can be declared multiple times in order to upload multiple files.")
@click.option("--reportfilesfolder", type=unshell_list,
              help="Folders that contains nothing but report files. All files in folder will be uploaded. This argument can be declared multiple times in order to upload multiple files from multiple folders.")
@click.option("--source", default="Junit xml report",
              help="The reports provider. If not set, the default will be 'Junit xml report'")
@click.option("--type", default="JunitReport", help="The report type. If not set, the default will be 'JunitReport'")
@click.option("--hasmorerequests", default="true", type=strtobool,
              help="flag indicating if test results contains multiple reports. True for multiple reports. False otherwise")
@click.pass_context
def uploadreports(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, labid, reportfile,
                  reportfilesfolder, source, type, hasmorerequests):
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, labid)
    UploadReports(config_data, labid, reportfile, reportfilesfolder, source, type, hasmorerequests).execute()


@cli.command(context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.option("--cov-report", type=click.Path(writable=True), help="generate xml coverage report")
@click.option("--per-test", default="true", type=strtobool, help="collect coverage per test")
@click.option("--interval", default=constants.INTERVAL_IN_MILLISECONDS, type=int, help="interval in milliseconds to send data")
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, labid, cov_report, per_test, interval, args):
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, None)
    config_data.args = sys.argv
    Run(config_data, labid, cov_report, per_test, interval).execute(args)


@cli.command(hidden=True, context_settings=CONTEXT_SETTINGS)
@common_options
@click.option("--labid", help="Lab Id, case-sensitive.")
@click.pass_context
def sendfootprints(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile, labid):
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, None)
    config_data.isOfflineMode = True
    SendFootprintsAnonymousExecution(config_data, labid).execute()


@cli.command(hidden=True, context_settings=CONTEXT_SETTINGS)
@common_options
@click.pass_context
def init(ctx, token, tokenfile, proxy, buildsessionid, buildsessionidfile):
    config_data = get_config_data(ctx, token, tokenfile, buildsessionid, buildsessionidfile, proxy, None)
    AgentExecution(config_data, None)


if __name__ == '__main__':
    cli()
