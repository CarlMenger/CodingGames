import numpy as np
from cVSz_classes import GameState
import matplotlib.pyplot as plt

# TODO: Make this able to take GS in any state and visualize up to that point, being able to save
# TODO: some genomes as ash path and use it for debugging
# TODO: turn by turn visualization?


def visualize_turn(gs: GameState):
    # Common settings
    plt.title = f'Score: {gs.score}'
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim(0, 16000)
    plt.ylim(0, 9000)

    # Plot zombies
    for z in gs.zombies:
        x, y = z.point
        r = 400
        # Plot last one
        plt.annotate(z.id, z.point, color='green')
        plt.scatter(x, y, s=10, facecolors='g', edgecolors='g')  # point
        # plt.scatter(x, y, s=r, facecolors='none', edgecolors='green')  # circle

        # Plot history
        x = [move[0] for move in z.move_history]
        y = [move[1] for move in z.move_history]

        # Circle when died
        if z.turn_death:
            x_death = x[z.turn_death-1]
            y_death = y[z.turn_death-1]
            plt.scatter(x_death, y_death, s=r, facecolors='none', edgecolors='green')  # circle

        for i, point in enumerate(z.move_history):
            plt.annotate(i, xy=point)

        # add last points not in history
        x.append(z.point[0])
        y.append(z.point[1])
        plt.plot(x, y, color='green', linestyle='dashed', linewidth=1,
                 marker='o', markerfacecolor='green', markersize=2)

    # Plot humans
    for h in gs.humans:
        human_color = ['black', 'blue'][h.alive]  # Blue alive, Black dead

        x, y = h.point
        r = 400
        plt.scatter(x, y, facecolors=human_color, edgecolors=human_color)
        plt.scatter(x, y, s=r, facecolors='none', edgecolors=human_color)

        if h.turn_death:
            plt.annotate(h.turn_death, h.point, color='blue')
            plt.scatter(x, y, s=r, facecolors='none', edgecolors='blue')  # circle on death
    # Plot player
    p = gs.player
    x, y = p.point
    r = 2000
    # Plot last one
    plt.scatter(x, y, s=10, facecolors='r', edgecolors='r')
    plt.scatter(x, y, s=r, facecolors='none', edgecolors='red')
    # Plot history
    x = [move[0] for move in p.move_history]
    y = [move[1] for move in p.move_history]
    # turn = [_ for _ in range(len(p.move_history))]

    # add last points not in history
    x.append(p.point[0])
    y.append(p.point[1])
    plt.plot(x, y, color='red', linestyle='dashed', linewidth=1,
             marker='o', markerfacecolor='red', markersize=2)
    for i, point in enumerate(p.move_history):
        plt.annotate(i, xy=point)
    plt.show()

    # plotting the points
    # plt.plot(x, y, color='green', linestyle='dashed', linewidth=3,
    #          marker='o', markerfacecolor='blue', markersize=12)
