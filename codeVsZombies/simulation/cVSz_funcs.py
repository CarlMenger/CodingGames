import math
import platform
import random
import time
from functools import wraps
from typing import List
import copy

from cVSz_classes import GameState, Player, Character, Zombie, Point, Population
from constants import BOARD_X_MAX, BOARD_Y_MAX

path = 'input.txt'

global max_possible_score


def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kw):
        tstart = time.time()
        output = my_func(*args, **kw)
        tend = time.time()
        print('"{}" took {:.3f} ms to execute\n'.format(my_func.__name__, (tend - tstart) * 1000))
        return output

    return timed


# def calc_max_possible_score(human_cnt_max, zombie_cnt_max) -> float:
#     sum_ = 0
#     for nth_zombie_killed in range(zombie_cnt_max + 1):
#         sum_ += (math.sqrt(human_cnt_max) * 10) * KILL_MODIFIER[nth_zombie_killed]
#     return sum_


@timeit
def load_data():
    # NTB
    if platform.node() in ('CZ-L1132', 'DESKTOP-JK8TMGJ'):
        return load_init_data_offline()
    else:
        return load_init_data_online()


def load_init_data_online() -> dict:
    """
    Load data in an online environment for actual code testing.
    """
    humans = []
    zombies = []

    # Player
    player_x, player_y = [int(i) for i in input().split()]

    # Humans
    human_cnt_max = int(input())
    player = Player(0, Point(player_x, player_y), Point(0, 0))
    for i in range(human_cnt_max):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        humans.append(Character(human_id, Point(human_x, human_y), Point(0, 0)))

    # Zombies
    zombie_cnt_max = int(input())
    for i in range(zombie_cnt_max):
        zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = [int(j) for j in input().split()]
        zombies.append(Zombie(zombie_id, Point(zombie_x, zombie_y), Point(zombie_x_next, zombie_y_next)))

    # max_possible_score = calc_max_possible_score(human_cnt_max, zombie_cnt_max)
    return dict(player=player, humans=humans, zombies=zombies)


def dist(p: Point, q: Point) -> float:
    return math.sqrt((p.x - q.x) ** 2.0 + (p.y - q.y) ** 2.0)


def load_init_data_offline() -> dict:
    """
    Load data from txt file structured in the same way as online data source. Returns dict of lists containing data
    necessary for initialization of GameState. Player Obj., List[Humans],  List[Zombie].
    """
    humans = []
    zombies = []

    with open(path, 'r+') as data:
        # Player
        x, y = map(int, data.readline().split())
        player = Player(0, Point(x, y), Point(x, y))

        # Humans
        human_cnt_max = int(data.readline())
        for i in range(human_cnt_max):
            human_id, human_x, human_y = map(int, data.readline().split())
            humans.append(Character(human_id, Point(human_x, human_y), Point(human_x, human_y)))

        # Zombies
        zombie_cnt_max = int(data.readline())
        for i in range(zombie_cnt_max):
            zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = map(int, data.readline().split())
            zombies.append(Zombie(zombie_id, Point(zombie_x, zombie_y), Point(zombie_x_next, zombie_y_next)))

    return dict(player=player, humans=humans, zombies=zombies)


@timeit  # "generate_blank_population" took 0.000 ms to execute
def generate_blank_population(count: int, generation_id=0) -> Population:
    init_data = load_data()
    game_states = []
    for n in range(count):
        init_data = copy.deepcopy(init_data)
        game_states.append(GameState(n, generation_id, init_data))
    return Population(generation_id, game_states=game_states)


# FIXME: Make sure gene_cnt is doing what it is suppose to do.
# TODO: should be method of GameState, parametrize debug/ or make Simulation class and allow for different scenarios
# TODO: make debug as Debugger Class
# TODO: make simulation Class?
# @timeit "create_population_from_selected_performers" took 0.000 ms to execute
def create_population_from_selected_performers(parent_pop: List[GameState],
                                               population_size: int,
                                               gene_crossover_cnt: int,
                                               generation_id: int) -> Population:
    """
    Generate new population of GameStates based on selected performers.
    Take move history up to given turn number from selected performers and assign it evenly to new population as move_future.
    :param parent_pop: Population that will be used to generate new population.
    :param population_size: Number of genes in population.
    :param gene_crossover_cnt: Number of turns to be taken from move_history of selected performers and assigned to new population as move_future.
    :param generation_id: ID of generation to be assigned to new population.
    :return: List of new GameStates.
    """
    new_pop: Population = generate_blank_population(population_size, generation_id)
    for i in range(len(new_pop)):
        index: int = i % len(parent_pop)
        new_pop.game_states[i].player.move_future = parent_pop[index].player.move_history[:gene_crossover_cnt + 1]
    return new_pop


