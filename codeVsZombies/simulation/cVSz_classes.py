import math
import random
from typing import List
from constants import PLAYER_RANGE, ZOMBIE_RANGE, KILL_MODIFIER
# from simulation.cVSz_funcs import generate_random_move


class GameState:
    __slots__ = ('id', 'player', 'humans', 'zombies', 'score', 'score_decision', 'turn', 'active', 'state',)

    def __init__(self, id, init_data, turn):
        self.id = id
        self.player: Player = init_data['player']
        self.humans: List[Character] = init_data['humans']
        self.zombies: List[Zombie] = init_data['zombies']

        self.score: int = 0  # Actual score, set as -1 on game loss
        self.score_decision: float = 0  # Output of scoring function for gene selection
        self.turn: int = 0
        # self.turn: int = turn  # FIXME: Why even initialize, always 0, nth players turn can be determined from Player class

        self.active: bool = True  # Is game still going
        self.state: int = 0  # 0: Not resolved, -1: Loss, 1: Win

    def __repr__(self):
        return f'Humans: {len(self.get_alive_humans())}/{len(self.humans)},\t' \
               f'Zombies: {len(self.get_alive_zombies())}/{len(self.zombies)},\t' \
               f'Score: {round(self.score)},\t' \
               f'Score_decision: {self.score_decision},\t' \
               f'Turn: {self.turn},\t' \
               f'State: {self.state},\t'

    def generate_random_move(self):
        return random.randint(0, 16000), random.randint(0, 9000)

    # TODO: this should be moved and have a way to change strategy of how to generate player moves
    def resolve_game(self, mode='random'):
        while self.active:
            self.turn += 1
            player_move = self.generate_random_move()
            self.resolve_turn(player_move)

            # print(self)

    def resolve_turn(self, player_move):
        """
        Simulate single turn. Update movements directions. Move player, move zombies. Kill.
        Check game status. Update Score.
        """
        # Moving
        self.set_player_next_move(player_move)
        self.zombies_find_next_target()  # zombies can be init with no next target
        self.zombies_move2next_point()
        self.player_move2next_point()

        # Killing
        self.player_kill()
        self.check_game_status()
        self.zombies_kill()  # humans.point changed
        self.check_game_status()

        self.update_score()

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
        for zombie in self.get_alive_zombies():
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
        return tuple(map(round, [x3, y3]))  # FIXME: rounding might cause slight overshooting (+0.4122875237472)

    # KILLING
    def player_kill(self):
        for zombie in self.get_alive_zombies():
            if math.dist(self.player.point, zombie.point) <= PLAYER_RANGE:
                zombie.alive = False
                zombie.turn_death = self.turn

    def zombies_kill(self):
        assert self.zombies and self.humans, 'No zombies alive or no humans alive!'
        for zombie in self.get_alive_zombies():
            for human in self.humans:
                assert isinstance(zombie, Zombie) and isinstance(human, Character), ''
                if math.dist(zombie.point, human.point) <= ZOMBIE_RANGE:
                    human.alive = False
                    human.turn_death = self.turn

    def update_score(self):
        # Loss
        if self.state == -1:
            self.score = -1
        else:
            humans_alive_cnt = len(self.get_alive_humans())
            assert humans_alive_cnt > 0, f'[Error] Scoring with {humans_alive_cnt} humans left'

            zombies_dead_this_turn_cnt = len(
                [zombie for zombie in self.zombies if not zombie.alive and zombie.turn_death == self.turn])
            if zombies_dead_this_turn_cnt > 0:
                self.score += (math.sqrt(humans_alive_cnt) * 10) * KILL_MODIFIER[zombies_dead_this_turn_cnt]

    def get_human_by_id(self, id):
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

    def check_game_status(self, print_status=False):
        """
        If all humans or all zombies are dead
        """

        if not self.get_alive_zombies():
            self.active = False
            self.state = 1
            # print('Game Over: Win')
        if not self.get_alive_humans():
            self.active = False
            self.state = -1
            # print('Game Over: Loss')
        # quit()
        # return False

    def fitting_score(self):
        """ Calc score to fit given gene (player move)
            features::
            score/killed zombies
            humans left
            score potential? (max possible point to earn)
            current score?

        """
        pass

    def avg_dist_change(self):
        """ Average change in distance between Player and All alive zombies.
            Potential feature for fitting func.
        ++ is good
        -- is bad
        """
        dist0 = 0  # Total dist to current point
        dist1 = 0  # Total dist to next point
        for z in self.get_alive_zombies():
            dist0 += math.dist(self.player.point, z.point)
            dist1 += math.dist(self.player.point_next, z.point)
        dist_diff = dist0 - dist1
        return dist_diff / len(self.get_alive_zombies())


class Character:
    _slots_ = ('id', 'point', 'point_next', 'move_history', 'alive', 'turn_death')

    def __init__(self, id: int, point: tuple, point_next: tuple):
        self.id: int = id
        self.point: tuple = point
        self.point_next: tuple = point_next
        self.move_history: List[tuple] = []
        self.alive = True  # FIXME: Can be replaced by turn_death
        self.turn_death = None

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

class Point:
    pass