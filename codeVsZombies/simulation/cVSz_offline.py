# from cVSz_classes import *
from cVSz_funcs import *
from visualization import visualize_turn
import timeit

WEIGHTS = {
    'zombie_dist': 0.3,
    'human_dist': 0.8
}
player, humans, zombies = load_init_data_offline()

# Simul 1 game
# game = GameState(id, player, humans, zombies, 0, WEIGHTS)
# game.weights = WEIGHTS
# game = simulate_1game(game)
# visualize_turn(game)


population = generate_base_population(player, humans, zombies, 10, weights=WEIGHTS)
# TODO: Calculating score for move to already preselect better one?

new_generation = []
for pop in population:
    new_generation.append(simulate_1game(pop))
for gene in new_generation:
    print(gene.id)