import math

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


def init_round_inputs_offline():
    """ keep 2 lists of objects, keep player as last id/position human"""
    humans = []
    zombies = []
    x, y = [int(i) for i in input().split()]
    human_count = int(input())
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        humans.append(Character(human_id, (human_x, human_y), (0, 0)))
    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = [int(j) for j in input().split()]
        zombies.append(Zombie(zombie_id, (zombie_x, zombie_y), (zombie_x_next, zombie_y_next)))
    humans.append(Character(human_count, x, y))  # add player at the end
    return humans, zombies


@timeit
def load_offline_data():
    humans = []
    zombies = []
    with open(path, 'r+') as data:
        x, y = map(int, data.readline().split())
        player = Player(0, x, y)
        human_count = int(data.readline())
        for i in range(human_count):
            human_id, human_x, human_y = map(int, data.readline().split())
            humans.append(Character(human_id, human_x, human_y))
        zombie_count = int(data.readline())
        for i in range(zombie_count):
            zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = map(int, data.readline().split())
            zombies.append(Zombie(zombie_id, (zombie_x, zombie_y), (zombie_x_next, zombie_y_next)))
    return player, humans, zombies

