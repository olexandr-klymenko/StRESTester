import multiprocessing as mp
import os

from invoke import task

from action_registry.registry import *
from configure_logging import configure_logging
from constants import *
from report import StressTestReport
from stress_test_config import StressTestConfig
from version import version
from worker import worker

# TODO add doc strings


@task
def run(_, scenario, config):
    logger = configure_logging()
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    _config = StressTestConfig(config)
    os.environ[ST_SCENARIO_PATH] = scenario
    os.environ[ST_CONFIG_PATH] = config

    mp.set_start_method('spawn')
    workers_info = {}
    report_metrics = []
    for index in range(1, _config[WORKERS_NUMBER] + 1):
        parent_conn, child_conn = mp.Pipe()
        workers_info[index] = parent_conn, mp.Process(target=worker, args=(index, child_conn))

    for _, (parent_conn, process) in workers_info.items():
        process.start()

    for _, (parent_conn, process) in workers_info.items():
        report_metrics.append(parent_conn.recv())

    for _, (parent_conn, process) in workers_info.items():
        process.join()

    report = StressTestReport(report_metrics)
    report.process_metrics()


@task
def getactions(_, ):
    print(ActionsRegistry.get_actions())
