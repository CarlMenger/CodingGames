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
    _slots_ = ('id', 'x', 'y', 'coords')

    def __init__(self, id: int, x: int, y: int) -> None:
        self.id: int = id
        self.x: int = x  # TODO: use just point system and remove this
        self.y: int = y  # TODO: use just point system and remove this
        self.coords: tuple = (x, y)

    def __str__(self) -> str:
        return f'I am f{self.id} at: {self.x}, {self.y}'


class Human(Character):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)


class Zombie(Character):
    _slots_ = (
        'x_next',
        'y_next',
        'coords_next',
        'target',
        'target_interception',
        'target_coords',
        'target_distance',
        '',
    )

    def __init__(self, id: int, x: int, y: int, x_next: int, y_next: int):
        super().__init__(id, x, y)
        self.x_next: int = x_next  # TODO: use just point system and remove this
        self.y_next: int = y_next  # TODO: use just point system and remove this
        self.coords_next: tuple = (x_next, y_next)

        self.target: int = -1
        self.target_interception: float = -1
        self.target_coords: tuple = get_target_coords()
        self.target_distance: float = float('inf')
        self.interception: tuple = tuple()

        self.player_interception = -1

    def set_target_vars(self, humans):  # TODO: add new attrs
        target_distance = float('inf')
        for h in humans:
            if h.distance <= target_distance:
                self.target = h.id
                target_distance = distance(h.coords, self.coords)
        self.target_interception = target_distance // 400

    # after each round, recalculate all distances/coords/interceptions
    def recalculate_coors(self):
        pass

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


def get_human(id: int, humans) -> Human:
    out = [h for h in humans if h.id == id]
    assert out, 'Human with f{id} not found!'
    return out[0]


def go_to_human(id: int, humans: list):
    player = get_human(len(humans), humans)
    human = get_human(id, humans)
    return go_to((player.x, player.y), (human.x, human.y))


def find_mandatory_coords(humans):
    return [z.target for z in zombies if z.target_interception <= 1.0]


# game loop
while True:
    humans, zombies = init_round_inputs()
    # print("humans after init",humans[0].id, file=sys.stderr, flush=True)
    # print(humans)
    mandatory_coords = find_mandatory_coords(humans)
    if len(humans) == 1:
        order = go_to_human(humans[0].id, humans)

    # default

    order = go_to_human(0, humans)
    # print(f'{order}')
    print(*order)


