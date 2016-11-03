import math
import pygame
import sys
import os
import random
import argparse
import time
import signal
from pygame.locals import *
from penguin import PenguinState
from penguin import generate_initial_state
from threading import Thread

class Hexagon:

  def __init__(self, x, y, W, H):
    self.W = W
    self.H = H
    self.x = x
    self.y = y
    self.P = [ -1 for i in range(6) ]
    self.P[0] = (x + W / 2, y)
    self.P[1] = (x, y + H / 4)
    self.P[2] = (x, y + 3 * H / 4)
    self.P[3] = (x + W / 2, y + H)
    self.P[4] = (x + W, y + 3 * H / 4)
    self.P[5] = (x + W, y + H / 4)
    self.center = (x + W / 2, y + H / 2)

  def orient(self, p, q, r):
    orient = q[0] * r[1] - r[0] * q[1] - p[0] * (r[1] - q[1]) + p[1] * (r[0] - q[0])
    if orient == 0:
      return 0
    if orient < 0:
      return -1
    return 1

  def contains(self, p):
    orient = self.orient(p, self.P[0], self.P[1])
    for i in range(2, len(self.P)):
      if self.orient(p, self.P[i - 1], self.P[i]) != orient:
        return False
    return True

  def __str__(self):
    return str(self.P)

def getHexagon(p, W, H):
  x = p[1] * W
  if p[0] % 2 == 1:
    x = x + W / 2
  y = p[0] * 3 * H / 4
  return Hexagon(x, y, W, H)

def get_selected_cell(r, c, p, hexagons):
  for i in range(r):
    for j in range(c - i % 2):
      h = hexagons[i][j]
      if h.contains(p):
        return (i, j)
  return None

def get_action_threaded(state, agent, timeleft):
  result = [ None ]
  thread = Thread(target=get_action, args=(state, agent, timeleft, result))
  thread.start()
  return result

def get_action(state, agent, timeleft, result):
  action = agent.get_action(state, timeleft)
  result[0] = action

