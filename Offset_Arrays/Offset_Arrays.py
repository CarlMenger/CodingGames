import sys
import math
import re

# print(" ", file=sys.stderr, flush=True)

letters = {}
n = int(input())
regex = '(^\w+)\[(\-?\d+).*\] = (.*)'

for i in range(n):
    array = re.match(regex, input())  # 'A[-1..1] = 1 2 3'
    key = array.group(1)
    offset = array.group(2)
    values = list(map(int, array.group(3).split(' ')))
    print('values', values, file=sys.stderr)
    values.append(offset)  # keep offset on last index
    letters[key] = values
assignment = input()


while len(re.findall('\w+', assignment)) > 1:
        nested_x = re.match('(\w+)\[(-?\d+)\].*', assignment)  # X[-666]
        nested_key = nested_x.group(1)
        nested_index = int(nested_x.group(2))  # 666
        offset = int(letters[nested_key][-1])
        new_value = str(letters[nested_key][nested_index-offset])
        assignment = assignment.replace(nested_x.group(0), new_value)

print(assignment)