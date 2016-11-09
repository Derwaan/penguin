
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
        for action in state.get_actions(self.id):
            yield action

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        return depth > 2 or state.game_over()

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        scores = state.get_scores();
        me = state.cur_player
        other = me + 1 % 2

        if(scores[me] > scores[other]):
            return 1
        elif(scores[me] < scores[other]):
            return -1;
        return 0;

    def get_name(self):
        return 'Herbert'
