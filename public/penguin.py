from state import State
from ascii_hex import Hex
import random

"""
Useful variables
"""
# direction for even rows
dir_even = [ (-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1), (0, -1) ]
# directions for odd rows
dir_odd = [ (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (0, -1) ]
# directions
dir = [dir_even, dir_odd]

# state of the Penguin game
class PenguinState(State):

    """
    Create a state. The arguments are the following:

    -fish: 
    a matrix such that fish[i][j] = number of fish at position (i, j) or 0 if 
    position (i, j) is water
    
    -penguins: 
    a matrix such that penguins[i][j] = id of the player that has a penguin
    at position (i, j) or -1 is there is no penguin at position (i, j)

    -scores:
    an array such that scores[i] = score of player i

    -nb_tiles:
    an array such that nb_tiles[i] = number of tiles that player i captured

    -placement_phase: 
    boolean that is true if and only if the game is in the placement phase

    -nb_players:
    the number of players in the game

    -cur_player:
    the index of the current player

    -nb_penguins_player:
    number of penguins per player
    """
    def __init__(self, fish, penguins, scores, nb_tiles, placement_phase, nb_players, cur_player, nb_penguins_player):
        # set the number of rows
        self.nb_rows = len(fish)
        # set the first row size
        self.fst_row_size = len(fish[0])
        # set the fish matrix
        self.fish = fish
        # set the penguin matrix
        self.penguins = penguins
        # set scores
        self.scores = scores
        # set number of tiles captured
        self.nb_tiles = nb_tiles
        # set placement phase
        self.placement_phase = placement_phase
        # set number of players
        self.nb_players = nb_players
        # set current player
        self.cur_player = cur_player
        # set number of penguins per player
        self.nb_penguins_player = nb_penguins_player
        # build penguin position by player
        # penguin_positions[i] = set with the positions of the penguins of player i
        self.penguin_positions = [ set() for i in range(nb_players) ]
        for i in range(len(self.penguins)):
            for j in range(len(self.penguins[i])):
                if self.penguins[i][j] != -1:
                    self.penguin_positions[self.penguins[i][j]].add((i, j))
    
    #################
    # STATE METHODS #
    #################
    """
    Return true if and only if the game is over.
    """
    def game_over(self):
        for i in range(self.nb_players):
            actions = self.get_actions(i)
            if len(self.get_actions(i)) > 0:
                return False
        return True

    """
    Get the current player.
    """
    def get_cur_player(self):
        return self.cur_player

    """
    Checks if a given action is valid.
    """
    def is_action_valid(self, action):
        actions = self.get_current_player_actions()
        return action in actions

    """
    Applies a given action to this state. It assume that the actions is
    valid. This must be checked with is_action_valid.
    """
    def apply_action(self, action):
        if action[0] == 'place':
            # placement action
            pos = action[1]
            # update penguins matrix
            self.penguins[pos[0]][pos[1]] = self.cur_player
            # update penguin positions
            self.penguin_positions[self.cur_player].add(pos)
        else:
            # movement action
            origin = action[1]
            destination = action[2]
            # update penguins matrix
            self.penguins[origin[0]][origin[1]] = -1
            self.penguins[destination[0]][destination[1]] = self.cur_player
            # update pengun positions
            self.penguin_positions[self.cur_player].remove(origin)
            self.penguin_positions[self.cur_player].add(destination)
            # update socres
            self.scores[self.cur_player] += self.fish[origin[0]][origin[1]]
            self.nb_tiles[self.cur_player] += 1
            # update fish matrix
            self.fish[origin[0]][origin[1]] = 0
        # update current player
        self.cur_player = self.next_player()
        # check if we need to change phases
        if self.placement_phase:
            change_phase = True
            for p in range(self.nb_players):
                if len(self.penguin_positions[p]) < self.nb_penguins_player:
                    change_phase = False
                    break
            if change_phase:
                # every player has places all of its penguins
                # placement phase is over
                self.placement_phase = False

    """
    Return scores of the penguins, counting the fish on top of which the penguins are located.
    """
    def get_scores(self):
        ret = [self.scores[i] for i in range(self.nb_players)]
        for i in range(self.nb_players):
            for p in self.penguin_positions[i]:
                ret[i] += self.fish[p[0]][p[1]]
        return ret

    """
    Get the winner of the game. Call only if the game is over.
    Return the id of the winning player. In case of ties return -1.
    """
    def get_winner(self):
        sc = self.get_scores()
        results = [ (sc[i], self.nb_tiles) for i in range(self.nb_players) ]
        m = results[0]
        for i in range(self.nb_players):
            if results[i] > m:
                m = results[i]
        winners = [ ]
        for i in range(self.nb_players):
            if results[i] == m:
                winners.append(i)
        if len(winners) == 1:
            return winners[0]
        return -1

    """
    Return the state data. This is what is given to the students
    so that they implement their own state class.
    """
    def get_state_data(self):
        state_copy = self.copy()
        return (state_copy.fish, state_copy.penguins, state_copy.scores, state_copy.placement_phase, state_copy.cur_player)

    ################################
    # METHODS SPECIFIC TO THE GAME #
    ################################
    """
    Given a position pos, computes the neighbor position 
    on the hexagonal grid.
    """
    def get_neighbor_positions(self, pos):
        neighbor_position = [ ]
        # loop over the direction on the current row
        for d in dir[pos[0] % 2]:
            # create candidate position
            candidate = (d[0] + pos[0], d[1] + pos[1])
            if self.in_bounds(candidate[0], candidate[1]):
                # candidate position is withing bounds so we add it
                neighbor_position.append(candidate)
        return neighbor_position
    
    """
    Compute the size of a given rows
    """
    def row_size(self, i):
        return len(self.fish[i])

    """
    Compute all possible actions that the current player can perform
    on this state.
    """
    def get_current_player_actions(self):
        return self.get_actions(self.cur_player)

    """
    Compute all possible actions that player can perform
    on this state.
    """
    def get_actions(self, player):
        actions = [ ]
        # check whether we are in the placement phase
        if self.placement_phase:
            for i in range(self.nb_rows):
                for j in range(self.row_size(i)):
                    if self.penguins[i][j] == -1 and self.fish[i][j] == 1:
                        # no penguin at position (i, j)
                        actions.append(('place', (i, j)))
        else:
            # movement phase, compute all penguin movements
            for (i, j) in self.penguin_positions[player]:
                        # player owns penguin at position (i, j)
                        # compute the possible moves
                        for destination in self.get_moves(i, j):
                            actions.append(('move', (i, j), destination))
        return actions

    """
    Get all the moves that a penguin at position (i, j) would be able to do.
    """
    def get_moves(self, i, j):
        moves = set()
        for d in range(6):
            if i % 2 == 0:
                self.build_moves(d, i + dir_even[d][0], j + dir_even[d][1], moves)
            else:
                self.build_moves(d, i + dir_odd[d][0], j + dir_odd[d][1], moves)
        return moves

    """
    Auxiliary method to build the moves array in a given direction.
    """
    def build_moves(self, d, i, j, moves):
        if self.in_bounds(i, j) and self.fish[i][j] > 0 and self.penguins[i][j] == -1:
            moves.add((i, j))
            if i % 2 == 0:
                self.build_moves(d, i + dir_even[d][0], j + dir_even[d][1], moves)
            else:
                self.build_moves(d, i + dir_odd[d][0], j + dir_odd[d][1], moves)

    """
    Check if a position is withing the bounds of the board.
    """
    def in_bounds(self, i, j):
        return 0 <= i and i < self.nb_rows and 0 <= j and j < self.row_size(i)

    """
    Create a copy of this state.
    """
    def copy(self):
        # copy the fish matrix
        fish = [ [ self.fish[i][j] for j in range(len(self.fish[i])) ] for i in range(len(self.fish)) ]
        # copy the penguin matrix
        penguins = [ [ self.penguins[i][j] for j in range(len(self.penguins[i])) ] for i in range(len(self.penguins)) ]
        # copy the socres array
        scores = [ self.scores[i] for i in range(len(self.scores)) ]
        # copy the tiles array
        nb_tiles = [ self.nb_tiles[i] for i in range(len(self.nb_tiles)) ]
        # create new copy of this state
        return PenguinState(fish, penguins, scores, nb_tiles, self.placement_phase, self.nb_players, self.cur_player, self.nb_penguins_player)

    
    """
    Return the next player to play or -1 is no players have actions.
    """
    def next_player(self):
        if not self.game_over():
            next = (self.cur_player + 1) % self.nb_players
            if not self.placement_phase:
                while len(self.get_actions(next)) == 0:
                    next = (next + 1) % self.nb_players
            return next
        return -1

    """
    Set the score of a player to a specific value. This can we useful
    to deal with timeouts by putting a very negative score on a player
    who timesout.
    """
    def set_score(self, player_id, score):
        self.scores[player_id] = score

    """
    Build a string representation of the state. Player 0 is represented
    by p:0, player 1 by p:1 and so on.
    """
    def __str__(self):
        hex = Hex(len(self.fish), len(self.fish[0]))
        for i in range(len(self.fish)):
            for j in range(len(self.fish[i])):
                if self.fish[i][j] > 0:
                    hex.draw_hexagon(j, i)
                    s = '  ' + str(self.fish[i][j]) + '  '
                    if self.penguins[i][j] == -1:
                        s += '     '
                    else:
                        s += ' p:' + str(self.penguins[i][j]) + ' '
                    hex.draw_str(j, i, s)
        s = 'current player: ' + str(self.cur_player) + '\n'
        s += 'placement phase? ' + str(self.placement_phase) + '\n'
        s += str(hex)
        return s

"""
Generate the initial state.
"""
def generate_initial_state(nb_rows, fst_row_size, nb_players, nb_penguins_player):
    # compute the number of cells on the board
    size = fst_row_size * (nb_rows // 2 + nb_rows % 2) + (fst_row_size - 1 ) * nb_rows // 2
    # initialze the fish values
    f = [ 0 for i in range(size) ]
    # compute number of ones
    ones = size // 2
    # compute number of twos
    twos = size // 3
    # compute number of threes
    three = size - ones - twos
    # set the ones, twos and threes on f
    for i in range(0, ones):
        f[i] = 1
    for i in range(ones, ones + twos):
        f[i] = 2
    for i in range(ones + twos, ones + twos + three):
        f[i] = 3
    # shuffle f to randomize
    random.shuffle(f)
    k = 0
    # set the values of f into the fish matrix
    fish = [ [ 0 for j in range(fst_row_size - i % 2) ] for i in range(nb_rows) ]
    for i in range(nb_rows):
        for j in range(fst_row_size - i % 2):
            fish[i][j] = f[k]
            k += 1
    # generate penguin matrix
    penguin = [ [ -1 for j in range(fst_row_size - i % 2) ] for i in range(nb_rows) ]
    # initialize scores
    scores = [ 0 for i in range(nb_players) ]
    # initialize number of tiles
    nb_tiles = [ 0 for i in range(nb_players) ]
    return PenguinState(fish, penguin, scores, nb_tiles, True, nb_players, 0, nb_penguins_player)