def draw_screen():
  # clear the screen
  screen.fill((0,0,0))
  # draw the tiles
  for i in range(r):
    for j in range(c - i % 2):
      h = hexagons[i][j]
      screen.blit(tiles[state.fish[i][j]], (h.x, h.y))
      if state.penguins[i][j] != -1:
        screen.blit(penguins[state.penguins[i][j]], (h.x, h.y))
  # draw the moves
  if moves != None:
    for p in moves:
      pygame.draw.lines(screen, (255,255,255), True, hexagons[p[0]][p[1]].P, 2)
  # draw the cell under the mouse
  if over != None:
    pygame.draw.lines(screen, (0,255,0), True, hexagons[over[0]][over[1]].P, 2)
  # check if the game is over to compute final 
  if state.game_over():
    # the game is over, update the scores
    for i in range(r):
      for j in range(c - i % 2):
        if state.penguins[i][j] != -1:
          # add the score of this penguin to its owner score
          value = state.fish[i][j]
          label = end_points_font.render('+' + str(value), 1, (0,0,0))
          screen.blit(label, (hexagons[i][j].center[0] - 20, hexagons[i][j].center[1] - 20))
          state.scores[state.penguins[i][j]] += value
  # render scores
  screen.blit(score_lbl, (grid_size[0] + 10, 10))
  dy = 50
  for p in range(pl):
    screen.blit(penguins[p], (grid_size[0] + 10, score_lbl.get_rect().height + dy))
    if p == state.cur_player:
      screen.blit(selected_aura, (grid_size[0] + 10, score_lbl.get_rect().height + dy))
    label = score_points_font.render('fish: ' + str(state.scores[p]) + ' (' + str(state.nb_tiles[p]) + ')', 1, (255,255,255))
    screen.blit(label, (grid_size[0] + 20, dy))
    dy += penguins[p].get_rect().height
    if player_type[p] != 'human':
      minutes = str(math.ceil(time_left[p]) // 60)
      seconds = str(math.ceil(time_left[p]) % 60)
      time_str = ''
      if len(minutes) < 2:
        minutes = '0' + minutes
      if len(seconds) < 2:
        seconds = '0' + seconds
      time_str = minutes + ':' + seconds
      if time_left[p] == 0:
        label = score_points_font.render(time_str, 1, (255, 0, 0))
        screen.blit(label, (grid_size[0] + W + 10, 10 + dy - 3 * H // 4))
        label = score_points_font.render('timeout', 1, (255, 0, 0))
        screen.blit(label, (grid_size[0] + W + 10, 10 + dy - 3 * H // 4 + 30))
      else:
        label = score_points_font.render(time_str, 1, (255, 255, 255)) 
        screen.blit(label, (grid_size[0] + W + 10, 10 + dy - 3 * H // 4))
         
  # update the gui  
  pygame.display.update()

if __name__ == "__main__":
  # process the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-q', help='exit at the end', action='store_true')
  parser.add_argument('-t', help='total number of seconds credited to each player')
  parser.add_argument('-r', help='number of rows')
  parser.add_argument('-c', help='number of columns (on the first row)')
  #parser.add_argument('-pl', help='number of players')
  parser.add_argument('-pe', help='number of penguins per player')
  parser.add_argument('-ai0', help='path to the ai that will play as player 0')
  parser.add_argument('-ai1', help='path to the ai that will play as player 1')
  parser.add_argument('-w', help='time to wait after ai action')
  args = parser.parse_args()
  # set the time to play
  total_time = int(args.t) if args.t != None else 180
  # set the values
  r = int(args.r) if args.r != None else 8
  c = int(args.c) if args.c != None else 8
  #pl = int(args.pl) if args.pl != None else 2
  pl = 2
  pe = int(args.pe) if args.pe != None else 4
  wait = float(args.w) if args.w != None else 0
  quit = args.q
  player_type = [ 'human', 'human' ]
  player_type[0] = args.ai0 if args.ai0 != None else 'human'
  player_type[1] = args.ai1 if args.ai1 != None else 'human'
  agents = [ None for _ in range(pl) ]
  # load the agents
  for i in range(pl):
    if player_type[i] != 'human':
      j = player_type[i].rfind('/')
      # extract the dir from the agent
      dir = player_type[i][:j]
      # add the dir to the system path
      sys.path.append(dir)
      # extract the agent filename
      file = player_type[i][j+1:]
      # create the agent nstance
      agents[i] = getattr(__import__(file), 'MyAgent')()
      agents[i].set_id(i)
  # initialize pygame
  pygame.init()
  # load resources
  tiles = [ pygame.image.load(os.path.join('resources/' + str(i) + 'fish.png')) for i in range(4) ]
  select = pygame.image.load(os.path.join('resources/select.png'))
  penguins = [ pygame.image.load(os.path.join('resources/' + str(i) + 'penguin_t.png')) for i in range(2) ]
  score_lbl = pygame.image.load(os.path.join('resources/score.png'))
  selected_aura = pygame.image.load(os.path.join('resources/selected_t.png'))
  # initialize time variables
  time_left = [total_time for _ in range(pl)]
  # get the dimensions of the hexagons
  rect = tiles[1].get_rect()
  W = rect.width
  H = rect.height
  # initialize the state
  state = generate_initial_state(r, c, pl, pe)
  # precompute the hexagons
  hexagons = [ [ getHexagon((i, j), W, H) for j in range(c - i % 2) ] for i in range(r) ]
  # compute the size the grid will take on the window
  grid_size = (W * c, H + 3 * H * (r - 1) // 4)
  # create the screen
  os.environ['SDL_VIDEO_CENTERED'] = '1'
  screen = pygame.display.set_mode((2 * score_lbl.get_rect().width + grid_size[0] + 20, grid_size[1]))
  # initialize the clock
  clock = pygame.time.Clock()
  # initialize the position where the mouse is
  over = None
  # initialize the possible moves
  moves = None
  # initialize the origin of the move
  origin = None
  # initialize fonts
  score_points_font = pygame.font.SysFont("monospace", 30)
  end_points_font = pygame.font.SysFont("monospace", 30)
  # flag to know if the ai thread has been started
  ai_thinking = False
  start_ticks=pygame.time.get_ticks() #starter tick
  # start countdown
  CONTDOWN = pygame.USEREVENT + 1
  pygame.time.set_timer(CONTDOWN, 1000)
  # time
  start = 0
  end = 0
  # start game loop
  while not state.game_over():
    if pygame.event.get(pygame.QUIT):
      pygame.quit()
      sys.exit()
    timeout = False
    for p in range(pl):
      if time_left[p] - end + start <= 0:
        time_left[p] = 0
        state.set_score(p, -1)
        timeout = True
    if timeout:
      break
    if player_type[state.cur_player] != 'human':
      if not ai_thinking:
        action = get_action_threaded(state, agents[state.cur_player], time_left[state.cur_player])
        start = time.time()
        ai_thinking = True
      elif action != [None]:
        end = time.time()
        time_left[state.cur_player] -= end - start
        ai_thinking = False
        start = 0
        end = 0
        if time_left[state.cur_player] > 0:
          state.apply_action(action[0])
          action = [None]
          time.sleep(wait)
    else:
      # handle human player
      # loop over events and update game
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          # quit the game
          pygame.quit()
          sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
          clicked = get_selected_cell(r, c, event.pos, hexagons)
          if not clicked == None:
            # get coordinates
            i = clicked[0]
            j = clicked[1]    
            # mouse clicked in valid position
            # check the game phase
            if state.placement_phase:
              # placement phase
              if state.penguins[i][j] == -1 and state.fish[i][j] == 1:
                # this position is free, add penguin
                state.apply_action(('place', (i, j)))
            else:
              # movement phase
              if (i, j) in state.penguin_positions[state.cur_player]:
                # no penguin selected yet
                if state.penguins[i][j] == state.cur_player:
                  # this cell contains a penguins of the current player
                  moves = state.get_moves(i, j)
                  origin = (i, j)
              if origin != None:
                # there is a penguin selected
                if (i, j) in moves:
                  # the destination is valid
                  state.apply_action(('move', origin, (i, j)))
                  moves = None
                  origin = None
        elif event.type == pygame.MOUSEMOTION:
          over = get_selected_cell(r, c, event.pos, hexagons)
    draw_screen()
    clock.tick(60)
  draw_screen()
  if quit:
    print(state.get_scores())
    pygame.quit()
    sys.exit()
  else:
    while True:
      # the game is over, we only case about the close event
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          # quit the game
          pygame.quit()
          sys.exit()
