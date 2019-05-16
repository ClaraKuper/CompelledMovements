# Compelled movements - The football task
# Clara Kuper 2019
#########################################
#########################################
# Troubleshoots needed:
# release key tracking
# ioHub needs to work on PC
##########################################
##########################################
##### Changes/Future Versions ############
##########################################
# Probabilty
# Sudden change of direction with fixed goal distance
##########################################

# Setup of the environment
# Import relevant functions
from psychopy import visual, core, event, gui
import os as os
import random as rd
import numpy as np
import pandas as pd
from psychopy.iohub.client import launchHubServer

###################################
###### Functions for setup ########
###################################

# get participant data
def get_data(path_to_dat):
    '''
    Function calls GUI, asks for data, defines name for data file 
    and checks if the file already exists.
    
    Returns the name of the data file.
    '''
    
    while True:
        info = {'Participant':'Your Code','Experiment':'CompelledMovements','Session_No':0}
        infoDlg = gui.DlgFromDict(dictionary = info, title = 'participant data', fixed = ['Experiment'])
        
        name = info['Participant']
        session = str(info['Session_No'])
        # input file
        data_file = path_to_dat + name + session + '.txt'
        
        if os.path.isfile(data_file):
            pass
        else: 
            return data_file, name, session

# define a range function for decimals
def drange(x,y,jump):
    '''
    a range function for decimals, returns a list
    '''
    
    out = []
    while x < y:
        out.append(x)
        x = x+jump
    return out


##########################################
## Set Parameters for experiment #########
##########################################

# path
path_to_exp    = '/home/clara/Documents/projects/CompelledMovements'
path_to_dat    = path_to_exp + '/data/'

# waiting times
prep_time_pre  = 0.2
prep_time_post = 0.2 ## not used 

# repetition and blocks
reps   = 2
nblock = 5

# screen
window_size    = []
fullscreen     = True
background_rgb = [1,1,1]
scrcenter      = [0,0]

#########################
## Stimulus parameters ##
#########################

# the speed of the ball
speed          = 0.5
# angle of flight (ration between cath & ancath)
sides_ratio    = 0.5
# the start position of the player
player_start   = 4
# start position of the ball
ball_start     = 0
# will the ball fly left or right
ball_directions= ['-','+']
# how long is the flight
goal_distance       = drange(2.0,9.0,0.5)
# jitter time
jitter_time    = drange(0.3,1.0,0.15)

#################
## Participant ##
#################

# get participant data
data_file, name, session = get_data(path_to_dat)



########################
## initialize stimuli ##
########################

io      = launchHubServer(psychopy_monitor_name = 'default')
mykb    = io.devices.keyboard
display = io.devices.display
mykb.reporting = False
    
mywin    = visual.Window(display.getPixelResolution(), allowGUI = True, fullscr=True, monitor = 'testMonitor', units = 'cm')
mywin.MouseVisible = False
mygoal   = visual.Line(win = mywin, start = (0,0),end = (0,0))
myball   = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='red') 
mykeeper = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='green')
myplayer = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='blue')

#################
## Make design ##
#################

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
            trial_jitter     = np.random.choice(jitter_time,1)[0]
            
            df = pd.DataFrame(data = [[cond_i,trial_speed,trial_player,trial_ball,dir,goal_dist,trial_goal_size,trial_jitter]], columns = ['trial','speed','player_pos','ball_pos','direction','distance','broad','jitter'])
            dfs.append(df)

ntrials = len(dfs)

# arrange in blocks

blocks = []

for block in range (nblock):
    np.random.shuffle(dfs)
    for trial in range(ntrials):
        df_temp = dfs[trial]
        df_temp['trial_nr'] = trial+1
        dfs[trial]  = df_temp
    block_temp = pd.concat(dfs)
    block_temp['block']= block
    
    blocks.append(block_temp)

full_df       = pd.concat(blocks)

# save design 
full_df.to_csv(path_to_dat + '/des' + name + session + ".txt",sep='\t', encoding='utf-8', index = False)

###########################################
### functions for timing and presenting ###
###########################################

def response_flicker(stim1, stim2, repetition, waiting_time):
    '''
    take to stimuli and print them alternating while showing the word "caught"
    '''
    
    positive_feedback = visual.TextStim(win = mywin,text = 'caught!', pos = (0,0))
    
    # ball and keeper at the same spot
    stim1.setPos(stim2.pos)
    
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

def block_intro(nblock,mywin):
    '''
    print sth as block introduction
    '''
    write = "Block %s" %(nblock+1)
    visual.TextStim(win = mywin,text = write, pos = (0,0)).draw()

###################################
###### Single Trial Function ######
###################################

