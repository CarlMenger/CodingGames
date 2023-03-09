import math
import random
import time
from functools import wraps
from typing import List
from debug import debug_basic

from cVSz_classes import GameState, Player, Character, Zombie


path = 'input.txt'


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
def load_init_data_offline():
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
    return player, humans, zombies


@timeit
def generate_base_population(player, humans, zombies, count: int, weights) -> List[GameState]:
    population = []
    for id in range(count):
        population.append(GameState(id, player, humans, zombies, 0, weights))
    for gs in population:
        move = (random.randint(0, 16000), random.randint(0, 9000))
        gs.player.set_next_move(move)
    return population


# TODO: should be method of GameState, parametrize debug/ or make Simulation class and allow for different scenarios
# TODO: keep GameState as class, but make it DataClass. GameState.increment_turn()
# TODO: make debug as Debugger Class
# TODO: make 'move' a Point class
@timeit
def simulate_game_single_pop(gs: GameState) -> GameState:
    """ Simulate 1 population until loss/win"""
    c = 0
    assert isinstance(gs, GameState), 'Wrong input'
    while gs.active: 
        move = (random.randint(0, 16000), random.randint(0, 9000))
        gs.player.set_next_move(move)
        # print(f'Dist change: {game.avg_dist_change()}')
        gs.update_game_state()
        # debug_basic(gs, adc_action=True, adc_character='zombies', distance_matrix=True, zombie_points=True)
        debug_basic(gs, adc_action=False, adc_character='zombies', distance_matrix=False, zombie_points=False)
        c += 1
    return gs


def simulate_1turn_all(population: List[GameState]):
    new_pop = []
    for p in population:
        new_pop.append(simulate_game_single_pop(p))
    return new_pop


