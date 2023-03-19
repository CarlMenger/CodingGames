import math
import random
from typing import List
from constants import PLAYER_RANGE, ZOMBIE_RANGE, KILL_MODIFIER



# TODO: Start using Point class
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class GameState:
    __slots__ = ('id', 'player', 'humans', 'zombies', 'score', 'score_decision', 'turn', 'active', 'state',)

    def __init__(self, id, init_data,):
        self.id = id
        self.player: Player = init_data['player']
        self.humans: List[Character] = init_data['humans']
        self.zombies: List[Zombie] = init_data['zombies']

        self.score: int = 0  # Actual score, set as -1 on game loss
        self.score_decision: float = 0  # Output of scoring function for gene selection
        self.turn: int = 0

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
        return Point(random.randint(0, 16000), random.randint(0, 9000))

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
        self.zombies_kill()  # humans.point_current changed
        self.check_game_status()

        self.update_score()

    # MOVEMENT
    def player_move2next_point(self):
        self.player.move_history.append(self.player.point_current)  # Save current point
        self.player.point_next = self.get_point_next(self.player.point_current, self.player.point_next, PLAYER_RANGE)
        self.player.point_current = self.player.point_next

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
            zombie.target_point = target.point_current  #
            zombie.target_id = target.id
            zombie.point_next = self.get_point_next(zombie.point_current, zombie.target_point,
                                                    ZOMBIE_RANGE)  # Set path to target

    def zombies_move2next_point(self):
        for zombie in self.get_alive_zombies():
            zombie.move_history.append(zombie.point_current)  # Save current point
            zombie.point_current = zombie.point_next  # Current point = Next point

    def get_point_next(self, source_point: Point, target_point: Point, range: int) -> Point:
        # FIXME: rounding might cause slight overshooting (+0.4122875237472)
        from cVSz_funcs import dist
        x1, y1 = source_point.x, source_point.y
        x2, y2 = target_point.x, target_point.y
        if range > dist(source_point, target_point):  # Prevent overshooting
            return target_point
        distance = dist(source_point, target_point)
        r = range / distance  # segment ratio

        x3 = r * x2 + (1 - r) * x1  # find point that divides the segment
        y3 = r * y2 + (1 - r) * y1  # into the ratio (1-r):r
        return Point(round(x3, 2), round(y3, 2))

    # KILLING

    def player_kill(self):
        from cVSz_funcs import dist
        for zombie in self.get_alive_zombies():
            if dist(self.player.point_current, zombie.point_current) <= PLAYER_RANGE:
                zombie.alive = False
                zombie.turn_death = self.turn

    def zombies_kill(self):
        from cVSz_funcs import dist
        assert self.zombies and self.humans, 'No zombies alive or no humans alive!'
        for zombie in self.get_alive_zombies():
            for human in self.humans:
                assert isinstance(zombie, Zombie) and isinstance(human, Character), ''
                if dist(zombie.point_current, human.point_current) <= ZOMBIE_RANGE:
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
        from cVSz_funcs import dist
        assert zombie.alive, 'Non-alive zombie looking for target'
        dist_min = 99999
        h = None
        for human in self.get_alive_humans() + [self.player]:
            distance = dist(zombie.point_current, human.point_current)
            if distance < dist_min:
                dist_min = distance
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

    # def fitting_score(self):
    #     """ Calc score to fit given gene (player move)
    #         features::
    #         score/killed zombies
    #         humans left
    #         score potential? (max possible point to earn)
    #         current score?
    #
    #     """
    #     pass

    # def avg_dist_change(self):
    #     """ Average change in distance between Player and All alive zombies.
    #         Potential feature for fitting func.
    #     ++ is good
    #     -- is bad
    #     """
    #     dist0 = 0  # Total dist to current point
    #     dist1 = 0  # Total dist to next point
    #     for z in self.get_alive_zombies():
    #         dist0 += dist(self.player.point_current, z.point_current)
    #         dist1 += dist(self.player.point_next, z.point_current)
    #     dist_diff = dist0 - dist1
    #     return dist_diff / len(self.get_alive_zombies())


class Character:
    __slots__ = ('id', 'point_current', 'point_next', 'move_history', 'alive', 'turn_death')

    def __init__(self, id: int, point_current: Point, point_next: Point):
        self.id: int = id
        self.point_current: Point = point_current  # Point, character is currently at.
        self.point_next: Point = point_next  # Point, character is moving towards.
        self.move_history: List[Point] = []
        self.alive: bool = True  # FIXME: Can be replaced by turn_death
        self.turn_death = None

    def __str__(self) -> str:
        return f'{type(self)}, ID: {self.id} at: {self.point_current.x}, {self.point_current.y}'


class Player(Character):

    def __init__(self: super, id: int, point_current: Point, point_next: Point):
        super().__init__(id, point_current, point_next)

    def set_next_move(self, next_move: Point):
        self.point_next = next_move


class Zombie(Character):
    __slots__ = (
        'points_next',
        'target_id',
        'target_point',
        'target_distance',
        'interception_turns',
    )

    def __init__(self, id: int, point_current: Point, point_next: Point):
        super().__init__(id, point_current, point_next)
        self.target_id: int = -1
        self.target_point: Point(0, 0)
        self.target_distance: float = float('inf')  # FIXME: useful?
        self.interception_turns: int = -1  # FIXME: useful?
