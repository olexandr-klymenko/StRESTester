import asyncio

from config import StressTestConfig
from players.gamek_k02_player import StressTestGameK01Player

if __name__ == '__main__':
    config = StressTestConfig()
    loop = asyncio.get_event_loop()
    player = StressTestGameK01Player(loop, config, 'scenarios/scenario.json')
    player.run_player()
    loop.close()
