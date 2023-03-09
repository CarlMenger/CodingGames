import math
import logging
from datetime import datetime
from typing import List
import numpy as np
import pandas as pd

from cVSz_classes import GameState
from logging.handlers import RotatingFileHandler

# Configure the logging module
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

current_time = datetime.today().strftime("%Y%m%d_%H-%M-%S")
handler = RotatingFileHandler(filename=rf'logs/{current_time}.log', maxBytes=1024 * 1024, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)


def print_zombie_points(ws):
    print('')
    for z in ws.get_alive_zombies():
        dist_change = math.dist(z.point, z.point_next)
        dist2target = math.dist(z.point, z.target_point)
        print(f'--- Zombie {z.id} --- ')
        print(f'{z.point} --> {z.point_next}:[{round(dist_change)}]; target/id: {z.target_point}/{z.target_id}')
        # print(f'Dist to target: {dist2target} ({round(dist2target / 400, 2)}) ')
        print(f'Score_decision: {ws.score_decision}')
        print('')


def print_distance_matrix(ws):
    print("{:<8} {:<10} {:<12}".format('ZOMBIE', 'CHARACTER', 'DISTANCE'))
    for zombie in ws.get_alive_zombies():
        for human in ws.get_alive_humans() + [ws.player]:
            print('{:<8} {:<10} {:<12}'.format(zombie.id, human.id, round(math.dist(zombie.point, human.point))))


def print_distance_matrix2(ws):
    matrix = []
    if not ws.get_alive_zombies(): return None

    for character in [ws.player] + ws.get_alive_humans():
        row = []
        for z in ws.get_alive_zombies():
            row.append(round(math.dist(character.point, z.point)))
        matrix.append(row)

    # Format output
    headers_col = [f'Zombie {_}' for _ in [z.id for z in ws.get_alive_zombies()]]  # zombie ids
    headers_row = [_ for _ in [h.id for h in [ws.player] + ws.get_alive_humans()]]  # player + humans ids
    headers_row = ['Player'] + [f'Human {x}' for x in headers_row if x != 0]
    print(pd.DataFrame(matrix, columns=list(headers_col), index=list(headers_row)))
    print('')


def print_adc(ws: GameState, characters='zombies'):
    """ Potential feature for fitting func
    average distance change to zombies
    ++ is good
    -- is bad
    """
    if characters.lower() == 'zombies':
        obj_list = ws.get_alive_zombies()
    else:
        obj_list = ws.get_alive_humans()

    if not obj_list:
        print(f'ADC: No {characters} found!')
    else:
        dist0 = 0  # Total dist to current point
        dist1 = 0  # Total dist to next point
        for z in obj_list:
            dist0 += math.dist(ws.player.point, z.point)
            dist1 += math.dist(ws.player.point_next, z.point)
        dist_diff = (dist0 - dist1) / len(obj_list)
        # return dist_diff
        print(f'Average distance change to {characters}: {dist_diff}')


def debug_basic(ws, adc_action=False, adc_character='zombies', distance_matrix=False, zombie_points=False):
    print(f' ===================== {ws.turn} ===================== ')
    debug_options = 'Debug options:'
    if adc_action:
        debug_options += f'  - ADC_{adc_character}\n'
        print_adc(ws, adc_character)
    if distance_matrix:
        debug_options += f'  - Distance matrix\n'
        print_distance_matrix(ws)
    if zombie_points:
        print_zombie_points(ws)
        debug_options += f'  - Zombie points\n'

    print_distance_matrix2(ws)
    logger.warning(debug_options)
