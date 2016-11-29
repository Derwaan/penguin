
from agent import Agent
import minimax
import penguin

"""
Agent skeleton. Fill in the gaps.
"""

class Queue:
    """Queue is an abstract class/interface. There are three types:
        Stack(): A Last In First Out Queue.
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(lt): Queue where items are sorted by lt, (default <).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())
    Note that isinstance(Stack(), Queue) is false, because we implement stacks
    as lists.  If Python ever gets interfaces, Queue will be an interface."""

    def __init__(self): 
        abstract

    def extend(self, items):
        for item in items: self.append(item)

class FIFOQueue(Queue):
    """A First-In-First-Out Queue."""
    def __init__(self):
        self.A = []; self.start = 0
    def append(self, item):
        self.A.append(item)
    def __len__(self):
        return len(self.A) - self.start
    def extend(self, items):
        self.A.extend(items)     
    def pop(self):        
        e = self.A[self.start]
        self.start += 1
        if self.start > 5 and self.start > len(self.A)/2:
            self.A = self.A[self.start:]
            self.start = 0
        return e

class MyAgent(Agent):

    """This is the skeleton of an agent to play the Penguin game."""
    def __init__(self):
        super().__init__()
        self.previous_time = 0
        self.depth = 1
        self.factor = 20;

    def get_action(self, state, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        if(state.placement_phase):
            return minimax.search(state, self)
        time_taken = 0
        if(self.previous_time > 0):
            time_taken = self.previous_time - time_left
        self.previous_time = time_left
        if(self.factor * time_taken * time_taken < time_left):
            self.depth += 1
        elif(self.factor * time_taken > time_left):
            self.depth -= 1
        return minimax.search(state, self)


    def bfs(self, state, initial):
        closed = {}
        fringe = FIFOQueue()

        list_penguins = [initial]
        return_val = False

        fringe.append(initial)
        while fringe:
            pos = fringe.pop()
            if pos not in closed:
                closed[pos] = True
                if pos[0] >= 0 and pos[0] < len(state.penguins):
                    if pos[1] >= 0 and pos[1] < len(state.penguins[pos[0]]):
                        if state.fish[pos[0]][pos[1]] != 0: # Not in water
                            for dir in penguin.dir[pos[0] % 2]:
                                fringe.append((pos[0] + dir[0], pos[1] + dir[1])) # We add the neighbour
                        if state.penguins[pos[0]][pos[1]] != self.id and state.penguins[pos[0]][pos[1]] != -1:
                            return_val = True
                        elif state.penguins[pos[0]][pos[1]] == self.id:
                            list_penguins.append((pos[0], pos[1]))

        return return_val, list_penguins


    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s;
        """
        closed = {}
        must_not_move = {}

        for i in range(0, len(state.penguins)):
            for j in range(0, len(state.penguins[i])):
                if state.penguins[i][j] == self.id and (i,j) not in closed:
                    other_penguins, list_penguins = self.bfs(state, (i, j))
                    for pos in list_penguins:
                        closed[pos] = True
                        if not other_penguins:
                            must_not_move[pos] = True


        for action in state.get_current_player_actions():
            copied_state = state.copy()
            copied_state.apply_action(action)

            list = []
            done = False

            if action[1] not in must_not_move or action[0] != 'move':
                done = True
                yield (action, copied_state)
            else:
                list.append((action, copied_state))

            if(not done):
                print('All')
                return list

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        return depth >= self.depth or state.game_over()

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        if state.placement_phase:
            sum = 0
            for i in range(0, len(state.penguins)):
                for j in range(0, len(state.penguins[i])):
                    if state.penguins[i][j] == self.id:
                        for move in state.get_moves(i, j):
                            if state.penguins[move[0]][move[1]] == -1:
                                sum += state.fish[move[0]][move[1]]
            return sum

        scores = state.get_scores()
        other = (self.id + 1) % 2
        return scores[self.id] - scores[other]

    def get_name(self):
        return 'Smith'
