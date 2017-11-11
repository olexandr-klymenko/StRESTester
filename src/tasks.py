import logging
import os
import sys

from invoke import task

from action_registry.registry import ActionsRegistry
from constants import *
from scenario import Scenario
from stress_test_config import StressTestConfig
from version import version
from workers_manager import WorkerManager

# TODO implement unit testing
# TODO implement web ui

logger = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(os.environ.get('LOG_LEVEL') or logging.INFO)
logger.addHandler(out_hdlr)
logger.setLevel(os.environ.get('LOG_LEVEL') or logging.INFO)


@task
def run(_, scenario, config):
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    scenario_obj = Scenario(path=scenario)

    cfg = StressTestConfig(config)
    os.environ[ST_CONFIG_PATH] = config

    scenario_iterations = \
        cfg[WORKERS_NUMBER] *\
        cfg[USERS_NUMBER] *\
        cfg[ITERATIONS_NUMBER]

    rest_actions =\
        sum(scenario_obj.rest_actions_info.values()) * scenario_iterations

    total_actions = len(scenario_obj) * scenario_iterations

    workers_manager = WorkerManager(scenario_obj,
                                    cfg[WORKERS_NUMBER],
                                    total_actions)
    workers_manager.run_stress_test(rest_actions=rest_actions)


@task
def get_actions(_, ):
    print(ActionsRegistry.get_actions())


# TODO implement test resp api
