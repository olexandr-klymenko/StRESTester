import asyncio
from argparse import ArgumentParser

from config import StressTestConfig
from configure_logging import configure_logging
from constants import PROJECT
from counter import StatsCounter
from player import StressTestPlayer
from swagger_info import Swagger
from version import version


# TODO implement swaggerless flow
# TODO implement multiprocessing flow

def get_cmd_args():
    parser = ArgumentParser()
    parser.add_argument('-s', '--scenario', required=True,
                        help="Path to XML file with stress test scenario, i.e.: 'scenarios/test.xml'")
    parser.add_argument('-c', '--config', required=True, help="JSON file containing settings")
    return parser.parse_args()


if __name__ == '__main__':
    logger = configure_logging()
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    cmd_args = get_cmd_args()
    config = StressTestConfig(cmd_args.config)
    loop = asyncio.get_event_loop()
    Swagger.parse(loop, config)
    player = StressTestPlayer(loop=loop, config=config, scenario=cmd_args.scenario)
    try:
        player.run_player()
        loop.close()
    finally:
        logger.info("Time metrics: %s" % StatsCounter.get_averages())
        logger.info("Errors metrics: %s" % dict(StatsCounter.get_errors()))
        logger.info("Total time: %s" % StatsCounter.get_total_time())
