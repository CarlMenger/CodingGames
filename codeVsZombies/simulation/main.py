from cVSz_funcs import load_init_data_online, load_init_data_offline, generate_init_population, simulate_population, \
    report_population, timeit, report_single_game, simulate_evolution
import platform

from visualization import visualize_game


@timeit
def main():
    simulate_evolution(gene_cnt=100, top_performers_ratio=0.5, performers_survive_cnt=20,)

    # TODO: Move all this to separate function
    # NTB
    # if platform.node() in ('CZ-L1132', 'DESKTOP-JK8TMGJ'):
    #     game_state_init_data = load_init_data_offline()
    # else:
    #     game_state_init_data = load_init_data_online()

    # TEMP TEST SETUP
    # test_case_count = 1
    #
    # population_base = generate_init_population(game_state_init_data, test_case_count)
    # population_simulated = simulate_population(population_base)
    # report_population(population_simulated,)
    # if test_case_count == 1:
    #     report_single_game(population_simulated[0])
    #     visualize_game(population_simulated[0])


if __name__ == '__main__':
    main()

# TODO: Wtf is score == 0?
# TODO: separate file simulation.py
