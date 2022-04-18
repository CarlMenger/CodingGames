# from cVSz_classes import *
from cVSz_funcs import *
from visualization import visualize_turn
import timeit

WEIGHTS = {
    'zombie_dist': 0.3,
    'human_dist': 0.8
}
player, humans, zombies = load_init_data_offline()

# Simulate 1 game
game = GameState(id, player, humans, zombies, 0, WEIGHTS)
game.weights = WEIGHTS
game = simulate_1game_single(game)
visualize_turn(game)


# TODO: Chain funcs?
population = generate_base_population(player, humans, zombies, 10, weights=WEIGHTS)
selected_population = selection(population)
mated_population = mating(selected_population)
# crossover
# mutation



# new_generation = []
# for pop in population:
#     new_generation.append(simulate_1game(pop))
# for gene in new_generation:
#     print(gene.id)

# TODO: Calculating score for move to already preselect better one?
