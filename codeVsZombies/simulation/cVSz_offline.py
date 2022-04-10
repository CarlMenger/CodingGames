# from cVSz_classes import *
from cVSz_funcs import *
from visualization import visualize_turn
import timeit

# population_t0 = base_population_generation(player, humans, zombies)

# population_t0[0].debug()
# population_t1 = simulate_turn(population_t0)
#
# for gs in population_t1:
#     gs.debug()
population = [load_init_data_offline()]
c = 0
while len(population[0].get_alive_zombies()) and len(population[0].get_alive_humans()):
    print(f'Turn {c}')
    move = (random.randint(0, 16000), random.randint(0, 9000))
    population[0].player.set_next_move(move)
    population = simulate_turn(population)
    c += 1

visualize_turn(population[0])
print('Move_history:', population[0].zombies[0].move_history)
population[0].debug()