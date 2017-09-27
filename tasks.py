from invoke import task
import asyncio

from config import StressTestConfig
from configure_logging import configure_logging
from constants import PROJECT
from counter import StatsCounter
from player import StressTestPlayer
from codes_description import HTTPCodesDescription
from actions_registry import ActionsRegistry
from version import version
import actions

# TODO implement jinja2 instead of DIY template
# TODO implement multiprocessing flow
# TODO add doc strings


@task
def run(_, scenario, config, swagger=False):
    logger = configure_logging()
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    _config = StressTestConfig(config)
    loop = asyncio.get_event_loop()
    HTTPCodesDescription.init(loop, config, swagger)
    player = StressTestPlayer(loop=loop, config=_config, scenario=scenario)
    try:
        player.run_player()
        loop.close()
    finally:
        logger.info("Time metrics: %s" % StatsCounter.get_averages())
        logger.info("Errors metrics: %s" % dict(StatsCounter.get_errors()))
        logger.info("Total time: %s" % StatsCounter.get_total_time())


@task
def actions(_, ):
    print(ActionsRegistry.get_actions())
