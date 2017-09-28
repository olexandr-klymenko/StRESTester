import os
from logging import getLogger
from typing import Tuple, List
from multiprocessing import connection

from counter import StatsCounter
from stress_test_config import StressTestConfig
from codes_description import HTTPCodesDescription
from player import StressTestPlayer
from configure_logging import configure_logging
from constants import ST_CONFIG_PATH, ST_SCENARIO_PATH, TEST_USER_NAME, USERS_NUMBER
import actions # don't remove: registering actions

configure_logging()

logger = getLogger(__name__)


def main(worker_index, conn: connection) -> Tuple:
    scenario_path = os.environ[ST_SCENARIO_PATH]
    config_path = os.environ[ST_CONFIG_PATH]
    _config = StressTestConfig(config_path)
    HTTPCodesDescription.init(_config, False)

    test_users = _get_users(_config[USERS_NUMBER], worker_index)

    player = StressTestPlayer(config=_config, scenario_path=scenario_path, test_users=test_users)
    try:
        player.run_player()
    finally:
        logger.info("Time metrics: %s" % StatsCounter.get_averages())
        logger.info("Errors metrics: %s" % dict(StatsCounter.get_errors()))

    conn.send((StatsCounter.get_averages(), dict(StatsCounter.get_errors())))
    conn.close()


def _get_users(users_number, worker_index) -> List:
    return ["%s_%s" % (TEST_USER_NAME, idx)
            for idx in range((worker_index - 1) * users_number, users_number * worker_index)]