from importlib import reload
from time import sleep

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer

import bot


def main():
    player_config = [
        Bot(Race.Random, bot.Bot()),
        Computer(Race.Random, Difficulty.VeryHard)
    ]

    gen = sc2.main._host_game_iter(
        sc2.maps.get("CatalystLE"),
        player_config,
        realtime=False
    )

    while True:
        next(gen)

        if input('Press enter to reload or type "q" to exit: ') == 'q':
            exit()

        reload(bot)
        player_config[0].ai = bot.Bot()
        gen.send(player_config)


if __name__ == "__main__":
    main()
