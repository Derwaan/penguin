
from agent import Agent
import minimax

"""
Agent skeleton. Fill in the gaps.
"""


class MyAgent(Agent):

    """This is the skeleton of an agent to play the Penguin game."""

    def get_action(self, state, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        return minimax.search(state, self)

    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s;
        """
        for action in state.get_current_player_actions():
            copied_state = state.copy()
            copied_state.apply_action(action)
            yield (action, copied_state)

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        return depth >= 2 or state.game_over()

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
        return 'Eggsy'
