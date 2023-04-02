from cVSz_funcs import timeit, simulate_evolution


@timeit
def main():
    simulate_evolution(population_size=2,
                       top_performers_ratio=1,
                       performers_survive_cnt=1,
                       generation_cnt=1,
                       )


if __name__ == '__main__':
    main()

# TODO: Wtf is score == 0?
# TODO: separate file simulation.py ?
# TODO: maybe just set player move in get_player_move() rather than returning it here and feeding it to resolve_turn()
# TODO: end simulation if perfect score is found
# TODO: add id logging for population, game states, and generations. Use combination of number and letters
# TODO: move load_data() to consts to avoid loading it every time I call generate_blank_population()
