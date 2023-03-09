# from cVSz_classes import *
from cVSz_funcs import *
from visualization import visualize_turn
import timeit
from debug import debug_basic
def main():

    WEIGHTS = {
        'zombie_dist': 1,
        'human_dist': 1,
    }
    player, humans, zombies = load_init_data_offline()

    # Simulate 1 game
    game = GameState(id, player, humans, zombies, 0, WEIGHTS)
    game = simulate_1game_single(game)
    visualize_turn(game)

    # population = generate_base_population(player, humans, zombies, 10, WEIGHTS)
    # selected_population = selection(population)
    # mated_population = mating(selected_population)


    # new_generation = []
    # for pop in population:
    #     new_generation.append(simulate_1game(pop))
    # for gene in new_generation:
    #     print(gene.id)

    # TODO: Calculating score for move to already preselect better one?

if __name__ == '__main__':
    main()


# TODO: make load online data return data, same as offline
# TODO: feed the same data into GameState