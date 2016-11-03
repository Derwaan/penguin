import random
from agent import Agent

class MyAgent(Agent):

  def get_action(self, state, time_left):
    actions = state.get_current_player_actions()
    action = random.choice(actions)
    return action