import logging
import multiprocessing as mp
import os
import sys

from invoke import task

from action_registry.registry import ActionsRegistry
from constants import *
from report import StressTestReport
from stress_test_config import StressTestConfig
from utils import get_parsed_scenario_root, progress_handler, StressTestProcess
from version import version
from worker import worker

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
    cfg = StressTestConfig(config)
    os.environ[ST_CONFIG_PATH] = config
    scenario_xml_root = get_parsed_scenario_root(scenario)

    total_actions = len(scenario_xml_root) * cfg[WORKERS_NUMBER] * cfg[USERS_NUMBER] * cfg[ITERATIONS_NUMBER]
    logger.info("Total actions: %s" % total_actions)
    progress_queue = mp.Queue()
    progress_process = mp.Process(target=progress_handler, args=(progress_queue, total_actions))
    progress_process.start()

    workers_info = {}
    report_metrics = []
    for index in range(1, cfg[WORKERS_NUMBER] + 1):
        parent_conn, child_conn = mp.Pipe()
        workers_info[index] = parent_conn, StressTestProcess(target=worker, args=(index,
                                                                                  scenario_xml_root,
                                                                                  child_conn,
                                                                                  progress_queue))

    for _, (parent_conn, process) in workers_info.items():
        process.start()

    for _, (parent_conn, process) in workers_info.items():
        report_metrics.append(parent_conn.recv())

    for _, (parent_conn, process) in workers_info.items():
        process.join()

    try:
        for _, (parent_conn, process) in workers_info.items():
            if process.exception:
                error, traceback = process.exception
                raise Exception(traceback)

    except Exception:
        progress_process.terminate()
        raise
    else:
        progress_process.join()
    finally:
        report = StressTestReport(report_metrics)
        report.process_metrics()


@task
def getactions(_, ):
    print(ActionsRegistry.get_actions())
