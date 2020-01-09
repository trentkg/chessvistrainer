#!/usr/bin/env python3
import cmd
import re
import csv
import os
import sys
from collections import namedtuple
from queue import PriorityQueue
from random import randint
from datetime import datetime

mv_regex = "[a|b|c|d|e|f|g|h]:[1-8]"
move_regex = re.compile(mv_regex)
clor_regex = 'w|b'
color_regex = re.compile(clor_regex)

chess_notation = {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}
chess_notation_backwards = {value:key for key,value in chess_notation.items()}

def get_random_position(xmin=1,xmax=8,ymin=1,ymax=8):
    '''Returns a random position on a chessboard as a string, i.e. "a:1".
    Use the parameters to constrain the random position to a certain part of the board,
    i.e. xmin=1, xmax=1 would contrain the random position to just the a file.
    :param int xmin: The minimum board position that the x-axis can be (defaults to 1) 
    :param int xmax: The maximum board position that the x-axis can be (defaults to 8)
    :param int ymin: The minimum board position that the y-axis can be (defaults to 1)
    :param int ymax: The maximum board position that the x-axis can be (defaults to 8)
    '''
    assert 1<=xmin and xmin<=8
    assert 1<=xmax and xmax<=8
    assert 1<=ymin and ymin<=8
    assert 1<=ymax and ymax<=8

    letter = randint(xmin,xmax)
    number = randint(ymin,ymax)
    return get_chess_notation(letter, number)

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.distance = None 
        # length of route
        self.route = None  
        # i.e. "a:1","b:2"...
        self.name = get_chess_notation(x, y) 
        # i.e. "a:1"

def generate_knight_neighbors(x,y):
    directions = ((1, 2),(-1, 2),(2, 1),(-2, 1),
             (1, -2),(-1, -2),(2, -1),(-2, -1))
    for direction in directions:
        square = x+direction[0], y+direction[1]
        if square_exists(*square):
            yield square

def generate_graph():
    for x in range(1,9):
        for y in range(1,9):
            yield Node(x,y) 

def find_shortest_path_for_knight(start_position,end_position):
    nodes = {} # name -> node
    unvisited = PriorityQueue() # contains only the node names
    visited = set() 
    edge_length = 1 # 1 move
    
    for node in generate_graph():
        if node.name == start_position:
            node.distance = 0
            node.route = [node.name]
        else:
            node.distance = float('inf')
        nodes[node.name] = node
        unvisited.put((node.distance, node.name))

    # Djikstra's algorithm
    while not unvisited.empty():
        _, current_name = unvisited.get()
        current = nodes[current_name]
        if current.distance == float('inf') or end_position in visited:
            # This node doesnt connect, (distance = inf)
            # or we've visited the end position.We're done.
            break
        
        for neighbor_square in generate_knight_neighbors(current.x, current.y):
            neighbor_name = get_chess_notation(*neighbor_square)
            if neighbor_name not in visited:
                tentative_distance = current.distance + edge_length # add a move
                this_node = nodes[neighbor_name]
                if tentative_distance < this_node.distance:
                    this_node.distance = tentative_distance
                    this_node.route = current.route + [this_node.name]
        visited.add(current.name)
    
    if end_position not in visited:
        # Should never happen
        import pdb;pdb.set_trace()
        raise Exception("No route from {} to {} for a knight".format(start_position, end_position))
    
    return nodes[end_position]

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
    return get_chess_notation(xbro, ybro)

def get_chess_notation(x, y):
    '''i.e. x=1, y=1 would return "a:1"'''
    return "{}:{}".format(chess_notation[x], str(y))

def square_exists(x,y):
    result = (1<=x<=8) and (1<=y<=8)
    return result

def _walk_path(x,y,xi,yi):
    curx, cury = x+xi,y+yi
    while square_exists(curx,cury):
        yield curx,cury
        curx+=xi
        cury+=yi
    
