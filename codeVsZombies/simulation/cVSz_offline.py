# from cVSz_classes import *
from cVSz_funcs import *
import timeit

# population_t0 = base_population_generation(player, humans, zombies)

# population_t0[0].debug()
# population_t1 = simulate_turn(population_t0)
#
# for gs in population_t1:
#     gs.debug()
population = [load_init_data_offline()]
c = 0
while c < 5000:
    print(f'Turn {c}')
    move = (random.randint(0, 16000), random.randint(0, 9000))
    population[0].player.set_next_move(move)
    population = simulate_turn(population)
    c += 1
