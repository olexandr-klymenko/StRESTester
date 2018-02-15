from multiprocessing import connection, Queue
from typing import Iterable
from xml.etree import ElementTree as ET

from configure_logging import configure_logging
from constants import TEST_USER_NAME
from counter import StatsCounter
from interfaces import BaseStressTestConfig
from player import StressTestPlayer

configure_logging()


def process_worker(worker_index: int,
                   cfg: BaseStressTestConfig,
                   scenario: Iterable[ET.Element],
                   conn: connection,
                   progress_queue: Queue):
    """
    The function which is intended to run in separate process
     as a target within multiprocessing.Process

    :param worker_index:
    :param cfg:
    :param scenario:
    :param conn:
    :param progress_queue:
    :return:
    """

    player = StressTestPlayer(config=cfg,
                              scenario=scenario,
                              test_user=f"{TEST_USER_NAME}_{worker_index}",
                              progress_queue=progress_queue)
    try:
        player.run_player()

    finally:
        conn.send((StatsCounter.get_averages(),
                   dict(StatsCounter.get_errors())))