@timeit
def simulate_evolution(population_size: int,
                       top_performers_ratio: float,
                       performers_survive_cnt: int,
                       generation_cnt: int):
    """
    Simulate evolution of population of GameStates. Each evolution step consists of:
    1. Generate initial population of GameStates
    2. Do parent selection by getting top performers and random performers
    3. Use move_history of selected performers to guide first X moves of new population
    4. Repeat
    :param population_size: Number of genes in population.
    :param top_performers_ratio: Ratio of the best performers to be selected as parents for next generation.
    :param performers_survive_cnt: Total number of performers to be selected as parents for next generation.
    :param generation_cnt: Number of generations to simulate.
    :return:
    """
    top_performers_cnt = int(performers_survive_cnt * top_performers_ratio)

    # Do input checks
    assert top_performers_ratio <= 1.0, f"top_performers_ratio must be <= 1.0, got {top_performers_ratio}"
    assert top_performers_ratio > 0.0, f"top_performers_ratio must be > 0.0, got {top_performers_ratio}"
    assert performers_survive_cnt > 0, f"performers_survive_cnt must be > 0, got {performers_survive_cnt}"
    assert generation_cnt >= 0, f"generation_cnt must be > 0, got {generation_cnt}"
    assert population_size > 0, f"population_size must be > 0, got {population_size}"

    if population_size < performers_survive_cnt:
        population_size = performers_survive_cnt
        print(
            f"[Warning] population_size must be ({population_size}) >= performers_survive_cnt ({performers_survive_cnt}). "
            f"Setting population_size to {performers_survive_cnt}.")

    # Generation 0: selected_performers == initial_population
    population = generate_blank_population(population_size, generation_id=0)
    population.simulate()
    best_of: Population = Population(generation_id=0, game_states=population.get_best_game_states(top_performers_cnt))

    # Generations 1-X
    for generation_id in range(generation_cnt+1):
        # Select
        selected_performers = best_of.get_best_game_states(top_performers_cnt)
        # Fill the new population with random performers from previous generation up to a limit
        while len(selected_performers) < performers_survive_cnt:
            random_performer = get_random_performer(population)
            if random_performer not in selected_performers:
                selected_performers.append(random_performer)

        # TODO: :param gene_crossover_cnt this is here if we wanna have multiple generations with different
        # TODO: crossover genes passed to children than generation id
        # Generate new population
        population = create_population_from_selected_performers(selected_performers,
                                                                population_size,
                                                                gene_crossover_cnt=generation_id,
                                                                generation_id=generation_id)

        # Simulate 
        population.simulate()

        # Save the best
        best_of.add_game_states(population.get_best_game_states(top_performers_cnt))
        best_of.generation = generation_id  # TODO: wtf is this?

    best_of.report()


def get_random_performer(population: Population) -> GameState:
    return random.sample(population.game_states, 1)[0]


# TODO: formula for score calc is already in 2 places, consider moving it out

def generate_random_move(x_min=0, x_max=BOARD_X_MAX, y_min=0, y_max=BOARD_Y_MAX, ):
    assert x_min <= x_max, "x_min must be <= x_max"
    assert y_min <= y_max, "y_min must be <= y_max"
    assert x_min >= 0, "x_min must be >= 0"
    assert y_min >= 0, "y_min must be >= 0"
    assert x_max <= BOARD_X_MAX, "x_max must be <= BOARD_X_MAX"
    assert y_max <= BOARD_Y_MAX, "y_max must be <= BOARD_Y_MAX"
    return Point(random.randint(x_min, x_max), random.randint(y_min, y_max))


# TODO: Save top performers for analysis (as player.move_history)

def get_point_in_range(source_point: Point, target_point: Point, max_range: int) -> Point:
    """
    Get next point on path to target_point, within given range.
    :param source_point:
    :param target_point:
    :param max_range:
    :return:
    """
    # FIXME: rounding might cause slight overshooting (+0.4122875237472)
    x1, y1 = source_point.x, source_point.y
    x2, y2 = target_point.x, target_point.y
    if max_range > dist(source_point, target_point):  # Prevent overshooting
        return target_point
    distance = dist(source_point, target_point)
    r = max_range / distance  # segment ratio

    x3 = r * x2 + (1 - r) * x1  # find point that divides the segment
    y3 = r * y2 + (1 - r) * y1  # into the ratio (1-r):r
    return Point(round(x3, 2), round(y3, 2))


def find_nearest_character(hunter, prays: List):
    assert hunter.alive, f'Non-alive {type(hunter)} looking for target'
    assert prays, f'No pray to hunt'
    dist_min = 99999
    final_pray = None
    for pray in prays:
        distance = dist(hunter.point_current, pray.point_current)
        if distance < dist_min:
            dist_min = distance
            final_pray = pray
    return final_pray


def dist2targets(source, targets) -> List[float]:
    """
    Distance from source to targets.
    """
    return [dist(source, target) for target in targets]
