import math
import random
import time
from functools import wraps
from typing import List

from cVSz_classes import GameState, Player, Character, Zombie, Point
from constants import KILL_MODIFIER, BOARD_X_MAX, BOARD_Y_MAX
from visualization import visualize_game

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
    player = Player(0, Point(player_x, player_y), Point(0, 0))
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        humans.append(Character(human_id, Point(human_x, human_y), Point(0, 0)))
    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = [int(j) for j in input().split()]
        zombies.append(Zombie(zombie_id, Point(zombie_x, zombie_y), Point(zombie_x_next, zombie_y_next)))
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
        x, y = map(int, data.readline().split())
        player = Player(0, Point(x, y), Point(x, y))
        human_count = int(data.readline())
        for i in range(human_count):
            human_id, human_x, human_y = map(int, data.readline().split())
            humans.append(Character(human_id, Point(human_x, human_y), Point(human_x, human_y)))
        zombie_count = int(data.readline())
        for i in range(zombie_count):
            zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = map(int, data.readline().split())
            zombies.append(Zombie(zombie_id, Point(zombie_x, zombie_y), Point(zombie_x_next, zombie_y_next)))
    return dict(player=player, humans=humans, zombies=zombies)


# TODO: generate_init_population ---> generate_blank_population
@timeit
def generate_init_population(init_data, count: int) -> List[GameState]:
    population = []
    for id in range(count):
        population.append(GameState(id, init_data))
    return population


# TODO: should be method of GameState, parametrize debug/ or make Simulation class and allow for different scenarios
# TODO: keep GameState as class, but make it DataClass. GameState.increment_turn()
# TODO: make debug as Debugger Class
# TODO: make simulation Class?
# TODO: generate implies Generator, change name?
@timeit
def generate_population_from_selected_performers(selected_performers: List[GameState],
                                                 population_size: int,
                                                 generation_num: int) -> List[GameState]:
    """
    Generate new population of GameStates based on selected performers from previous population.
    Take move history up to generation number from selected performers and assign it evenly to new population as move_future.
    :param selected_performers: List of GameStates that will be used to generate new population.
    :param population_size: Number of genes in population.
    :param generation_num: Number of generation. Used to determine how many moves from start to take from selected_performers.
    :return: List of new GameStates.
    """
    population = generate_init_population(load_init_data_offline(), population_size)
    for i in range(len(population)):
        index: int = i % len(selected_performers)
        population[i].player.move_future = selected_performers[index].player.move_history[:generation_num + 1]
    return population


def simulate_evolution(population_size: int, top_performers_ratio: float, performers_survive_cnt: int, debug=True):
    """
    Simulate evolution of population of GameStates. Each evolution step consists of:
    1. Generate initial population of GameStates
    2. Do parent selection by getting top performers and random performers
    3. Use move_history of selected performers to guide first X moves of new population
    4. Repeat
    :param population_size: Number of genes in population.
    :param top_performers_ratio: Ratio of the best performers to be selected as parents for next generation.
    :param performers_survive_cnt: Total number of performers to be selected as parents for next generation.
    :param debug:
    :return:
    """

    assert population_size >= performers_survive_cnt, "Population size must be greater or equal to performers_survive_cnt"
    best_of = []

    # Generate initial population of GameStates
    population = generate_init_population(load_init_data_offline(), population_size)
    population = simulate_population(population)
    best_of.extend(get_top_performers(population, 1))

    for generation in range(50):
        # Get top performers
        top_performers_cnt = int(performers_survive_cnt * top_performers_ratio)
        selected_performers = get_top_performers(population, top_performers_cnt)
        # Fill the new population with random performers up to a limit given by performers_survive_cnt
        while len(selected_performers) < performers_survive_cnt:
            random_performer = get_random_performer(population)
            if random_performer not in selected_performers:
                selected_performers.append(random_performer)

        # Generate new population
        population = generate_population_from_selected_performers(selected_performers, population_size, generation)
        population = simulate_population(population)

        # Save the best performer
        best_of.extend(get_top_performers(population, 1))

    # Report overall results
    # TODO:Save top performers to file (move_history, score, generation)
    # Best of each evolution cycle
    report_population(best_of)
    # Best overall
    if best_of:
        report_single_game(get_top_performers(best_of, 1)[0])
    else:
        print('No best of found.')


# TODO: parametrize timeit to show how many populations it created
# @timeit
def simulate_population(population: List[GameState]) -> List[GameState]:
    for game_state in population:
        game_state.resolve_game(mode='previous_best')
    return population


def get_top_performers(population: List[GameState], top_cnt: int) -> List[GameState]:
    """
    Get top not-Game Over performers from population.
    :param population: Population of GameStates.
    :param top_cnt: Number of top performers to be selected.
    :return: List of top performers.
    """
    population = filter(lambda x: x.score >= 0, population)
    return sorted(population, key=lambda x: x.score, reverse=True)[:top_cnt]


def get_random_performer(population: List[GameState]) -> GameState:
    return random.sample(population, 1)[0]


# TODO: save human_cnt_max, zombie_cnt_max to GameState and use it here
def report_population(population: List[GameState], show_top_cnt=15):
    """
    Report basic statistics on bunch of GameStates: Top X score, avg score,
    """
    human_cnt_max = population[0].human_cnt_max
    zombie_cnt_max = population[0].zombie_cnt_max

    print(f"================================================================================")
    print(f'Max possible score: {calc_max_possible_score(human_cnt_max, zombie_cnt_max)}')
    # TODO: use filters()?
    scores = [round(gene.score) for gene in population]
    top_performers = sorted(scores, reverse=True)[:show_top_cnt]
    score_avg = round(sum(scores) / len(scores), 3)
    print(f"{top_performers=}")
    print(f"{score_avg=}")
    print(f"{score_avg=}")
    print(f"================================================================================")

    # print(f'{population[0].zombies[0].turn_death=}')
    # print(f'{population[0].zombies[0].alive=}')
    # print(f'{population[0].zombies[0].turn_death=}')
    # print(f'{population[0].zombies[1].alive=}')


def report_single_game(game: GameState):
    """
    Report basic statistics on a single GameState:
    """
    print(f'Game active: {game.active}')
    print(f'Game state: {game.state}')
    print(f'Player move_history_cnt: {len(game.player.move_history)}')
    print(f'Player move_future_cnt: {len(game.player.move_future)}')
    print(f'Game turn: {game.turn}')
    print(f'Player move_history: {game.player.move_history}')
    print(f'Player move_future: {game.player.move_future}')

    # Zombie deaths
    for zombie_id, zombie in enumerate(game.zombies):
        print(f'Zombie {zombie_id} turn_death: {zombie.turn_death}')

    # Human death
    for human_id, human in enumerate(game.humans):
        print(f'Human {human_id} turn_death: {human.turn_death}')

    # Visualize 
    visualize_game(game)


# TODO: formula for score calc is already in 2 places, consider moving it out
# TODO: consider moving this under GameState class
def calc_max_possible_score(human_cnt: int, zombie_cnt: int) -> float:
    sum_ = 0
    for nth_zombie_killed in range(zombie_cnt + 1):
        sum_ += (math.sqrt(human_cnt) * 10) * KILL_MODIFIER[nth_zombie_killed]
    return sum_


def generate_random_move():
    return Point(random.randint(0, BOARD_X_MAX), random.randint(0, BOARD_Y_MAX))


# TODO: Save top performers for analysis (as player.move_history)

def get_point_next(source_point: Point, target_point: Point, max_range: int) -> Point:
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
