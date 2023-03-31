import math
from typing import List

from constants import PLAYER_RANGE, ZOMBIE_RANGE, KILL_MODIFIER


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
    __slots__ = (
        'id', 'player', 'humans', 'zombies', 'human_cnt_max', 'zombie_cnt_max', 'score', 'score_decision',
        'turn', 'active', 'state',
    )

    def __init__(self, id, init_data, ):
        self.id = id
        self.player: Player = init_data['player']
        self.humans: List[Character] = init_data['humans']
        self.zombies: List[Zombie] = init_data['zombies']
        self.human_cnt_max = len(self.humans)
        self.zombie_cnt_max = len(self.zombies)

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

    def resolve_game(self, strategy='previous_best'):
        from codeVsZombies.simulation.cVSz_funcs import generate_random_move, get_point_next
        while self.active:
            self.turn += 1
            # --- Decide player move ---
            # if last zombie alive, move to it
            # TODO: move to nearest zombie

            # At default, player moves randomly
            random_point = generate_random_move()
            player_move = get_point_next(self.player.point_current, random_point, PLAYER_RANGE)
            # or use predefined moves up to certain turn
            if strategy == 'previous_best' and self.turn < len(self.player.move_future):
                player_move = self.player.move_future[self.turn]

            self.player.point_next = player_move
            # --- resolve turn ---
            self.resolve_turn()

    def resolve_turn(self):
        """
        Simulate single turn. Update movements directions. Move player, move zombies. Kill.
        Check game status. Update Score.
        """
        # Moving
        self.zombies_find_next_target()  # zombies can be init with no next target
        self.zombies_move()
        self.player_move()

        # Killing
        self.player_kill()
        self.check_game_status()
        self.zombies_kill()  # humans.point_current changed
        self.check_game_status()

        self.update_score()

    def player_move(self):
        self.player.move_to_next_point()

    # FIXME: kill everything in path, not just on arrival?
    def zombies_find_next_target(self):
        from codeVsZombies.simulation.cVSz_funcs import get_point_next, find_nearest_character
        # check if zombie is alive --> move all zombie funcs after zombie is alive condition
        # need to recheck target validity each turn, player moving around might change it
        for zombie in self.get_alive_zombies():
            assert zombie is not None, 'Unlive zombie looking for target!'
            # check target status from last round (not killed this or previous rounds)
            target = find_nearest_character(zombie, self.get_alive_humans() + [self.player])  # Find target
            assert isinstance(target, Character), 'Wrong/No target found for zombie!'
            zombie.target_point = target.point_current
            zombie.target_id = target.id
            zombie.point_next = get_point_next(zombie.point_current,
                                               zombie.target_point,
                                               ZOMBIE_RANGE)  # Set path to target

    def zombies_move(self):
        for zombie in self.get_alive_zombies():
            zombie.move_to_next_point()

    def player_kill(self):
        from cVSz_funcs import dist
        for zombie in self.get_alive_zombies():
            if dist(self.player.point_current, zombie.point_current) <= PLAYER_RANGE:
                zombie.die(self.turn)

    def zombies_kill(self):
        from cVSz_funcs import dist
        for zombie in self.get_alive_zombies():
            for human in self.humans:
                if dist(zombie.point_current, human.point_current) <= ZOMBIE_RANGE:
                    human.die(self.turn)

    def update_score(self):
        # Loss
        if self.state == -1:
            self.score = -1
        else:
            humans_alive_cnt = len(self.get_alive_humans())
            assert humans_alive_cnt > 0, f'[Error] Trying to assign positive score with {humans_alive_cnt} humans left'

            zombies_dead_this_turn_cnt = len(
                [zombie for zombie in self.zombies if not zombie.alive and zombie.turn_death == self.turn])
            if zombies_dead_this_turn_cnt > 0:
                self.score += (math.sqrt(humans_alive_cnt) * 10) * KILL_MODIFIER[zombies_dead_this_turn_cnt]

    def get_alive_zombies(self):
        return [zombie for zombie in self.zombies if zombie.alive]

    def get_alive_humans(self):
        return [human for human in self.humans if human.alive]

    def check_game_status(self):
        """
        If all humans or all zombies are dead, end the game.
        """
        # Win
        if not self.get_alive_zombies():
            self.active = False
            self.state = 1

        # Loss
        if not self.get_alive_humans():
            self.active = False
            self.state = -1

    def report(self, visualize=True):
        from codeVsZombies.simulation.cVSz_funcs import calc_max_possible_score
        from codeVsZombies.simulation.visualization import visualize_game

        print(f'Game active: {self.active}')
        print(f'Game state: {self.state}')
        print(f'Player move_history_cnt: {len(self.player.move_history)}')
        print(f'Player move_future_cnt: {len(self.player.move_future)}')
        print(f'Game turn: {self.turn}')
        print(f'Player move_history: {self.player.move_history}')
        print(f'Player move_future: {self.player.move_future}')
        print(f'Max score: {calc_max_possible_score()}')
        print(f'Score: {self.score}')

        # Zombie deaths
        for zombie_id, zombie in enumerate(self.zombies):
            print(f'Zombie {zombie_id} turn_death: {zombie.turn_death}')

        # Human death
        for human_id, human in enumerate(self.humans):
            print(f'Human {human_id} turn_death: {human.turn_death}')

        # Visualize
        if visualize:
            visualize_game(self)


class Population:
    def __init__(self, generation: int, game_states: List[GameState]):
        self.generation = generation
        self.game_states = game_states
        self.score_max = None  # TODO: make default -1?
        self.score_avg = None  # TODO: make default -1?

    def __repr__(self):
        return f"""
            Count       : {self.__len__()}
            Generation  : {self.generation}
            Best score  : {self.score_max}
            Avg score   : {self.score_avg}
            """

    def __len__(self):
        return len(self.game_states)

    def get_best_game_states(self, count=1):
        best_game_states = sorted([game_state for game_state in self.game_states if game_state.score > 0],
                                  key=lambda x: (x.score, len(x.get_alive_humans())), reverse=True)
        return best_game_states[:count]

    def set_score_max(self):
        self.score_max = max([game_state.score for game_state in self.game_states])

    def set_score_avg(self):
        self.score_avg = sum([game_state.score for game_state in self.game_states]) / len(self.game_states)

    def add_game_states(self, game_states: List[GameState]):
        self.game_states.extend(game_states)

    def simulate(self, strategy='previous_best'):
        for game_state in self.game_states:
            game_state.resolve_game(strategy=strategy)

    def report(self):
        self.set_score_max()
        self.set_score_avg()
        from codeVsZombies.simulation.cVSz_funcs import calc_max_possible_score
        print(f"================================================================================")
        # print(f'Max possible score: {calc_max_possible_score()}')
        print(self)
        print(f"================================================================================")


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

    def die(self, turn: int):
        self.alive = False
        self.turn_death = turn

    def move_to_next_point(self):
        self.move_history.append(self.point_current)
        self.point_current = self.point_next
        self.point_next = None  # TODO: Remove this line?


class Player(Character):

    def __init__(self: super, id: int, point_current: Point, point_next: Point):
        super().__init__(id, point_current, point_next)
        self.move_future: List[Point] = []

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
