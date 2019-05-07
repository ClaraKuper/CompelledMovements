# Compelled movements - The football task
# Clara Kuper 2019

# Troubleshoots needed:
# Track timimg of stimulus and response
# Keypresses only when wanted
# Save design output
# Design matrix to data frame

# Needs two versions: for Linux (iohub working) and windows (iohub not working)

win = False
lin = True

# Setup of the environment
# Import relevant functions

from psychopy import visual, core, event, gui
import os as os
import random as rd
import numpy as np
import pandas as pd
import myfuncs as mf
if lin:
    from psychopy.iohub.client import launchHubServer

global visual, core, event, gui, os, rd, np, pd, mf

## Parameters
## General parameters
path_to_exp    = '/home/clara/Documents/projects/CompelledMovements'
path_to_dat    = path_to_exp + '/data'

prep_time_pre  = 0.2
prep_time_post = 0.2

reps   = 2
nblock = 2

window_size    = []
fullscreen     = True
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
data_file, name, session = mf.get_data()

mywin    = visual.Window(size = window_size, allowGUI = True, fullscr=True, monitor = 'testMonitor', units = 'norm')
## that goes to make_design
exp_data = pd.DataFrame(np.nan, index=[], columns=['trial','response', 'speed', 'player', 'ball', 'direction', 'goal_size', 'goal_height'])
##
mygoal   = visual.Line(win = mywin, start = (0,0),end = (0,0))
myball   = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='red') 
mykeeper = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='green')
myplayer = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='blue')

if lin:
    io      = launchHubServer(experiment_code = data_file, psychopy_monitor_name = 'default')
    mykb    = io.devices.keyboard
    mykb.reporting = False



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
            
            df = pd.DataFrame(data = [cond_i,trial_speed,trial_player,trial_ball,dir,goal_dist,trial_goal_size], index = ['trial','speed','player_pos','ball_pos','direction','distance','broad'])
            dfs.append(df)
ntrials = len(dfs)

# shuffe for random
np.random.shuffle(dfs)

# add trial number
block_df = []

for block in range(nblock):
    for trial in range(ntrials):
        df_temp = dfs[trial]
        df_temp['trial_nr'] = trial+1
        df_temp['block']    = block
        dfs[trial]  = df_temp
    block_df.append(dfs)

# get trial 0
df_trial_zero = df_temp

# one data frame
full_df       = pd.concat(block_df[0])

# save design 
full_df.to_csv(path_to_dat + '/des' + data_file, index = False)

