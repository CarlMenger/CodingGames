import sys
from collections import deque, Counter
import copy
from timeit import timeit
import random
import time
from threading import Thread


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000), file=sys.stderr)
        return result

    return timed


class BridgeNode:
    def __init__(self, state, parent_path=None, parent_action=None):
        self.state = state  # dict with x-pos, bikes, speed
        self.parent_path = parent_path
        self.parent_action = parent_action  # 1 of 5: SPEED, SLOW, UP, DOWN, JUMP
        self.children = []  # states after parent action, objs
        self.untried_actions = self.get_legal_actions()
        self.path = self.get_path()

    def get_path(self):
        if self.parent_path is None:
            return []
        else:
            return self.parent_path + [self.parent_action]

    def get_legal_actions(self):
        if self.state['speed'] == 0:
            return ['SPEED']
        out = ['SPEED', 'JUMP']  # init with always possible actions
        if self.state['speed'] > 1:  # SLOW
            out.append('SLOW')
        if 0 not in self.state['bikes']:  # 0 refers to bike in 0th lane
            out.append('UP')
        if 3 not in self.state['bikes']:  # 3 refers to bike in 4th lane
            out.append('DOWN')
        return out

    def expand(self):  # create every child for current node and return them / ignore terminal nodes
        for action in self.untried_actions:
            next_state = move(self.state, action)
            child_node = BridgeNode(
                next_state, parent_path=self.path, parent_action=action)
            if len(child_node.state['bikes']) >= _MIN_BIKES:
                self.children += [child_node]
        return self.children


# ---------------------------------------------------------------------------------------------------
#  FUNCTIONS
# ---------------------------------------------------------------------------------------------------

def move(parent_state, action):
    if action == 'JUMP':
        return move_distance(parent_state, jump=True)

    elif action == 'UP':
        return move_distance(parent_state, extra_lane='UP')

    elif action == 'DOWN':
        return move_distance(parent_state, extra_lane='DOWN')

    elif action == 'SLOW':
        return move_distance(parent_state, speed_change='-')

    elif action == 'SPEED':
        return move_distance(parent_state, speed_change='+')


def move_distance(parent_state, extra_lane=None, speed_change=None, jump=False):
    new_state = copy.deepcopy(parent_state)  # TODO: need to
    if speed_change == '+':
        new_state['speed'] += 1
    elif speed_change == '-':
        new_state['speed'] -= 1
    for bike_index in new_state['bikes']:
        traveled_distance = LANES[bike_index][new_state['x']:new_state['x'] + new_state['speed'] + 1]
        if extra_lane == 'UP':
            traveled_distance = traveled_distance[:-1]
            traveled_distance += LANES[bike_index - 1][new_state['x']: new_state['x'] + new_state['speed'] + 1]
        elif extra_lane == 'DOWN':
            traveled_distance = traveled_distance[:-1]
            traveled_distance += LANES[bike_index + 1][new_state['x']: new_state['x'] + new_state['speed'] + 1]
        elif jump:
            if traveled_distance:
                # print('traveled_distance for JUMP action: ', traveled_distance, file=sys.stderr)
                traveled_distance = traveled_distance[-1]
        if '0' in traveled_distance:
            new_state['bikes'].remove(bike_index)
    # Change bike indices
    if extra_lane == 'UP':
        new_state['bikes'] = [bike_i - 1 for bike_i in new_state['bikes']]
    elif extra_lane == 'DOWN':
        new_state['bikes'] = [bike_i + 1 for bike_i in new_state['bikes']]
    new_state['x'] = new_state['x'] + new_state['speed']  # TODO: used to be +1 here, dunno way, kinda sus
    return new_state


# @timeit
# Expand given node in depth, not creating the whole tree, with large depth somewhat guaranteeing quality of chosen path
def grow_tree(subroot_node):  # --> returns subtree of certain height
    not_fully_expanded = deque([subroot_node])
    all_nodes = []
    while not_fully_expanded:
        current_node = not_fully_expanded.popleft()
        if len(current_node.path) >= GROW_DEPTH + 1:  # stop the growth after reaching a certain depth
            break
        children = current_node.expand()
        # purposefully reversing list of children to have 'SPEED' on highest priority to deal with possible time outs
        not_fully_expanded.extendleft(list(reversed(children)))
        all_nodes.append(current_node)
    # cut last one as it is one depth too deep, easier this way than checking next node while not running out of index
    return all_nodes[:-1]


