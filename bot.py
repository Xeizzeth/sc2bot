from logging import getLogger

from sc2 import BotAI

import debug_server

logger = getLogger(__name__)


class Bot(BotAI):
    async def on_start(self):
        logger.info("The match has started")
        try:
            debug_server.start_server()
            logger.info("The debug server has launched")
        except:
            logger.error("The problem launching server", exc_info=True)

    async def on_step(self, iteration):
        if iteration == 0:
            for worker in self.workers:
                self.do(worker.attack(self.enemy_start_locations[0]))
        if not iteration % 100:
            iteration_message = f"The current iteration is {iteration}"
            logger.info(iteration_message)
            await debug_server.LogSocketHandler.post_message(iteration_message)

    async def on_end(self, game_result):
        logger.info(f"The game has ended with {game_result}")
