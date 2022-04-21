import math
import logging
from datetime import datetime

OUTPUT_DIR = "D:\__CodingGames\coding_games\codeVsZombies\simulation\debug_dump"
today = datetime.today()
current_time = today.strftime("%Y%m%d_%H-%M-%S")
logger = logging.getLogger('mylogger')
handler = logging.FileHandler(f'{OUTPUT_DIR}\{current_time}.log')
logger.addHandler(handler)


# logger.warning('This is a WARNING message')
# logger.error('This is an ERROR message')
# logger.critical('This is a CRITICAL message')


def test_zombie_points(ws, num):
    print('')
    for z in ws.get_alive_zombies():
        dist_change = math.dist(z.point, z.point_next)
        dist2target = math.dist(z.point, z.target_point)
        print(f'--- Zombie {z.id} --- ')
        print(f'{z.point} --> {z.point_next}; target/id: {z.target_point}/{z.target_id} ++ {round(dist_change)} ')
        print(f'Dist before moving {dist2target} ({round(dist2target / 400, 2)}) ')
        print(f'Score_decision: {ws.score_decision}')
        print('')


def print_distance_matrix(ws):
    print("{:<8} {:<10} {:<12}".format('ZOMBIE', 'CHARACTER', 'DISTANCE'))
    for zombie in ws.get_alive_zombies():
        for human in ws.get_alive_humans() + [ws.player]:
            print('{:<8} {:<10} {:<12}'.format(zombie.id, human.id, round(math.dist(zombie.point, human.point))))


def get_avg_dist_change(ws):
    """ Potential feature for fitting func
    ++ is good
    -- is bad
    """
    dist0 = 0  # Total dist to current point
    dist1 = 0  # Total dist to next point
    for z in ws.get_alive_zombies():
        dist0 += math.dist(ws.player.point, z.point)
        dist1 += math.dist(ws.player.point_next, z.point)
    dist_diff = dist0 - dist1
    return dist_diff / len(ws.get_alive_zombies())


def debug_basic(ws):
    avg_dist_change = get_avg_dist_change(ws)
