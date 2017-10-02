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

# TODO add doc strings
# TODO implement web ui

logger = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
logger.addHandler(out_hdlr)
logger.setLevel(logging.INFO)


@task
def run(_, scenario, config):
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    scenario_xml_root = Scenario(scenario)

    cfg = StressTestConfig(config)
    os.environ[ST_CONFIG_PATH] = config

    total_actions = len(scenario_xml_root) * cfg[WORKERS_NUMBER] * cfg[USERS_NUMBER] * cfg[ITERATIONS_NUMBER]
    logger.info("Total actions: %s" % total_actions)

    workers_manager = WorkerManager(scenario_xml_root, cfg[WORKERS_NUMBER], total_actions)
    workers_manager.manage_workers()


@task
def getactions(_, ):
    print(ActionsRegistry.get_actions())
