from cVSz_classes import GameState
import matplotlib.pyplot as plt
from constants import PLAYER_RANGE, ZOMBIE_RANGE, BOARD_X_MAX, BOARD_Y_MAX


# TODO: Make this able to take GS in any state and visualize up to that point, being able to save
# TODO: some genomes as ash path and use it for debugging
# TODO: turn by turn visualization?


def visualize_game(gs: GameState):
    #  =========== Init settings ===========
    plt.title = f'Score: {gs.score}'
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim(0, BOARD_X_MAX)
    plt.ylim(0, BOARD_Y_MAX)

    # ====================== Zombies ======================
    for z in gs.zombies:

        # Plot last point
        # plt.annotate(z.id, z.point_current, color='green')
        # plt.scatter(x, y, s=10, facecolors='g', edgecolors='g')

        # Plot history points + current point
        x = [move.x for move in z.move_history]
        y = [move.y for move in z.move_history]
        # x = [move.x for move in z.move_history + [z.point_current]]
        # y = [move.y for move in z.move_history + [z.point_current]]

        # Circle when killed by Player
        if z.turn_death:
            x_death = x[z.turn_death - 1]
            y_death = y[z.turn_death - 1]
            plt.scatter(x_death, y_death, s=ZOMBIE_RANGE, facecolors='none', edgecolors='green')  # circle

        # Plot turn numbers
        for i, point in enumerate(z.move_history):
            plt.annotate(i, xy=(point.x, point.y), color='green')

        # Plot lines
        plt.plot(x, y, color='green', linestyle='dashed', linewidth=1,
                 marker='o', markerfacecolor='green', markersize=2)
        # Plot arrows
        for i in range(len(x) - 1):
            x_arrow = x[i + 1] - x[i]
            y_arrow = y[i + 1] - y[i]
            plt.quiver(x[i], y[i], x_arrow, y_arrow, angles='xy', scale_units='xy', scale=1,
                       color='green', width=0.0035, alpha=0.5)

    # ====================== Humans ======================
    for h in gs.humans:
        x, y = h.point_current.x, h.point_current.y
        human_color = ['black', 'blue'][h.alive]  # Blue alive, Black dead

        plt.scatter(x, y, facecolors=human_color, edgecolors=human_color)  # Point on current position
        if h.turn_death:
            plt.scatter(x, y, s=ZOMBIE_RANGE, facecolors='none', edgecolors=human_color)  # circle on death

    # ====================== Player ======================
    p = gs.player
    # x, y = p.point_current.x, p.point_current.y

    # Plot history points + current point
    x = [move.x for move in p.move_history + [p.point_current]]
    y = [move.y for move in p.move_history + [p.point_current]]

    # Plot lines
    plt.plot(x, y, color='red', linestyle='dashed', linewidth=1,
             marker='o', markerfacecolor='red', markersize=2)

    # Plot turn numbers
    for i, point in enumerate(p.move_history):
        plt.annotate(i, xy=(point.x, point.y), color='red')

    # Plot arrows
    for i in range(len(x) - 1):
        x_arrow = x[i + 1] - x[i]
        y_arrow = y[i + 1] - y[i]
        plt.quiver(x[i], y[i], x_arrow, y_arrow, angles='xy', scale_units='xy', scale=1,
                   color='red', width=0.0035, alpha=0.5)
    # ====================== Plot ======================
    plt.show()

# TODO: move colors to constants or visualization config
