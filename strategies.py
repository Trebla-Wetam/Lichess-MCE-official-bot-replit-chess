"""
Some example strategies for people who want to create a custom, homemade bot.
And some handy classes to extend
"""
import sys
import chess
from chess.engine import PlayResult
import random
from engine_wrapper import EngineWrapper


class FillerEngine:
    """
    Not meant to be an actual engine.
    This is only used to provide the property "self.engine"
    in "MinimalEngine" which extends "EngineWrapper"
    """
    def __init__(self, main_engine, name=None):
        self.id = {
            "name": name
        }
        self.name = name
        self.main_engine = main_engine

    def __getattr__(self, method_name):
        main_engine = self.main_engine

        def method(*args, **kwargs):
            nonlocal main_engine
            nonlocal method_name
            return main_engine.notify(method_name, *args, **kwargs)

        return method


class MinimalEngine(EngineWrapper):
    """
    Subclass this to prevent a few random errors
    Even though MinimalEngine extends EngineWrapper,
    you don't have to actually wrap an engine.
    At minimum, just implement `search`,
    however you can also change other methods like
    `notify`, `first_search`, `get_time_control`, etc.
    """
    def __init__(self, *args, name=None):
        super().__init__(*args)

        self.engine_name = "MCE"

        self.last_move_info = []
        self.engine = FillerEngine(self, name=self.name)
        self.engine.id = {
            "name": self.engine_name
        }

    def search_with_ponder(self, board, wtime, btime, winc, binc, ponder, draw_offered):
        timeleft = 0
        if board.turn:
            timeleft = wtime
        else:
            timeleft = btime
        return self.search(board, timeleft, ponder, draw_offered)

    def search(self, board, timeleft, ponder, draw_offered):
        a=MCE(board, timeleft, draw_offered, ponder, 3).get()
        sys.stderr.write(str(a)+"\n")
        return PlayResult(a[2], None)

    def notify(self, method_name, *args, **kwargs):
        """
        The EngineWrapper class sometimes calls methods on "self.engine".
        "self.engine" is a filler property that notifies <self> 
        whenever an attribute is called.
        Nothing happens unless the main engine does something.
        Simply put, the following code is equivalent
        self.engine.<method_name>(<*args>, <**kwargs>)
        self.notify(<method_name>, <*args>, <**kwargs>)
        """
        pass



class MCE:
        def __init__(self, board, timeleft, draw_offered, ponder, depth=3, mode="careless"):
            if mode!="careless":
                if int(timeleft.time)<(90-board.fullmove_number)*30:
                    if int(timeleft.time)<30: depth=2
                    else: depth=int(depth/2)+1
            self.draw_offered,self.board=draw_offered,board
            self.depth=self.DEPTH=depth
        def get(self, move=None): return (self.score()+(len(tuple(self.board.legal_moves))/100 if self.board.turn else -len(tuple(self.board.legal_moves))/100),chess.Move.from_uci(move)) if self.depth==0 or self.board.is_checkmate() or self.board.is_variant_draw() else self.getbest(set(map(self.get_score,self.board.generate_legal_moves())))
        def get_score(self, move):
            m=str(move)
            self.board.push(chess.Move.from_uci(m))
            self.depth-=1
            a=self.get(m)[0]
            self.depth+=1
            if self.depth==self.DEPTH:
                a+=self.score()/100
                self.board.pop()
                return (a,m,move)
            self.board.pop()
            return (a,m)
        def score(self):
            values={"p":-100,"n":-290,"b":-305,"r":-490,"q":-895,"k":0,"P":100,"N":290,"B":305,"R":490,"Q":895,"K":0,"/":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0}
            if self.board.is_checkmate():
                return -1000000 if self.board.turn else 1000000
            elif self.board.is_variant_draw():
                return -190 if self.board.turn else 190
            k=0
            for i in self.board.fen().split(" ")[0]:
                k+=values[i]
            return k
        def getbest(self, mapped):
            func = max if self.board.turn else min
            a=func(set(mapped))
            return a


class ExampleEngine(MinimalEngine):
    pass


# Strategy names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    def search(self, board, *args):
        return PlayResult(random.choice(list(board.legal_moves)), None)


class Alphabetical(ExampleEngine):
    def search(self, board, *args):
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return PlayResult(moves[0], None)


class FirstMove(ExampleEngine):
    """Gets the first move when sorted by uci representation"""
    def search(self, board, *args):
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return PlayResult(moves[0], None)
    