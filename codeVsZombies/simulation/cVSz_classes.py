import math

from typing import List

KILL_MODIFIER = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
PLAYER_RANGE = 2000
ZOMBIE_RANGE = 400


class GameState:
    __slots__ = ('id', 'player', 'humans', 'zombies', 'score')

    def __init__(self, id, player, humans, zombies, score):
        self.id = id
        self.player: Player = player
        self.humans: List[Character] = humans
        self.zombies: List[Zombie] = zombies
        self.score: int = score

    def __repr__(self):
        return f'Humans: {len(self.get_alive_humans())}/{len(self.humans)}, ' \
               f'Zombies: {len(self.get_alive_zombies())}/{len(self.zombies)},' \
               f' Score: {self.score}'

    def debug(self):
        # TODO: dist matrix zombies to player+humans
        print("{:<8} {:<10} {:<12}".format('ZOMBIE', 'CHARACTER', 'DISTANCE'))
        for zombie in self.get_alive_zombies():
            for human in self.get_alive_humans() + [self.player]:
                print('{:<8} {:<10} {:<12}'.format(zombie.id, human.id, round(math.dist(zombie.point, human.point))))

    def update_game_state(self):
        # Moving
        self.zombies_move()
        self.player_move()

        # Killing
        self.player_kill()
        self.is_game_over()
        self.zombies_kill()
        self.is_game_over()

        # Recalculating
        self.zombies_find_next_target()  # zombies can be init with no next target
        self.update_score()
        self.remove_dead_zombies()

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

    def zombies_find_next_target(self):
        # check if zombie is alive --> move all zombie funcs after zombie is alive condition
        # need to recheck target validity each turn, player moving around might change it
        for zombie in self.get_alive_zombies():
            assert zombie is not None, 'Unlive zombie looking for target!'
            # check target status from last round (not killed this or previous rounds)
            target = self.find_nearest_character(zombie)
            assert isinstance(target, Character), 'Wrong/No target found for zombie!'
            zombie.set_point_next(target.point)  # set next move

    def zombies_kill(self):
        assert self.zombies and self.humans, 'No zombies alive or no humans alive!'
        for zombie in self.get_alive_zombies():
            for human in self.humans:
                assert isinstance(zombie, Zombie) and isinstance(human, Character), ''
                if math.dist(zombie.point, human.point) <= ZOMBIE_RANGE:
                    print(f'Zombie {zombie.id} kills Human {human.id}')
                    human.alive = False

    def update_score(self):
        humans_alive_cnt = len(self.get_alive_humans())
        zombies_dead_cnt = len([zombie for zombie in self.zombies if not zombie.alive])
        self.score += (math.sqrt(humans_alive_cnt) * 10) * (KILL_MODIFIER[zombies_dead_cnt] + 2 + 1)

    def remove_dead_zombies(self):
        for zombie in self.zombies:
            if not zombie.alive:
                del zombie

    def get_human(self, id):
        for human in self.humans:
            if human.id == id:
                return human

    def find_nearest_character(self, zombie):
        assert zombie.alive, 'Non-alive zombie looking for target'
        dist_min = 99999
        h = None
        for human in self.get_alive_humans() + [self.player]:
            dist = math.dist(zombie.point, human.point)
            if dist < dist_min:
                dist_min = dist
                h = human
        return h

    def get_alive_zombies(self):
        return [zombie for zombie in self.zombies if zombie.alive]

    def get_alive_humans(self):
        return [human for human in self.humans if human.alive]

    def is_game_over(self):
        if not self.get_alive_humans():
            print('Game Over: Loss')
            print(f'{self}')
            # quit()
        elif not self.get_alive_zombies():
            print('Game Over: Win')
            print(f'{self}')
            # quit()
        return False


class Character:
    _slots_ = ('id', 'point', 'point_next', 'alive')

    def __init__(self, id: int, point: tuple, point_next: tuple):
        self.id: int = id
        self.point: tuple = point
        self.point_next: tuple = point_next
        self.alive = True

    def __str__(self) -> str:
        return f'{type(self)}, ID: {self.id} at: {self.point[0]}, {self.point[1]}'


class Player(Character):
    # _slots_ = ('id', 'point', 'point_next',)

    def __init__(self: super, id: int, point: tuple, point_next: tuple):
        super().__init__(id, point, point_next)

    def set_next_move(self, next_move: tuple):
        self.point_next = next_move


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

    # def set_target(self, target_id, target_point, target_distance, interception_turns):
    #     self.target_id: int = target_id
    #     self.target_point: tuple = target_point
    #     self.target_distance: float = target_distance
    #     self.interception_turns: int = interception_turns
    #     self.find_point_next(self.target_point)

    def set_point_next(self, target_point):
        # TODO: limit so to not overshoot the target?
        x0, y0 = self.point
        x1, y1 = target_point
        gradient = (y1 - y0) / (x1 - x0)
        point0 = x0 + 400 / math.sqrt((1 + gradient ** 2))
        point1 = x0 - 400 / math.sqrt((1 + gradient ** 2))
        assert isinstance(point0, float) and isinstance(point1, float), 'Wrong format in get_point_next() method'
        self.point_next = tuple([point0, point1])

# ZOMBIE find_target will be outside of class Zombie, Zombie only sets updated vars using set_target method
