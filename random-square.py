#!/usr/bin/env python3
import sys
from random import randint
import re
# might try python3s cmd library
mv_regex = "[a|b|c|d|e|f|g]:[1-8]"
move_regex = re.compile(mv_regex)
clor_regex = 'w|b'
color_regex = re.compile(clor_regex)

if 'raw_input' in dir(): # python 2
    get_input = raw_input
else: # python 3
    get_input = input

chess_notation = {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}

def get_random_position():
    letter = randint(1,8)
    number = randint(1,8)
    return chess_notation[letter] + ":" + str(number)

def get_color(position):
    letter,number = position.split(':')
    number = int(number) - 1 
    # We subtract 1 to go from chess notation to 0-7, 
    # which is easier to use with modulo arithmetic.
    if letter in ('a','c', 'e', 'g'):
        initial_color = 0 # black
    else:
        initial_color = 1 # white
    number_color = (initial_color + number) % 2
    if number_color == 1:
        return 'w'
    return 'b'

print("Random Position")
print("-----")
position = get_random_position()
print(position)
print("")
print("What color is this position?")
answer = get_input() 
print("")
print('You answered: {}'.format(answer))
assert color_regex.match(answer), 'Answer must match regex {}!'.format(clor_regex)
right_answer = get_color(position)
if answer == right_answer:
    print("You answered correctly!")
else:
    print("Incorrect! Right answer was {}".format(right_answer))

