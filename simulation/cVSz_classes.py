import math

KILL_MODIFIER = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
PLAYER_RANGE = 2000
ZOMBIE_RANGE = 400


class GameState:
    __slots__ = ('player', 'humans', 'zombies', 'score')

    def __init__(self, player, humans, zombies, score):
        self.player = player
        self.humans = humans
        self.zombies = zombies
        self.score = score

    def update_game_state(self):
        # player should  have player.point_next
        # move zombies
        # move player
        # player kills during movement
        # zombies kill
        # find next point for zombies?
        # update score

        self.zombies_move()
        self.player_move()
        self.player_kill()
        self.zombies_kill()
        
        self.update_score()

    def player_move(self):
        self.player.point = self.player.point_next
        # TODO: after this, no new point_next is set

    # FIXME: kill everything in path, not just on arrival?
    def player_kill(self):
        for zombie in self.zombies:
            if math.dist(self.player.point, zombie.point) <= PLAYER_RANGE:
                zombie.alive = False

    def zombies_move(self):
        for zombie in self.zombies:
            zombie.point = zombie.point_next
        # TODO:  find new point

    def zombies_kill(self):
        for zombie in self.zombies:
            for human in self.humans:
                if math.dist(zombie.point, human.point) <= ZOMBIE_RANGE:
                    human.alive = False

    def update_score(self):
        humans_alive = len([human for human in self.humans if human.alive == True])
        zombies_dead = len([zombie for zombie in self.zombies if zombie.alive == False])
        # zombies_alive = len([zombie for zombie in self.zombies if zombie.alive == True])
        if humans_alive == 0:
            self.score = 0
        elif zombies_dead == len(self.zombies):  # TODO: feels bug prone
            pass  # TODO: way to end the calc
        else:
            self.score += (math.sqrt(humans_alive) * 10) * (KILL_MODIFIER[zombies_dead] + 2 + 1)
            # +1 to compensate index

    def remove_dead_zombies(self):
        for zombie in self.zombies:
            if not zombie.alive:
                del zombie


class Character:
    _slots_ = ('id', 'point', 'point_next', 'alive')

    def __init__(self, id: int, point: tuple, point_next: tuple):
        self.id: int = id
        self.point: tuple = point
        self.point_next: tuple = point_next
        self.alive = True

    def __str__(self) -> str:
        return f'I am f{self.id} at: {self.point[0]}, {self.point[1]}'


class Player(Character):
    # _slots_ = ('id', 'point', 'point_next',)

    def __init__(self: super, id: int, point: tuple, point_next: tuple):
        super().__init__(id, point, point_next)


class Zombie(Character):
    _slots_ = (
        'points_next',
        'target_id',
        'target_point',
        'target_distance',
        'interception_turns',
    )

    def __init__(self, id: int, point: tuple, point_next: tuple):
        super().__init__(id, point, point_next)
        self.target_id: int = -1
        self.target_point: tuple = ()
        self.target_distance: float = float('inf')
        self.interception_turns: int = -1

    def set_target(self, target_id, target_point, target_distance, interception_turns):
        self.target_id: int = target_id
        self.target_point: tuple = target_point
        self.target_distance: float = target_distance
        self.interception_turns: int = interception_turns
        self.find_point_next(self.point, self.target_point)

    def find_point_next(self, point, target_point):
        # TODO: limit so to not overshoot the target?
        x0, y0 = point
        x1, y1 = target_point
        gradient = (y1 - y0) / (x1 - x0)
        point0 = x0 + 400 / math.sqrt((1 + gradient ** 2))
        point1 = x0 - 400 / math.sqrt((1 + gradient ** 2))
        assert isinstance(point0, float) and isinstance(point1, float), 'Wrong format in get_point_next() method'
        self.point_next = tuple([point0, point1])


# ZOMBIE find_target will be outside of class Zombie, Zombie only sets updated vars using set_target method