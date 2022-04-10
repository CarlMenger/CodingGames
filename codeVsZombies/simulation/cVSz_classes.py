import math

from typing import List

KILL_MODIFIER = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
PLAYER_RANGE = 2000
ZOMBIE_RANGE = 400


class GameState:
    __slots__ = ('id', 'player', 'humans', 'zombies', 'score', 'score_decision', 'turn')

    def __init__(self, id, player, humans, zombies, turn):
        self.id = id
        self.player: Player = player
        self.humans: List[Character] = humans
        self.zombies: List[Zombie] = zombies
        self.score: int = 0
        self.score_decision: float = 0
        self.turn: int = turn

    def __repr__(self):
        return f'Humans: {len(self.get_alive_humans())}/{len(self.humans)}, ' \
               f'Zombies: {len(self.get_alive_zombies())}/{len(self.zombies)},' \
               f'Score: {self.score},' \
               f'Turn: {self.turn}'

    def debug(self):
        # TODO: dist matrix zombies to player+humans
        print("{:<8} {:<10} {:<12}".format('ZOMBIE', 'CHARACTER', 'DISTANCE'))
        for zombie in self.get_alive_zombies():
            for human in self.get_alive_humans() + [self.player]:
                print('{:<8} {:<10} {:<12}'.format(zombie.id, human.id, round(math.dist(zombie.point, human.point))))

    # TEST FUNC
    def test_zombie_points(self, num):
        print('')
        for z in self.zombies:
            dist_change = math.dist(z.point, z.point_next)
            dist2target = math.dist(z.point, z.target_point)
            print(f'--- Zombie {z.id} --- ')
            print(f'{z.point} --> {z.point_next}; target/id: {z.target_point}/{z.target_id} ++ {round(dist_change)}')
            print(f'Dist {dist2target} ({round(dist2target/400,2)})')
            print('')

    # **************************************************************************************************************
    def update_game_state(self):
        # Moving
        self.zombies_find_next_target()  # zombies can be init with no next target
        self.test_zombie_points(f" Turn {self.turn}")
        self.zombies_move2next_point()
        self.player_move2next_point()

        # Killing
        self.player_kill()
        self.is_game_over()
        self.zombies_kill()  # humans.point changed
        self.is_game_over()

        # Recalculating
        self.update_score()
        self.remove_dead_zombies()

    # MOVEMENT
    def player_move2next_point(self):
        self.player.move_history.append(self.player.point)  # Save current point
        self.player.point_next = self.get_point_next(self.player.point, self.player.point_next, 'p')
        self.player.point = self.player.point_next

    def set_player_next_move(self, next_point: tuple) -> None:
        self.player.point_next = next_point

    # FIXME: kill everything in path, not just on arrival?
    def zombies_find_next_target(self):
        # check if zombie is alive --> move all zombie funcs after zombie is alive condition
        # need to recheck target validity each turn, player moving around might change it
        for zombie in self.get_alive_zombies():
            assert zombie is not None, 'Unlive zombie looking for target!'
            # check target status from last round (not killed this or previous rounds)
            target = self.find_nearest_character(zombie)  # Find target
            assert isinstance(target, Character), 'Wrong/No target found for zombie!'
            zombie.target_point = target.point  #
            zombie.target_id = target.id
            zombie.point_next = self.get_point_next(zombie.point, zombie.target_point)  # Set path to target

    def zombies_move2next_point(self):
        for zombie in self.zombies:
            zombie.move_history.append(zombie.point)  # Save current point
            zombie.point = zombie.point_next  # Current point = Next point

    def get_point_next(self, source_point: tuple, target_point: tuple, char='z') -> tuple:
        x1, y1 = source_point
        x2, y2 = target_point
        range = [PLAYER_RANGE, ZOMBIE_RANGE][char == 'z']
        if range > math.dist(source_point, target_point):  # Prevent overshooting
            return target_point
        distance = math.dist(source_point, target_point)
        r = range / distance  # segment ratio

        x3 = r * x2 + (1 - r) * x1  # find point that divides the segment
        y3 = r * y2 + (1 - r) * y1  # into the ratio (1-r):r
        return tuple(map(round, [x3, y3]))  # FIXME: rounding might cause slight overshooting (400.4122875237472)

    # KILLING
    def player_kill(self):
        for zombie in self.zombies:
            if math.dist(self.player.point, zombie.point) <= PLAYER_RANGE:
                print(f'Player kills Zombie {zombie.id}')
                zombie.alive = False

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
    _slots_ = ('id', 'point', 'point_next', 'move_history', 'alive')

    def __init__(self, id: int, point: tuple, point_next: tuple):
        self.id: int = id
        self.point: tuple = point
        self.point_next: tuple = point_next
        self.move_history: List[tuple] = []
        self.alive = True

    def __str__(self) -> str:
        return f'{type(self)}, ID: {self.id} at: {self.point[0]}, {self.point[1]}'


class Player(Character):
    # _slots_ = ('move_history',)

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
        self.target_id: int = -1  # FIXME: useful?
        self.target_point: tuple = ()
        self.target_distance: float = float('inf')  # FIXME: useful?
        self.interception_turns: int = -1  # FIXME: useful?

# TODO: why keep point_next for player? Its generated externally and just inputted
