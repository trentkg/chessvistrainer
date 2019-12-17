#!/usr/bin/env python3
import cmd
import re
import csv
import os
from collections import namedtuple
from random import randint
from datetime import datetime

mv_regex = "[a|b|c|d|e|f|g|h]:[1-8]"
move_regex = re.compile(mv_regex)
clor_regex = 'w|b'
color_regex = re.compile(clor_regex)

chess_notation = {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}
chess_notation_backwards = {value:key for key,value in chess_notation.items()}

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

def get_brother_square(position):
    letter,number = position.split(':')
    x = chess_notation_backwards[letter]
    y = int(number)

    xbro =  -1*x + 9
    ybro =  -1*y + 9

    return "{}:{}".format(chess_notation[xbro], ybro)

Round = namedtuple("Round", ['number', 'correct', 'total_time', 'position', 'answer', 'utc_datetime'])

class ChessVisualizationTrainer(cmd.Cmd):
    intro = "Chess visualization trainer. Choose a game to play! Type help or '?' to see a list of commands.\n"
    prompt = '(chess-trainer)'
    file = None

    def do_colorgame(self, arg):
        '''Displays a random square on the chess board, repeatedly. 'colorgame 10' would play the game for 10 trials. Respond with 'w' for 'white' and 'b' for black. Displays statistics at the end.'''
        args = arg.split()
        kwargs = {}
        if len(args):
             kwargs['rounds'] = int(arg.split()[0])
        ColorGame(**kwargs).cmdloop()
        return False 
    
    def do_brothergame(self, arg):
        '''play "brothers square" chess game.'''
        # change to square and color
        args = arg.split()
        kwargs = {}
        if len(args):
            kwargs['rounds'] = int(arg.split()[0])
        BrotherSquareGame(**kwargs).cmdloop()
        return False

class BadFormatError(Exception):
    '''Raised when an answer to a prompt is poorly formatted.'''
    pass

class RandomSquareGame(cmd.Cmd):
    prompt = '(game)'
    name = None

    def __init__(self, rounds=5):
        super(RandomSquareGame,self).__init__()
        assert rounds > 0, 'Number of rounds must be greater than 0'
        self.rounds = rounds
        self.cur_pos = None
        self.cur_trial_end_time = None
        self.round_results = []
        self.answered = False

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
        self.answered = False
        self._stop_clock()
        return line

    def postcmd(self,stop,line):
        if not stop and self.answered:
            self.cur_pos = get_random_position()
            self._start_clock()
            self.stdout.write("{} ? \n".format(self.cur_pos))
        return stop

    def get_answer(self, line):
        raise NotImplementedError('You must override get_correct_answer')

    def get_correct_answer(self, cur_position):
        raise NotImplementedError('You must override get_correct_answer')

    def onecmd(self, line):
        if line is None:
            return self.emptyline()
        try:
            answer = self.get_answer(line)
        except BadFormatError as e:
            self.stdout.write(e.args[0])
            self.answered = False
            stop = False
            return stop 
        self.answered = True
        right_answer = self.get_correct_answer(self.cur_pos)
        if answer == right_answer:
            self.stdout.write("Correct!\n")
            correct = True
        else:
            self.stdout.write("Incorrect! Answer was {}\n".format(right_answer))

            correct = False
        round_number = len(self.round_results) + 1
        self.round_results.append(Round(
            number=round_number,
            correct=int(correct),
            total_time=self.get_trial_time(), 
            position=self.cur_pos, 
            answer=answer, 
            utc_datetime=str(datetime.now())
            ))
        if round_number >= self.rounds:
            stop = True
        else:
            stop = False
        return stop

    def compute_statistics(self,results):
        correct = 0.0
        incorrect = 0.0
        total_time = 0.0
        for trial in results:
            correct +=int(trial.correct)
            incorrect +=int(not int(trial.correct))
            total_time += float(trial.total_time)
        avg_time = round(total_time/len(results), 2)
        perc_correct = round(correct/len(results), 3)
        statistic = {'num_correct': correct, 'num_results': len(results),
                'perc_correct': perc_correct, 'avg_time': avg_time}
        return statistic

    def print_statistics(self,statistic):
        self.stdout.write("Number Correct: {} out of {}\n".format(int(statistic['num_correct']), statistic['num_results']))
        self.stdout.write("Percent Correct: {}\n".format(statistic['perc_correct']))
        self.stdout.write("Average time per answer in seconds: {}\n".format(statistic['avg_time']))

    def log_trials(self, results):
        filename = self.prompt.replace("(","").replace(")", "") + '.csv'
        file_exists = os.path.exists(filename)
        if not file_exists:
            mode = 'w+'
        else:
            mode = 'a'
        with open(filename, mode=mode)  as f:
            writer = csv.DictWriter(f,fieldnames=Round._fields)
            if not file_exists:
                writer.writeheader()
            writer.writerows(x._asdict() for x in results)

    def read_trials(self):
        filename = self.prompt.replace("(","").replace(")", "") + '.csv'
        with open(filename, mode='r')  as f:
            reader = csv.reader(f)
            header = reader.__next__()
            for row in reader:
                yield Round(*row)

    def postloop(self):
        self.log_trials(self.round_results)
        this_session = self.compute_statistics(self.round_results)
        self.stdout.write("\nSession Finished! Stats for this session:\n")
        self.print_statistics(this_session)
        all_time_rounds = tuple(self.read_trials())
        self.stdout.write("\nAll-time stats:\n")
        all_time_stats = self.compute_statistics(all_time_rounds)
        self.print_statistics(all_time_stats)

        
class ColorGame(RandomSquareGame):
    intro="Enter the color ('w' or 'b') of the random position generated"
    prompt='(color-square)'
    
    def get_answer(self, line):
        if not color_regex.match(line):
            raise BadFormatError('Answer must match {}\n'.format(clor_regex))
        return line

    def get_correct_answer(self, cur_position):
        return get_color(cur_position)


class BrotherSquareGame(RandomSquareGame):
    intro="Enter the square (.e.g a1) and then the color ('w' or 'b') seperated \
            by a space of the brother square generated."
    
    prompt='(brother-square)'
    
    def get_answer(self, line):
        args = line.split()
        if len(args) != 2:
            RaiseBadFormatError('Answer must come in the form of "<square> <color>"\n')
        square, color = args
        if not move_regex.match(square):
            raise BadFormatError('Square must match {}. You gave {}\n'.format(mv_regex, square))
        if not color_regex.match(color):
            raise BadFormatError('Color must match {}. You gave {}\n'.format(clor_regex, color))
        return square, color

    def get_correct_answer(self, cur_position):
        brother_square = get_brother_square(cur_position)
        brother_color = get_color(brother_square)
        return brother_square, brother_color

if __name__ == "__main__":
    ChessVisualizationTrainer().cmdloop()
