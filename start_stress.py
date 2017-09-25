import asyncio
from argparse import ArgumentParser

from version import version
from constants import PROJECT, CONFIG
from configure_logging import configure_logging
from config import StressTestConfig
from players.gamek_k02_player import StressTestGameK01Player

# TODO add README.md


def get_cmd_args():
    parser = ArgumentParser()
    parser.add_argument('-s', '--scenario', required=True,
                        help="Path to JSON file with stress test scenario, i.e.: 'scenarios/profile_service.json'")
    parser.add_argument('-c', '--config', default=CONFIG, help="JSON file containing settings")
    return parser.parse_args()

if __name__ == '__main__':
    logger = configure_logging()
    logger.info("Starting '%s' version %s ..." % (PROJECT, version))
    cmd_args = get_cmd_args()
    config = StressTestConfig(cmd_args.config)
    loop = asyncio.get_event_loop()
    player = StressTestGameK01Player(loop, config, cmd_args.scenario)
    player.run_player()
    loop.close()
