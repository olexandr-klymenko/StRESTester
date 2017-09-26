import asyncio
from argparse import ArgumentParser

from version import version
from constants import PROJECT, CONFIG
from configure_logging import configure_logging
from config import StressTestConfig
from players.gamek_k02_player import StressTestGameK01Player
from counter import StatsCounter

# TODO add README.md


def get_cmd_args():
    parser = ArgumentParser()
    parser.add_argument('-s', '--scenario', required=True,
                        help="Path to XML file with stress test scenario, i.e.: 'scenarios/test.xml'")
    parser.add_argument('-c', '--config', default=CONFIG, help="JSON file containing settings")
    return parser.parse_args()


if __name__ == '__main__':
    logger = configure_logging()
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    cmd_args = get_cmd_args()
    config = StressTestConfig(cmd_args.config)
    loop = asyncio.get_event_loop()
    player = StressTestGameK01Player(loop=loop, config=config, scenario=cmd_args.scenario)
    try:
        player.run_player()
        loop.close()
    finally:
        logger.info("Time metrics: %s" % StatsCounter.get_averages())
        logger.info("Errors metrics: %s" % dict(StatsCounter.get_errors()))
        logger.info("Total time: %s" % StatsCounter.get_total_time())
