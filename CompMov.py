# Compelled movements - The football task
# Clara Kuper 2019

# Needs two versions: for Linux (iohub working) and windows (iohub not working)

win = False
lin = True

# Setup of the environment
# Import relevant functions
from psychopy import visual, core, event
import random as rd
import numpy as np
import pandas as pd
if lin:
    from psychopy.iohub import launchHubServer

# clean all data in the environment

# input file
data_file = 'Some Name'

# get participant data
name = 'CK'
session = 1

# Setup design and screen
# Define number of blocks and trials
nblock = 2
ntrial = 2

# Define the test monitor, keyboard and objects
# Find out how the window gets automatically full screen
# mouse is not used mymouse = event.Mouse(visible = True, win = mywin)
mywin    = visual.Window(fullscr=True, monitor = 'testMonitor', units = 'cm')
exp_data = pd.DataFrame(np.nan, index=[], columns=['trial','response', 'speed', 'player', 'ball', 'direction', 'goal_size', 'goal_height'])
mygoal   = visual.Line(win = mywin, start = (0,0),end = (0,0))
myball   = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf= 0, color='red') 
mykeeper = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0,color='green')
myplayer = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0,color='blue')

if lin:
    io      = launchHubServer(experiment_code = 'compelled_move', psychopy_monitor_name = 'default')
    mykb    = io.devices.keyboard
    
#teams    = visual.TextStim(win = mywin,text = 'Heute spielt: FSC Friedrichshaus vs Eschbacher Bombers', pos = (0,0))

# build a function that checks if the ID/session are already taken

def check_file(data_file):
    # open file as read
    # check ID and number
    # return true or false
    pass

# build a function that writes data to file

def write_to_file(data,data_file):
    '''
    writes information to fila - can be done for data and design
    '''
    # open file with permission "write"
    # find last line
    # write below last line
    # close file
    pass

#make contact to eyetracker etc.


# define a range function for decimals
def drange(x,y,jump):
    out = []
    while x < y:
        out.append(x)
        x = x+jump
    return out

#  This function provide positive feedack
def response_flicker(stim1, stim2, repetition, waiting_time):
    positive_feedback = visual.TextStim(win = mywin,text = 'caught!', pos = (0,0))
    for reps in range(repetition):
        positive_feedback.draw()
        # draw keeper
        stim1.draw()
        # update window
        mywin.flip()
        core.wait(0.1)
        # draw ball on screen
        stim2.draw()
        positive_feedback.draw()
        mywin.flip()
        core.wait(0.1)

def feedback_press():
    visual.TextStim(win = mywin,text = 'Keep the key pressed!', pos = (0,0)).draw()

def block_intro(nblock):
    write = "Block %s" %(nblock+1)
    visual.TextStim(win = mywin,text = write, pos = (0,0)).draw()

# write a function to set up the design matrix
def design_matrix(trials):
    # the speed of the ball
    speed_list          = []
    speedrange          = [0.5]
    # Define the angle for the shot
    down_side_ratio     = 0.5
    # the start position of the player
    player_pos_list     = []
    positions_player    = [2]
    # start position of the ball
    ball_pos_list       = []
    positions_ball      = [0]
    # will the ball fly left or right
    ball_direction_list = []
    ball_directions     = ['+','-']
    # how long is the flight
    goal_distance_list  = []
    goal_distance       = drange(2,9,0.5)
    # the size of the goal
    # defined depending of the flight duration
    goal_broad_list      = []
    
    # for all the trials in one block, write the parameters for the experimental design
    for trial in range(trials):
        #define the speed
        speed_list.append(rd.sample(speedrange,1)[0])
        #define the player position
        player_pos_list.append(5)
        # position of ball
        ball_pos_list.append(rd.sample(positions_ball,1)[0])
        # direction of shot
        ball_direction_list.append(rd.sample((ball_directions),1))
        # flight duration/goal distance
        distance = rd.sample((goal_distance),1)[0]
        goal_distance_list.append(distance)
        # goal size
        side_b = distance*down_side_ratio
        goal_broad_list.append(side_b)
        
    # And make the information available
    return speed_list, player_pos_list,ball_pos_list, ball_direction_list, goal_distance_list, goal_broad_list, down_side_ratio


