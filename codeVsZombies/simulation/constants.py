"""
File for keeping constants.
"""

# Accessing these with number of zombies killed, if 1 is killed start at index = 1,
# if 0 killed, modify score change by 0.
KILL_MODIFIER = [0, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

# Distance to kill zombies. If distance to zombie <= range, zombie is killed.
PLAYER_RANGE = 2000

# Distance to kill npc humans. If distance to npc <= range, zombie is killed.
ZOMBIE_RANGE = 400

# Board size
BOARD_X_MAX = 16000
BOARD_Y_MAX = 9000


