from cVSz_funcs import load_init_data_online, load_init_data_offline, generate_init_population, simulate_population, \
    report_population, timeit, report_single_game
import platform

from simulation.visualization import visualize_turn


@timeit
def main():
    # NTB
    if platform.node() == 'CZ-L1132':
        game_state_init_data = load_init_data_offline()
    else:
        game_state_init_data = load_init_data_online()

    # TEMP TEST SETUP
    test_case_count = 1

    z_cnt = len(game_state_init_data['zombies'])
    h_cnt = len(game_state_init_data['humans'])

    population_base = generate_init_population(game_state_init_data, test_case_count)
    population_simulated = simulate_population(population_base)
    report_population(population_simulated, human_cnt=h_cnt, zombie_cnt=z_cnt)
    if test_case_count == 1:
        report_single_game(population_simulated[0])
        visualize_turn(population_simulated[0])


if __name__ == '__main__':
    main()

# TODO: Wtf is score == 0?
