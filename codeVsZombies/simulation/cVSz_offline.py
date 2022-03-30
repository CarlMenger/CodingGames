# from cVSz_classes import *
from cVSz_funcs import *
import timeit

# print('TIME*load_offline_data: ', timeit.timeit(stmt=load_offline_data, number=1000)/1000)
# print('TIME*calc_next_turn: ', timeit.timeit(stmt=calc_next_turn, number=1000)/1000)
player, humans, zombies = load_init_data_offline()

# TEST
# game_state = GameState(player, humans, zombies, 0)
# print(game_state)

population_t0 = base_population_generation(player, humans, zombies)

population_t1 = simulate_turn(population_t0)