## Define the events in one trial
## This takes as input information from the design matrix
def play_trial(mywin , full_df, trial_id):

    # define a timer
    trial_timer    = core.Clock()
    trial_prepared = False
    trial_timer.reset()
    trial_timer.add(prep_time_pre)
    
    while trial_timer.getTime()<0:
        if not trial_prepared:
            # player, goal, keeper, ball
            myplayer.setPos([0,full_df['player'][trial_id]])
            myball.setPos([0,full_df['ball'][trial_id]])
            mygoal.setStart([-full_df['broad'][trial_id],-full_df['distance'][trial_id]])
            mygoal.setEnd([+full_df['broad'][trial_id],-full_df['distance'][trial_id]])
            mykeeper.setPos([0,-full_df['distance'][trial_id]])
            # reset answers
            key_hit = False
            # Define the duration of the trial in frames
            # How long does the player move towards the ball
            runtime   = (t_player.pos[1]-t_ball.pos[1])/t_speed
            # How long does the ball move
            ballfly   = (t_ball.pos[1]-t_goal.start[1])/t_speed
            # How long are both times together
            trialtime = int(runtime)+int(ballfly)+20
            # initiate a list that will save the pressed keys
            keypress  = []
            trial_prepared = True
        else:
            pass

    # wait for keypress
    mykb.reporting = True
    if win:
        keys = event.waitKeys(keyList=['b'])
    else:
        keys = io.devices.keyboard.waitForKeys(keys = ['b',], maxWait = 10)
    if keys:
        mykb.reporting = False
        # draw player on screen
        myplayer.draw()
        # draw goal
        mygoal.draw()
        # draw keeper
        mykeeper.draw()
        # draw ball on screen
        myball.draw()
        mywin.flip()
        # wait for jitter
        core.wait(0.5)
    else:
        pass
    
    # Update the screen with every frame
    while True: 
        for frameN in range(trialtime):
            mykb.reporting = False
            # If the player has reached the ball
            if frameN >= runtime:
                mykb.reporting = True
                # update the position of the ball
                myball.setPos([0.0,t_speed],'-')
                myball.setPos([t_speed*t_ratio,0.0],t_sign[0])
            else:
                
                # update the position of the player and check if 'b' is pressed
                myplayer.setPos([0,t_speed],'-')
                #was_pressed = t_kb.getReleases(keys = 'b',clear = True)
                #if was_pressed:
                #    print(was_pressed)
                    #feedback_press
                    #mywin.flipkb
                    #t_kb.clearEvents()
                    #core.wait(0.1)
                    #break
            # draw player on screen
            myplayer.draw()
            # draw goal
            mygoal.draw()
            # draw keeper
            mykeeper.draw()
            # draw ball on screen
            myball.draw()
            # update window
            mywin.flip()
            # check keyboard presses
            if not key_hit:
                key_was_down_n = event.getKeys(keyList=['n'],timeStamped=True)
                key_was_down_x = event.getKeys(keyList=['x'],timeStamped=True)
                key_was_down_v = event.getKeys(keyList=['v'],timeStamped=True)
                if key_was_down_n:
                    # print response right
                    mykeeper.setPos(t_goal.end)
                    keypress = 'n'
                    key_hit = True
                if key_was_down_v:
                    #print response left
                    mykeeper.setPos(t_goal.start)
                    keypress = 'v'
                    key_hit = True
                if key_was_down_x:
                    keypress = 'x'
                    key_hit = True
                    break
                mykb.reporting = False
            if int(myball.pos[0]) == int(mykeeper.pos[0]) and int(myball.pos[1]) == int(mykeeper.pos[1]):
                mf.response_flicker(myball,mykeeper,5,0.1)
                trial_on = False
                break
        break
    
    
    core.wait(0.5)
    return keypress

# define a function that gets the trial information and plays alls trial in a row
# play all trials in a block

def play_block(full_df, block_id):
    # play all trials in one block
    # initialize data frame
    block_data = full_df.query('block'== block_id)

    for trial in range(trial_number):
        trial_data = block_data.query('trial_nr' == trial)
        # play trials and get the pressed keys
        key_response   = play_trial(mywin,trial_data)
        trial_data.iloc[trial]['response']   = str(key_response)
        
        # clear screen after trial is played
        mywin.flip()
        core.wait(0.5)
        
    # make data available
    return(trial_data)
    


# Run the entire experiment
def play_experiment(blockn):
    # initialize data frame
    mywin.flip()
    
    # for all blocks in the experiment
    for block in range(blockn):
        
        # define the parameters based on the design matrix
        mf.block_intro(block)
        mywin.flip()
        
        key_was_down_x = event.getKeys(keyList=['x'],timeStamped=True)
        core.wait(0.5)
        if key_was_down_x:
            play = False
        event.waitKeys(keyList=['g'])
        
        
        # play all blocks
        block_data = play_block(ntrial,speed_list, player_pos_list,ball_pos_list, ball_direction_list, goal_distance_list, goal_broad_list,global_ratio)
        # save the keys
        block_data['ID']       =  name
        block_data['session']  =  session
        block_data['block']    =  block
        complete_data = join_data_file(block_data,data_file)
        complete_data.to_csv(data_file, sep='\t', encoding='utf-8', index = False)
        # clear screen after block is over and wait a little bit
        mywin.flip()
        core.wait(3.0)
        
    return True


# Play the experiment:
played = play_experiment(nblock)

if played:
    print ('The experiment ran successfull')

# end and close after 3 secs
core.wait(1.0)
mywin.saveFrameIntervals(fileName = 'framtime.log')
mywin.close()
if lin:
    io.quit()
core.quit()