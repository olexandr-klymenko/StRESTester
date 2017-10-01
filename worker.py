import os
from multiprocessing import connection, Queue
from typing import List
from xml.etree import ElementTree as ET

from codes_description import HTTPCodesDescription
from configure_logging import configure_logging
from constants import ST_CONFIG_PATH, TEST_USER_NAME, USERS_NUMBER
from counter import StatsCounter
from player import StressTestPlayer
from stress_test_config import StressTestConfig

configure_logging()


def worker(worker_index: int, scenario_xml_root: ET.Element, conn: connection, progress_queue: Queue):
    """
    The function which is intended to run in separate process
     as a target within multiprocessing.Process
    :param worker_index:
    :param scenario_xml_root:
    :param conn:
    :param progress_queue:
    :return:
    """
    config_path = os.environ[ST_CONFIG_PATH]
    _config = StressTestConfig(config_path)
    HTTPCodesDescription.init(_config, False)

    test_users = _get_users(_config[USERS_NUMBER], worker_index)

    player = StressTestPlayer(config=_config,
                              scenario_xml_root=scenario_xml_root,
                              test_users=test_users,
                              progress_queue=progress_queue)
    try:
        player.run_player()

    finally:
        conn.send((StatsCounter.get_averages(), dict(StatsCounter.get_errors())))


def _get_users(users_number, worker_index) -> List:
    """
    It figures out the list of users for given worker
    :param users_number:
    :param worker_index:
    :return: list of user names
    """
    return ["%s_%s" % (TEST_USER_NAME, idx)
            for idx in range((worker_index - 1) * users_number, users_number * worker_index)]
