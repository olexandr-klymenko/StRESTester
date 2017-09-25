import asyncio

from configure_logging import configure_logging
from config import StressTestConfig
from players.gamek_k02_player import StressTestGameK01Player

# TODO add argparser to be able to choose scenario
# TODO add README.md

if __name__ == '__main__':
    configure_logging()
    config = StressTestConfig()
    loop = asyncio.get_event_loop()
    player = StressTestGameK01Player(loop, config, 'scenarios/scenario.json')
    player.run_player()
    loop.close()