def play_trial(mywin , trial_data, trial_id):
    '''
    serial presentation of stimuli with given parameter, monitor timing
    returns information about participant behaviour
    '''
    
    # define a timer
    trial_timer    = core.Clock()
    trial_prepared = False
    trial_timer.reset()
    trial_timer.add(prep_time_pre)
    
    while trial_timer.getTime()<0:
        if not trial_prepared:
            ##### timing parameters #####
            t_start    = 0
            t_set      = 0
            t_ball     = 0
            t_release  = 0
            t_response = 0
            t_goal     = 0

            # set position of stimuli
            myplayer.setPos([0,int(trial_data['player_pos'])])
            myball.setPos([0,int(trial_data['ball_pos'])])
            mygoal.setStart([-int(trial_data['broad']),-int(trial_data['distance'])])
            mygoal.setEnd([+int(trial_data['broad']),-int(trial_data['distance'])])
            mykeeper.setPos([0,-int(trial_data['distance'])])
            # reset answers
            key_hit = False
            # reset keyboard
            io.clearEvents('all')
            # Define the duration of the trial in frames
            # How long does the player move towards the ball
            runtime   = (myplayer.pos[1]-myball.pos[1])/speed
            # How long does the ball move
            ballfly   = (myball.pos[1]-mygoal.start[1])/speed
            # How long are both times together
            trialtime = int(runtime)+int(ballfly)+20
            # initiate a list that will save the pressed keys
            sign      = trial_data['direction'].values
            trial_jitter = trial_data['jitter'].values
            keypress  = []
            trial_prepared = True
        else:
            pass

    # wait for keypress
    mykb.reporting = True
    # draw player on screen
    myplayer.draw()
    # draw goal
    mygoal.draw()
    # draw ball on screen
    myball.draw()
    t_start = mywin.flip()
    keys = io.devices.keyboard.waitForKeys(keys = ['b'])
    
    mykb.reporting = False
    # draw player on screen
    myplayer.draw()
    # draw goal
    mygoal.draw()
    # draw keeper
    mykeeper.draw()
    # draw ball on screen
    myball.draw()
    t_set = mywin.flip()
    # wait for jitter
    core.wait(trial_jitter)
    
    # Update the screen with every frame
    while True: 
        for frameN in range(trialtime):
            mykb.reporting = False
            # If the player has reached the ball
            if frameN == runtime:
                t_ball = core.getTime()
            if frameN >= runtime:
                mykb.reporting = True
                # update the position of the ball
                myball.setPos([0.0,speed],'-')
                myball.setPos([speed*sides_ratio,0.0],sign)
            else:
                # update the position of the player
                myplayer.setPos([0,speed],'-')
                
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
                for kb_event in mykb.getEvents():
                    if kb_event.char == 'n':
                        # print response right
                        mykb.reporting = False
                        mykeeper.setPos(mygoal.end)
                        keypress = 'n'
                        key_hit = True
                        t_response = kb_event.time
                    if kb_event.char == 'x':
                        mykb.reporting = False
                        keypress = 'x'
                        key_hit = True
                        t_response = kb_event.time
                        break
                    if kb_event.char == 'v':
                        #print response left
                        mykb.reporting = False
                        mykeeper.setPos(mygoal.start)
                        keypress = 'v'
                        key_hit = True
                        t_response = kb_event.time
                mykb.reporting = False
            if int(myball.pos[1]) == int(mygoal.start[1]):
                t_goal = core.getTime()
                if keypress == 'v' and sign == '-' or keypress == 'n' and sign == '+':
                    response_flicker(myball,mykeeper,5,0.1)
                    trial_on = False
                    break
        break
    resp_data = pd.DataFrame(data = [[keypress,trial_id+1,t_start,t_set - t_start, t_ball - t_start, t_release, t_response - t_ball, t_goal-t_start]], columns = ['response','trial_nr','t_start','t_set','t_ball','t_release','t_response','t_goal'])
    
    core.wait(0.5)
    
    return resp_data

# define a function that gets the trial information and plays alls trial in a row
# play all trials in a block

def play_block(full_df, block_id):
    responses = []
    # play all trials in one block
    # initialize data frame
    block_data = full_df.query('block == %s' %(block_id))
    trial_number = len(block_data)

    for trial in range(trial_number):
        trial_data = block_data.query('trial_nr == %s'%(trial+1))
        # play trials and get the pressed keys
        resp_dat   = play_trial(mywin,trial_data,trial)
        responses.append(resp_dat)
        
        # clear screen after trial is played
        mywin.flip()
        core.wait(0.5)
    all_responses = pd.concat(responses)
    # make data available
    return all_responses


# Run the entire experiment
def play_experiment(blockn):
    # initialize data frame
    mywin.flip()
    data = []
    # for all blocks in the experiment
    for block in range(blockn):
        
        # define the parameters based on the design matrix
        block_intro(block,mywin)
        mywin.flip()
        
        key_was_down_x = event.getKeys(keyList=['x'],timeStamped=True)
        core.wait(0.5)
        if key_was_down_x:
            play = False
        event.waitKeys(keyList=['g'])
        
        
        # play all blocks
        block_data = play_block(full_df,block)
        data.append(block_data)
        
        # clear screen after block is over and wait a little bit
        mywin.flip()
        core.wait(3.0)
    complete_data       = pd.concat(data)
    return complete_data


# Play the experiment:
response_data = play_experiment(nblock)
response_data.to_csv(data_file, sep='\t', encoding='utf-8', index = False)

# end and close after 3 secs
core.wait(1.0)
mywin.saveFrameIntervals(fileName = path_to_dat + '/' + 'framtime.log', clear = True)
mywin.close()

io.quit()
core.quit()