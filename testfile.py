# Setup of the environment
# Import relevant functions
from psychopy import visual, core, event, gui
import os as os
import random as rd
import numpy as np
import pandas as pd
import myfuncs as mf



## Parameters
## General parameters
path_to_exp    = '/home/clara/Documents/projects/CompelledMovements'
path_to_dat    = path_to_exp + '/data'

prep_time_pre  = 0.2
prep_time_post = 0.2

reps   = 1
nblock = 2

window_size    = [10,10]
fullscreen     = False
background_rgb = [1,1,1]
scrcenter      = [0,0]

## Stimulus parameters
# the speed of the ball
speed          = 0.5
# angle of flight (ration between cath & ancath)
sides_ratio    = 0.5
# the start position of the player
player_start   = 2
# start position of the ball
ball_start     = 0
# will the ball fly left or right
ball_directions= ['+','-']
# how long is the flight
goal_distance       = mf.drange(2.0,9.0,0.5)

# participant

# get participant data
data_file, name, session = 'testfile.txt', 'ck', 'test'

mywin    = visual.Window(size = window_size, allowGUI = True, monitor = 'testMonitor', units = 'norm')
mygoal   = visual.Line(win = mywin, start = (0,0),end = (0,0))
myball   = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='red') 
mykeeper = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='green')
myplayer = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='blue')

## Make design
dfs = []
cond_i = 0
for goal_dist in goal_distance:
    for dir in ball_directions:
        for rep in range(reps):
            cond_i = cond_i + 1
            trial_speed      = speed
            trial_ball       = ball_start
            trial_ratio      = sides_ratio
            trial_player     = player_start
            trial_goal_size  = float(goal_dist)*float(trial_ratio)
            
            df = pd.DataFrame(data = [[cond_i,trial_speed,trial_player,trial_ball,dir,goal_dist,trial_goal_size]], columns = ['trial','speed','player_pos','ball_pos','direction','distance','broad'])
            dfs.append(df)

ntrials = len(dfs)

# make blocks
blocks = []

for block in range (nblock):
    np.random.shuffle(dfs)
    for trial in range(ntrials):
        df_temp = dfs[trial]
        df_temp['trial_nr'] = trial+1
        dfs[trial]  = df_temp
    block_temp = pd.concat(dfs)
    block_temp['block']= block
    print(block_temp)
    
    blocks.append(block_temp)

full_df       = pd.concat(blocks)

print(full_df)
