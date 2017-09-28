from invoke import task

from config import StressTestConfig
from configure_logging import configure_logging
from constants import PROJECT, TEST_USER_NAME, USERS_NUMBER, USER_NUMBER_MULTIPLIER
from counter import StatsCounter
from player import StressTestPlayer
from codes_description import HTTPCodesDescription
from actions_registry import ActionsRegistry
from version import version
from utils import get_users
import actions # don't remove

# TODO implement multiprocessing flow
# TODO add doc strings


@task
def run(_, scenario, config, multiplier=USER_NUMBER_MULTIPLIER, swagger=False):
    logger = configure_logging()
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    _config = StressTestConfig(config)
    HTTPCodesDescription.init(config, swagger)
    test_users = get_users(TEST_USER_NAME, _config[USERS_NUMBER], multiplier)
    player = StressTestPlayer(config=_config, scenario_path=scenario, test_users=test_users)
    try:
        player.run_player()
    finally:
        logger.info("Time metrics: %s" % StatsCounter.get_averages())
        logger.info("Errors metrics: %s" % dict(StatsCounter.get_errors()))
        logger.info("Total time: %s" % StatsCounter.get_total_time())


@task
def actions(_, ):
    print(ActionsRegistry.get_actions())
