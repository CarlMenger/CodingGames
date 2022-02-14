"""
d=sqr((x1-x0)^2 + (y1-y0)^2)
a=(r0^2-r1^2+d^2)/(2*d)
h=sqr(r0^2-a^2)
x2=x0+a*(x1-x0)/d
y2=y0+a*(y1-y0)/d
x3=x2+h*(y1-y0)/d       // also x3=x2-h*(y1-y0)/d
y3=y2-h*(x1-x0)/d       // also y3=y2+h*(x1-x0)/d
"""

import sys
import math

print("", file=sys.stderr, flush=True)


class Character:
    _slots_ = ('id', 'x', 'y', 'points')

    def __init__(self, id: int, x: int, y: int) -> None:
        self.id: int = id
        self.point: tuple = (x, y)

    def __str__(self) -> str:
        return f'I am f{self.id} at: {self.point[0]}, {self.point[1]}'


class Human(Character):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)


class Zombie(Character):
    _slots_ = (
        'x_next',
        'y_next',
        'points_next',
        'target_id',
        'target_point',
        'target_distance',
        'interception_turns',
        # 'interception_point',
        # 'player_interception',
    )

    def __init__(self, id: int, x: int, y: int, x_next: int, y_next: int):
        super().__init__(id, x, y)
        self.point_next: tuple = (x_next, y_next)
        self.target_id: int = -1
        self.target_point: tuple = ()
        self.target_distance: float = float('inf')
        self.interception_turns: float = -1
        # self.set_target_vars()

    def set_target_vars(self):  # TODO: add new attrs
        global HUMANS
        target_distance = float('inf')
        # find closest target # TODO: not working
        for h in HUMANS:
            human_distance = distance(h.point, self.point)
            if human_distance < target_distance:  # find closer target
                self.target_id = h.id
                target_distance = human_distance

        # calc all other attrs
        self.point_next = self.get_point_next()
        self.target_point = h.point # HUMANS[self.target_id].point
        self.target_distance = target_distance
        print('self.target_distance: ', self.target_distance, file=sys.stderr)
        self.interception_turns = (target_distance // 400) + 1
        # self.interception_point =
        # self.player_interception =

    def get_point_next(self):
        x0, y0 = self.point
        x1, y1 = self.target_point
        gradient = (y1 - y0) / (x1 - x0)
        point0 = x0 + 400 / math.sqrt((1 + gradient ** 2))
        point1 = x0 - 400 / math.sqrt((1 + gradient ** 2))
        assert point0 is float and point1 is float, 'Wrong format in get_point_next() method'
        return (point0, point1)


def init_round_inputs():
    """ keep 2 lists of objects, keep player as last id/position human"""
    humans = []
    zombies = []
    x, y = [int(i) for i in input().split()]
    human_count = int(input())
    for i in range(human_count):
        human_id, human_x, human_y = [int(j) for j in input().split()]
        humans.append(Human(human_id, human_x, human_y))
    zombie_count = int(input())
    for i in range(zombie_count):
        zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next = [int(j) for j in input().split()]
        zombies.append(Zombie(zombie_id, zombie_x, zombie_y, zombie_x_next, zombie_y_next))
    humans.append(Human(human_count, x, y))  # add player at the end
    return humans, zombies


def distance(a, b):
    return math.dist(a, b)


def go_to(_from: tuple,
          _to: tuple):  # FIXME not doing what u are expecting, finding middle not 1000 units in that direction
    a, b = _from
    x, y = _to
    return tuple([int((a + x) / 2), int((b + y) / 2)])  # FIXME this cant be proper tuple declaration


def get_human(id: int) -> Human:
    global HUMANS
    out = [h for h in HUMANS if h.id == id]
    print("out", out, file=sys.stderr, flush=True)
    assert len(out) > 0, f'Human with ID: {id} not found!'
    return out[0]


def go_to_human(id: int):
    player = get_human(len(HUMANS) - 1)
    return go_to(player.point, HUMANS[id].point)


def recalculate_zombies() -> None:
    global ZOMBIES
    for z in ZOMBIES: z.set_target_vars()


def get_t0_points():
    return [z.point_next for z in ZOMBIES if z.interception_turns <= 1.0]


def get_t1_points():
    return [z.point_next for z in ZOMBIES if 1.0 <= z.interception_turns <= 2.0]


# TODO, sorted list of inception turns and use that for point selection

def get_circles_intersection(point_a, point_b, range_0, range_1):
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1
    print('gci input points:', point_a, point_b, file=sys.stderr)

    distance = math.dist(point_a, point_b)
    x0, y0 = point_a
    x1, y1 = point_b
    if distance > range_0 + range_1:  # no intersection
        return None
    elif distance > range_0 + range_1:  # 1 intersection
        pass
    # One circle within other
    elif distance < abs(range_0 - range_1):
        return None
    # coincident circles
    if distance == 0 and range_0 == range_1:
        return None
    else:  # 2 intersections
        a = (range_0 ** 2 - range_1 ** 2 + distance ** 2) / (2 * distance)
        h = math.sqrt(range_0 ** 2 - a ** 2)
        x2 = x0 + a * (x1 - x0) / distance
        y2 = y0 + a * (y1 - y0) / distance
        x3 = x2 + h * (y1 - y0) / distance
        y3 = y2 - h * (x1 - x0) / distance
        x4 = x2 - h * (y1 - y0) / distance
        y4 = y2 + h * (x1 - x0) / distance

        return (x3, y3), (x4, y4)


# game loop
while True:
    HUMANS, ZOMBIES = init_round_inputs()
    for z in ZOMBIES: z.set_target_vars()
    # default
    # order = go_to_human(0)
    # print("humans after init",humans[0].id, file=sys.stderr, flush=True)
    t0_points = get_t0_points()
    t1_points = get_t1_points()
    print('t0_points: ', t0_points, file=sys.stderr)
    print('t0_points: ', t1_points, file=sys.stderr)
    print(ZOMBIES[0].interception_turns, file=sys.stderr)
    if len(ZOMBIES) == 2:  # test scenario
        a = ZOMBIES[0].point_next
        b = ZOMBIES[1].point_next
        intersection_1, intersection_2 = get_circles_intersection(a, b, 2000, 2000)
        order = intersection_1
    if len(HUMANS) == 1:
        order = go_to_human(HUMANS[0].id)


    print(*order)
