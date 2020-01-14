#!/usr/bin/env python3
import cmd
import re
import csv
import os
import sys
from queue import PriorityQueue as _PriorityQueue
from collections import namedtuple, defaultdict
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
    '''A single square on a chess board.'''
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.distance = float("inf")
        # length of route
        self.route =  []
        # i.e. ["a:1","b:2"...]
        self.name = get_chess_notation(x, y) 
        # i.e. "a:1"

    def __eq__(self, other):
        return other.name == self.name
    
    @classmethod
    def from_chess_name(cls, name):
        return Node(*get_num_notation(name))

def generate_graph():
    '''Generates all the nodes on a chess board.'''
    for x in range(1,9):
        for y in range(1,9):
            yield Node(x,y)

def generate_knight_neighbors(x,y):
    directions = ((1, 2),(-1, 2),(2, 1),(-2, 1),
             (1, -2),(-1, -2),(2, -1),(-2, -1))
    for direction in directions:
        square = x+direction[0], y+direction[1]
        if square_exists(*square):
            yield get_chess_notation(*square)

class PriorityQueue(_PriorityQueue):
    '''queue.PriorityQueue with a 'contains' method'''

    def _find(self, item):
        index = None
        for _index, _item_tuple in enumerate(self.queue):
            old_priority, _item = _item_tuple
            if _item == item:
                index = _index
                break
        return index

    def __contains__(self, item):
        index = self._find(item) 
        return index is not None 

class KeyBasedDefaultDict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = self.default_factory(key)
        return self[key]

def find_shortest_path_for_knight(start_position,end_position):
    '''Finds *one* of the many shortest paths from start_position to end_position
    for a knight.
    :param str start_position: The starting position on a chess board, i.e. "a:1"
    :param str end_position: The end positiion on a chess board, i.e. "h:8"
    Returns a route from start_position -> end_position that is one of the shortest
    (never gauranteed to be the only path)
    '''
    queue = PriorityQueue() # distance to node, with the name, i.e. "a:1"
    nodes = KeyBasedDefaultDict(Node.from_chess_name) # 'a:1' -> Node(1,1)
    edge_length = 1 # 1 move
    start_node = nodes[start_position] 
    start_node.distance = 0
    start_node.route = [start_node.name]
    queue.put((start_node.distance, start_node.name))
    
    # A version of djikstra's algorithm
    while not queue.empty():
        _, cur = queue.get()
        current = nodes[cur]
        tentative_distance = current.distance + edge_length
        for n in generate_knight_neighbors(current.x, current.y):
            neighbor = nodes[n]
            if tentative_distance < neighbor.distance:
                if neighbor.name not in queue:
                    neighbor.distance = tentative_distance
                    neighbor.route = current.route + [neighbor.name]
                    queue.put((neighbor.distance, neighbor.name))
    
    return nodes[end_position].route

def is_a_shortest_path_for_knight(path, a_shortest_path):
    '''
    :param list(str) path: A list of chess squares along a chess board, i.e. 
        ['a:1', 'b:3', ...]
    :param list(str) a_shortest_path: A shortest path for a knight between two
        squares on a chess board. Same format as `path`
    Returns a boolean if `path` is a shortest path.
    '''

    if path == a_shortest_path:
        return True
    if len(path) != len(a_shortest_path):
        return False
    # the lengths are the same, so now we must
    # transverse their path and see if it exists
    cur = path[0]
    path_exists = True
    for next_square in path[1:]:
        x,y = get_num_notation(cur)
        neighbors = tuple(generate_knight_neighbors(x,y))
        if next_square not in neighbors:
            path_exists = False
            break
        cur = next_square
    return path_exists

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

def get_num_notation(position):
    '''"a:1" -> (1,1)'''
    letter,number = position.split(':')
    return chess_notation_backwards [letter], int(number)

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
        games = ColorGame(),BrotherSquareGame(), DiagonalSquareGame(),KnightSquareGame() 
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

    def do_knightgame(self, arg):
        '''play "knight game", where you find the shortest path
        between two squares for a knight.'''
        args = arg.split()
        kwargs = {}
        if len(args):
            kwargs['rounds'] = int(arg.split()[0])
        KnightSquareGame(**kwargs).cmdloop()
        return False


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

    def get_random_position(self):
        '''Grabs a random initial position from the board.'''
        return get_random_position()

    def preloop(self):
        self.cur_pos = self.get_random_position()
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
            self.cur_pos = self.get_random_position()
            self._start_clock()
            self.stdout.write("{} ? \n".format(self.cur_pos))
        return stop

    def get_answer(self, line):
        raise NotImplementedError('You must override get_correct_answer')

    def get_correct_answer(self, cur_position):
        raise NotImplementedError('You must override get_correct_answer')

    def is_right_answer(self, answer, right_answer):
        return answer == right_answer

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
        if self.is_right_answer(answer, right_answer):
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

class KnightSquareGame(RandomSquareGame):
    intro="given a start and end position for a knight, give *one of* the shortest routes."
    
    prompt='(knight)'

    def get_random_position(self):
        start = get_random_position(xmin=1,xmax=8,ymin=1,ymax=1)
        end = get_random_position(xmin=1,xmax=8,ymin=8,ymax=8)
        return "{} {}".format(start, end)

    def get_answer(self, line):
        args = line.split()
        if len(args) < 2:
            raise BadFormatError('Answer must come in the form of "<square> <square> ... <square>"\n')
        
        for square in args:
            if not move_regex.match(square):
                raise BadFormatError('Square must match {}. You gave {}\n'.format(mv_regex, square))
        return args 

    def get_correct_answer(self, cur_position):
        start, end = cur_position.split()
        answer = find_shortest_path_for_knight(start, end)
        return answer 

    def is_right_answer(self, answer, right_answer):
        return is_a_shortest_path_for_knight(answer, right_answer)

if __name__ == "__main__":
    try:
        ChessVisualizationTrainer().cmdloop()
    except KeyboardInterrupt:
        print('')
        print('Thanks for playing!')
        sys.exit(0)

