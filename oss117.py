
from agent import Agent
import minimax

"""
Agent skeleton. Fill in the gaps.
"""


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
                        for k in range(0, len(state.fish[i])):
                            sum += state.fish[i][k]
            return sum

        scores = state.get_scores()
        other = (self.id + 1) % 2
        return scores[self.id] - scores[other]

    def get_name(self):
        return 'OSS 117'
