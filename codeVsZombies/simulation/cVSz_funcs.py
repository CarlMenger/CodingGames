import math
import random
import time
from functools import wraps
from typing import List

from cVSz_classes import GameState, Player, Character, Zombie
from constants import KILL_MODIFIER

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


def load_init_data_online() -> dict:
    """
    Load data in online environment for a actual validation.
    """
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
    return dict(player=player, humans=humans, zombies=zombies)


@timeit
def load_init_data_offline() -> dict:
    """
    Load data from txt file structured in the same way as online data source. Returns dict of lists containing data
    necessary for initialization of GameState. Player Obj., List[Humans],  List[Zombie].
    """
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
    return dict(player=player, humans=humans, zombies=zombies)


@timeit
def generate_init_population(init_data, count: int) -> List[GameState]:
    population = []
    for id in range(count):
        population.append(GameState(id, init_data, 0))
    return population


# TODO: should be method of GameState, parametrize debug/ or make Simulation class and allow for different scenarios
# TODO: keep GameState as class, but make it DataClass. GameState.increment_turn()
# TODO: make debug as Debugger Class
# TODO: make 'move' a Point class
# TODO: make simulation Class?


# TODO: parametrize timeit to show how many populations it created
@timeit
def simulate_population(population_base: List[GameState]) -> List[GameState]:
    for genome in population_base:
        genome.resolve_game()
    return population_base


def report_population(population: List[GameState], human_cnt, zombie_cnt, show_top_cnt=15):
    """
    Report basic statistics on bunch of GameStates: Top X score, avg score,
    """

    print(f'Max possible score: {calc_max_possible_score(human_cnt, zombie_cnt)}')
    # TODO: use filters()?
    scores = [round(gene.score) for gene in population]
    top_performers = sorted(scores, reverse=True)[:show_top_cnt]
    score_avg = round(sum(scores) / len(scores), 3)
    print(f"{top_performers=}")
    print(f"{score_avg=}")
    print(f"{score_avg=}")

    # print(f'{population[0].zombies[0].turn_death=}')
    # print(f'{population[0].zombies[0].alive=}')
    # print(f'{population[0].zombies[0].turn_death=}')
    # print(f'{population[0].zombies[1].alive=}')


def report_single_game(game: GameState):
    """
    Report basic statistics on a single GameState:
    """
    print(f'Result: {game.state}')
    print(f'Turns num: {len(game.player.move_history)}')

    # Zombie death
    print(f'{game.zombies[0].turn_death=}')
    print(f'{game.zombies[1].turn_death=}')

    # Human death
    print(f'{game.humans[0].turn_death=}')
    print(f'{game.humans[1].turn_death=}')



# TODO: formula for score calc is already in 2 places, consider moving it out
def calc_max_possible_score(human_cnt: int, zombie_cnt: int) -> float:
    sum = 0
    for nth_zombie_killed in range(zombie_cnt + 1):
        sum += (math.sqrt(human_cnt) * 10) * KILL_MODIFIER[nth_zombie_killed]
    return sum

# 1 genome = 1 round == X turns
# 1 population = X genomes/ rounds

# TODO: Save top performers for analysis (as player.move_history)
