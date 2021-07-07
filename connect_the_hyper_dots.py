import sys
import math


# print('', file=sys.stderr, flush=True)

class Point:
    def __init__(self, label, coordinates):
        self.label: str = label
        self.coordinates = list(map(int, coordinates))

    def __str__(self):
        return 'Coordinates: ', self.coordinates

    def distance2point(self, point2) -> int:
        distance = []
        for coord_i in range(len(self.coordinates)):
            distance += [(point2.coordinates[coord_i] - self.coordinates[coord_i]) ** 2]
        return math.sqrt(sum(distance))

    def find_closest_point(self, points):
        print('------------------------CALLED BY: ', self.label, '------------------------', file=sys.stderr)
        lowest_dist = float('inf')
        closest_point = None
        for point in points:
            point_dist = self.distance2point(point)
            if point_dist <= lowest_dist:
                lowest_dist = point_dist
                closest_point = point
        return closest_point


def find_point_by_label(label: str) -> Point:
    return [p for p in points_ls if p.label == label][0]


def axis_crossed(cp: Point, np: Point) -> bool:
    for i in range(len(cp.coordinates)):
        if (cp.coordinates[i] < 0 < np.coordinates[i]) or (cp.coordinates[i] > 0 > np.coordinates[i]):
            return True
    return False


# INIT DATA
phrase = ''
points_ls = []
count, n = [int(i) for i in input().split()]

for i in range(count):
    point_data = input().split()
    point = Point(point_data[0], point_data[1:])
    points_ls.append(point)

# MAIN LOOP
init_point_coords = [0 for i in range(n)]
current_point = Point('', init_point_coords)
while len(points_ls):
    print(phrase, file=sys.stderr)
    next_point = current_point.find_closest_point(points_ls)
    if axis_crossed(current_point, next_point):
        phrase += ' '
    phrase += next_point.label
    current_point = next_point
    points_ls.remove(next_point)

# OUTPUT
print(phrase)