@timeit
def start_full_tree_search(init_node):
    def grow_tree_wide(subroot_node):  # --> returns subtree of certain height
        global all_nodes_wide
        not_fully_expanded = deque([subroot_node])
        all_nodes_wide = []
        while not_fully_expanded and grow_tree_wide_flag:
            current_node = not_fully_expanded.popleft()
            if len(current_node.path) >= GROW_DEPTH + 1:  # stop the growth after reaching a certain depth
                break
            children = current_node.expand()
            not_fully_expanded.extend(children)
            all_nodes_wide.append(current_node)

    grow_tree_wide_flag = True
    another_thread = Thread(target=grow_tree_wide, args=(init_node,))
    another_thread.daemon = True
    another_thread.start()
    time.sleep(TIMER_THREAD_2)
    print('all_nodes_wide nodes found: ', len(all_nodes_wide), file=sys.stderr)
    grow_tree_wide_flag = False


# @timeit
def get_next_node(nodes):
    try:
        max_distance = max([n.state['x'] for n in nodes])
        return [n for n in nodes if n.state['x'] == max_distance][0]
    except ValueError:
        print('WARNING: max_distance in FUNC get_next_node has probably no nodes inputted')
        return None


# @timeit
def get_next_greedy_node(nodes):
    greedy_nodes = [n for n in nodes if len(n.state['bikes']) == BIKES_N]
    if greedy_nodes:
        max_distance = max([n.state['x'] for n in greedy_nodes])
    else:
        print('WARNING: No greedy nodes were found!', file=sys.stderr)
        return None
    if max_distance >= _MIN_GREEDY_DISTANCE:
        potential_nodes = [n for n in greedy_nodes if n.state['x'] == max_distance]
        print('get_next_greedy_node RETURNING ', len(potential_nodes), ' / ', len(greedy_nodes), ' nodes',
              file=sys.stderr)
        return potential_nodes[0]
    print('NO ACCEPTABLE GREEDY NODE WAS FOUND', file=sys.stderr)
    return None


# ---------------------------------------------------------------------------------------------------
#  INIT
# ---------------------------------------------------------------------------------------------------
BIKES_N = int(input())  # the amount of motorbikes to control
_MIN_BIKES = int(input())  # the minimum amount of motorbikes that must survive
LANES = [input(), input(), input(), input()]
GROW_DEPTH = 30
GREED_STATUS = True  # Flag for turning on/off second thread exploring better nodes
TIMER_THREAD_2 = 0.1  # Time allocated to search for better nodes, 0.1 = 100 ms
_MIN_GREEDY_DISTANCE = 5  # Const used to prevent choosing short-term better move resulting in later failure
# ---------------------------------------------------------------------------------------------------
#  MAIN PROGRAM
# ---------------------------------------------------------------------------------------------------

while True:
    # ----------------------------- LOAD THIS ROUND INPUTS -----------------------------
    all_nodes_wide = []  # test one
    bike_ids = []
    speed = int(input())  # the motorbikes' speed
    for i in range(BIKES_N):
        x_temp, y, a = [int(j) for j in input().split()]
        # print("x, y, a...", x, y, a, file=sys.stderr, flush=True)
        if a == 1:
            bike_ids.append(y)
            x = x_temp
        state = {'speed': speed,
                 'bikes': bike_ids,
                 'x': x}

    # ----------------------------- SEARCH FOR 'GOOD ENOUGH' NODE -----------------------------
    init_node = BridgeNode(state, parent_path=None)
    found_nodes = grow_tree(init_node)
    next_node = get_next_node(found_nodes)
    # ----------------------------- SEARCH FOR 'BETTER' NODE -----------------------------
    if GREED_STATUS:
        start_full_tree_search(init_node)
        better_node = get_next_greedy_node(all_nodes_wide)
        if better_node:
            print('**Better node FOUND**', file=sys.stderr)
            next_node = better_node
        else:  # turn off searching for node where all bikes are alive, as this is no longer possible
            print('****TURNING OFF SEARCH FOR BETTER NODE****', file=sys.stderr)
            GREED_STATUS = False
    # ----------------------------------- OUTPUT -----------------------------------
    # print(next_node.path, file=sys.stderr)
    print(next_node.path[0])