def _get_diagonal_squares(x,y):
    diagonals = ((1,1), (-1,1), (1,-1),(-1,-1))
    for direction in diagonals:
        for square in _walk_path(x,y,*direction):
            yield square

def _to_strings(chesspath):
    for x,y in chesspath:
        yield "{}:{}".format(chess_notation[x],y)

def get_diagonal_squares(position):
    letter, number = position.split(":")
    y_num = int(number)
    x_num = chess_notation_backwards[letter]
    diagonals = _get_diagonal_squares(x_num,y_num) 
    as_strings = _to_strings(diagonals)
    return sorted(as_strings)

Round = namedtuple("Round", ['number', 'correct', 'total_time', 'position', 'answer', 'utc_datetime'])

class ChessVisualizationTrainer(cmd.Cmd):
    intro = "Chess visualization trainer. Choose a game to play! Type help or '?' to see a list of commands. 'Ctrl+c' to quit\n"
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
    
    def do_diagonal(self, arg):
        '''play "diagonal" chess game.'''
        # change to square and color
        args = arg.split()
        kwargs = {}
        if len(args):
            kwargs['rounds'] = int(arg.split()[0])
        DiagonalSquareGame(**kwargs).cmdloop()
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
    
    def do_getstats(self, arg):
        '''Grabs the statistics for all games. Enter a name
        as a second parameter to print a specific games statitstics.'''
        games = ColorGame(),BrotherSquareGame(), DiagonalSquareGame()
        game_name = arg
        options = [x.name for x in games]
        if game_name and game_name not in options:
            self.stdout.write('\nGame "{}" does not exist. Options are: {}\n'.format(game_name, ", ".join(options)))
        for game in games:
            if game_name and game_name != game.name:
                continue
            else:
                all_time_rounds = tuple(game.read_trials())
                self.stdout.write("\nAll-time stats for {}:\n".format(game.name))
                all_time_stats = game.compute_statistics(all_time_rounds)
                game.print_statistics(all_time_stats)

class BadFormatError(Exception):
    '''Raised when an answer to a prompt is poorly formatted.'''
    pass

class RandomSquareGame(cmd.Cmd):
    prompt = '(game)'

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

    @property
    def name(self):
        return self.prompt.replace("(","").replace(")", "")

    @property
    def filename(self):
        return self.name + '.csv'

    def log_trials(self, results):
        file_exists = os.path.exists(self.filename)
        if not file_exists:
            mode = 'w+'
        else:
            mode = 'a'
        with open(self.filename, mode=mode)  as f:
            writer = csv.DictWriter(f,fieldnames=Round._fields)
            if not file_exists:
                writer.writeheader()
            writer.writerows(x._asdict() for x in results)

    def read_trials(self):
        with open(self.filename, mode='r')  as f:
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
            raise BadFormatError('Answer must come in the form of "<square> <color>"\n')
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

class DiagonalSquareGame(RandomSquareGame):
    intro="enter all the diagonals of the random square, followed"+ \
    " by a color"
    
    prompt='(diag)'
    
    def get_answer(self, line):
        args = line.split()
        guess = 4
        if len(args) <= guess:
            raise BadFormatError('Answer must come in the form of "<square> <square> ... <color>"\n')
        
        squares = args[:-1]
        color  = args[-1]
        for square in squares:
            if not move_regex.match(square):
                raise BadFormatError('Square must match {}. You gave {}\n'.format(mv_regex, square))
        if not color_regex.match(color):
            raise BadFormatError('Color must match {}. You gave {}\n'.format(clor_regex, color))
        return sorted(squares) + [color]

    def get_correct_answer(self, cur_position):
        diagonal_squares = get_diagonal_squares(cur_position)
        color = get_color(cur_position)
        answer = diagonal_squares + [color]
        return answer 

if __name__ == "__main__":
    try:
        ChessVisualizationTrainer().cmdloop()
    except KeyboardInterrupt:
        print('')
        print('Thanks for playing!')
        sys.exit(0)

