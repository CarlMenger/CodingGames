# from cVSz_classes import *
from cVSz_funcs import *
import timeit


population_t0 = [load_init_data_offline()]
# population_t0 = base_population_generation(player, humans, zombies)

population_t0[0].debug()
population_t1 = simulate_turn(population_t0)

# for gs in population_t1:
#     gs.debug()
