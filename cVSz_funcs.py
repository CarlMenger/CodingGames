import copy
import math
import random

from functools import wraps
import time
from cVSz_classes import *

path = 'D:/__CodingGames/coding_games/codeVsZombies/simulation/input.txt'


def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kw):
        tstart = time.time()
        output = my_func(*args, **kw)
        tend = time.time()
        print('"{}" took {:.3f} ms to execute\n'.format(my_func.__name__, (tend - tstart) * 1000))
        return output

    return timed


def load_init_data_online() -> GameState:
    """ keep 2 lists of objects, keep player as last id/position human"""
    humans = []
    zombies = []
    player_x, player_y = [int(i) for i in input().split()]
    human_count = int(input())
    player = Player(0, (player_x, player_y), (0, 0))
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        humans.append(Character(human_id, (human_x, human_y), (0, 0)))
    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = [int(j) for j in input().split()]
        zombies.append(Zombie(zombie_id, (zombie_x, zombie_y), (zombie_x_next, zombie_y_next)))
    return GameState(0, player, humans, zombies, 0)


@timeit
def load_init_data_offline() -> GameState:
    humans = []
    zombies = []
    with open(path, 'r+') as data:
        x, y = map(int, data.readline().split())
        player = Player(0, (x, y), (x, y))
        human_count = int(data.readline())
        for i in range(human_count):
            human_id, human_x, human_y = map(int, data.readline().split())
            humans.append(Character(human_id, (human_x, human_y), (human_x, human_y)))
        zombie_count = int(data.readline())
        for i in range(zombie_count):
            zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = map(int, data.readline().split())
            zombies.append(Zombie(zombie_id, (zombie_x, zombie_y), (zombie_x_next, zombie_y_next)))
    return GameState(0, player, humans, zombies, 0)


@timeit
def base_population_generation(player, humans, zombies) -> List[GameState]:
    population = []
    for i in range(1000):
        population.append(GameState(i, player, humans, zombies, 0))
    for gs in population:
        move = (random.randint(0, 16000), random.randint(0, 9000))
        gs.player.set_next_move(move)
    return population


@timeit
def simulate_turn(population: List[GameState]) -> List[GameState]:
    for game_state in population:
        game_state.update_game_state()
    return population
