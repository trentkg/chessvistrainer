#!/usr/bin/env python3
import cmd
import re
from collections import namedtuple
from random import randint
from datetime import datetime

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

Trial = namedtuple("Trial", ['number', 'correct', 'total_time', 'position'])


class ChessVisualizationTrainer(cmd.Cmd):
    intro = "Chess visualization trainer. Choose a game to play! Type help or '?' to see a list of commands.\n"
    prompt = '(chess-trainer)'
    file = None

    def do_rs(self, arg):
        '''Displays a random square on the chess board, repeatedly. 'rs 10' would play the game for 10 trials. Respond with 'w' for 'white' and 'b' for black. Displays statistics at the end.'''
        num_trials = int(arg.split()[0])
        RandomSquareGame(rounds=num_trials).cmdloop()
        return True 

class RandomSquareGame(cmd.Cmd):
    intro="Enter the color ('w' or 'b') of the random position generated"
    prompt='(rs)'
    
    def __init__(self, rounds):
        super(RandomSquareGame,self).__init__()
        assert rounds > 0, 'Number of rounds for random square must be greater than 0'
        self.rounds = rounds
        self.cur_pos = None
        self.cur_trial_end_time = None
        self.round_results = []

    def preloop(self):
        self.cur_pos = get_random_position()
        self.intro += '.\n Ready?... GO!\n\n\n{} ?'.format(self.cur_pos)
        self._start_clock()

    def _start_clock(self):
        self._trial_stime = datetime.now()

    def _stop_clock(self):
        self._trial_etime = datetime.now()

    def get_trial_time(self):
        diff = self._trial_etime - self._trial_stime
        return diff.total_seconds()

    def precmd(self, line):
        self._stop_clock()
        return line

    def postcmd(self,stop,line):
        if not stop:
            self.cur_pos = get_random_position()
            self._start_clock()
            self.stdout.write("{} ? \n".format(self.cur_pos))
        return stop

    def parseline(self, line):
        if not color_regex.match(line):
            return None
        return line
    
    def default(self, line):
        self.stdout.write('Color must match regex {}\n'.format(color_regex))

    def onecmd(self, line):
        if line is None:
            return self.emptyline()

        color = self.parseline(line)
        if color is None:
            return self.default(line)
        right_answer = get_color(self.cur_pos)
        if color == right_answer:
            self.stdout.write("Correct!\n")
            correct = True
        else:
            self.stdout.write("Incorrect! Answer was {}\n".format(right_answer))

            correct = False
        round_number = len(self.round_results) + 1
        self.round_results.append(Trial(number=round_number,correct=correct,total_time=self.get_trial_time(), position=self.cur_pos))
        if round_number >= self.rounds:
            stop = True
        else:
            stop = False
        return stop
    
    def postloop(self):
        correct = 0.0
        incorrect = 0.0
        total_time = 0.0
        for trial in self.round_results:
            correct +=int(trial.correct)
            incorrect += int(not trial.correct)
            total_time += trial.total_time
        avg_time = round(total_time/self.rounds, 2)
        perc_correct = round(correct/self.rounds, 3)
        self.stdout.write("\n\n\nRandom square session Finished!\n")
        self.stdout.write("Number Correct: {} out of {}\n".format(int(correct), int(self.rounds)))
        self.stdout.write("Percent Correct: {}\n".format(perc_correct))
        self.stdout.write("Average time per answer in seconds: {}\n".format(avg_time))


if __name__ == "__main__":
    ChessVisualizationTrainer().cmdloop()