# Define the events in one trial
# This takes as input information from the design matrix
def play_trial(t_speed, t_player, t_ball, t_win, t_sign, t_goal, t_keeper, t_ratio):

    # reset answers
    key_hit = False
    # Define the duration of the trial in frames
    # How long does the player move towards the ball
    runtime   = (t_player.pos[1]-t_ball.pos[1])/t_speed
    # How long does the ball move
    ballfly   = (t_ball.pos[1]-t_goal.start[1])/t_speed
    # How long are both times together
    trialtime = int(runtime)+int(ballfly)+20
    # Set the speed of the ball, it's twice as fast as the player
    ballspeed = t_speed
    # initiate a list that will save the pressed keys
    keypress  = []
    # start the trial, present ball, player and goal and wait for a keypress
    # draw player on screen
    t_player.draw()
    # draw ball on screen
    t_ball.draw()
    # draw goal
    t_goal.draw()
    # update window
    mywin.flip()
    # wait for keypress
    event.waitKeys(keyList=['b'])
    # draw player on screen
    t_player.draw()
    # draw goal
    t_goal.draw()
    # draw keeper
    t_keeper.draw()
    # draw ball on screen
    t_ball.draw()
    mywin.flip()
    # wait for jitter
    core.wait(0.5)
    
    # Update the screen with every frame
    trial_on = True
    while trial_on: 
        for frameN in range(trialtime):
            # If the player has reached the ball
            if frameN >= runtime:
                # update the position of the ball
                t_ball.setPos([0.0,ballspeed],'-')
                t_ball.setPos([ballspeed*t_ratio,0.0],t_sign[0])
            else:
                # update the position of the player and check if 'b' is pressed
                t_player.setPos([0,t_speed],'-')
                #was_pressed = t_kb.getReleases(keys = 'b',clear = True)
                #if was_pressed:
                #    print(was_pressed)
                    #feedback_press
                    #mywin.flip
                    #t_kb.clearEvents()
                    #core.wait(0.1)
                    #break
            # draw player on screen
            t_player.draw()
            # draw goal
            t_goal.draw()
            # draw keeper
            t_keeper.draw()
            # draw ball on screen
            t_ball.draw()
            # update window
            mywin.flip()
            # check keyboard presses
            if not key_hit:
                key_was_down_n = event.getKeys(keyList=['n'],timeStamped=True)
                key_was_down_x = event.getKeys(keyList=['x'],timeStamped=True)
                key_was_down_v = event.getKeys(keyList=['v'],timeStamped=True)
                if key_was_down_n:
                    # print response right
                    t_keeper.setPos(t_goal.end)
                    keypress = 'n'
                    key_hit = True
                if key_was_down_v:
                    #print response left
                    t_keeper.setPos(t_goal.start)
                    keypress = 'v'
                    key_hit = True
                if key_was_down_x:
                    keypress = 'x'
                    key_hit = True
                    break
            if int(t_ball.pos[0]) == int(t_keeper.pos[0]) and int(t_ball.pos[1]) == int(t_keeper.pos[1]):
                response_flicker(t_ball,t_keeper,5,0.1)
                trial_on = False
                break
        trial_on = False
    
    
    core.wait(0.5)
    return keypress

# define a function that gets the trial information and plays alls trial in a row
# play all trials in a block

def play_block(trial_number,speed_list, player_pos_list,ball_pos_list, ball_direction_list,goal_distance_list,goal_broad_list,my_ratio):
    # play all trials in one block
    # initialize data frame
    trial_data = pd.DataFrame('NA', index=drange(0,trial_number,1), columns=['trial','response', 'speed', 'player', 'ball', 'direction', 'goal_size', 'goal_height'])
    trial_data.shape

    for trial in range(trial_number):
        # set parameters for player, ball and goal
        myplayer.setPos([0,player_pos_list[trial]])
        myball.setPos([0,ball_pos_list[trial]])
        mygoal.setStart([-goal_broad_list[trial],-goal_distance_list[trial]])
        mygoal.setEnd([+goal_broad_list[trial],-goal_distance_list[trial]])
        # set location parameter for keeper
        mykeeper.setPos([0,(-goal_distance_list[trial])])
        # save trial information
        trial_data.iloc[trial]['direction']  = ball_direction_list[trial][0]
        trial_data.iloc[trial]['goal_size']  = mygoal.end[(0)]
        trial_data.iloc[trial]['goal_height']= mygoal.end[(1)]
        trial_data.iloc[trial]['trial']      = trial
        # play trials and get the pressed keys
        key_response   = play_trial(speed_list[trial],myplayer,myball,mywin,ball_direction_list[trial],mygoal,mykeeper,my_ratio)
        trial_data.iloc[trial]['response']   = str(key_response)
        
        # clear screen after trial is played
        mywin.flip()
        core.wait(0.5)
        
    # make data available
    return(trial_data)
    


# Run the entire experiment
def play_experiment(blockn):
    # initialize data frame
    exp_data = pd.DataFrame(np.nan, index=[], columns=['trial','response', 'speed', 'player', 'ball', 'direction', 'goal_size', 'goal_height'])
    mywin.flip()
    
    # for all blocks in the experiment
    for block in range(blockn):
        
        # define the parameters based on the design matrix
        speed_list, player_pos_list,ball_pos_list, ball_direction_list, goal_distance_list, goal_broad_list, global_ratio = design_matrix(ntrial)
        block_intro(block)
        mywin.flip()
        event.waitKeys(keyList=['b'])
        
        # play all blocks
        block_data = play_block(ntrial,speed_list, player_pos_list,ball_pos_list, ball_direction_list, goal_distance_list, goal_broad_list,global_ratio)
        # save the keys
        exp_data = pd.concat([exp_data,block_data])
        # clear screen after block is over and wait a little bit
        mywin.flip()
        core.wait(3.0)
        
    return exp_data


# Play the experiment:
data = play_experiment(nblock)
data['ID']       =  name
data['session']  =  session


# Save the output as text file
data.to_csv('experiment_data.txt', sep='\t', encoding='utf-8')

# end and close after 3 secs
core.wait(1.0)
mywin.saveFrameIntervals(fileName = 'framtime.log')
mywin.close()
#io.quit()
core.quit()