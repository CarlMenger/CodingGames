# from cVSz_classes import *
from cVSz_funcs import *
import timeit

# print('TIME*load_offline_data: ', timeit.timeit(stmt=load_offline_data, number=1000)/1000)
# print('TIME*calc_next_turn: ', timeit.timeit(stmt=calc_next_turn, number=1000)/1000)
humans, zombies = load_offline_data()
print(zombies)
print(humans[0].point)
