# Compelled movements - Sudden position jump 
# Clara Kuper 2019
#########################################
##To Dos#################################

# release key tracking
# eyetracking

# Initialize the EyeLink system, and open a link connection to the EyeLink tracker.
# Check the display mode, create a full-screen window, and initialize the calibration system.
# Send any configuration commands to the EyeLink tracker to prepare it for the experiment
# Set an EDF file name, and open an EDF data file (stored on the eye tracker)
# Record one or more blocks of trials.
# Each block typically begins with tracker setup (camera setup and calibration), and then several trials are run.
# Close the EDF data file.
# If desired, copy it via the link to the local computer. 
# Close the window, and the link connection to the eye tracker. 

#########################################

#########################################
##### Changes/Future Versions ###########
#########################################

# Probabilty

#########################################

# Setup of the environment
# Import relevant functions
from __future__ import absolute_import, division, print_function, unicode_literals
from psychopy import visual, core, event, gui
import os as os
import pylink as pl
import random as rd
import numpy as np
import pandas as pd
from psychopy.iohub.client import launchHubServer


io = launchHubServer(psychopy_monitor_name = 'default')

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
        info = {'Participant':'Your Code','Experiment':'CoMo4','Session_No':0}
        infoDlg = gui.DlgFromDict(dictionary = info, title = 'participant data', fixed = ['Experiment'])
        
        exp  = info['Experiment']
        name = info['Participant']
        session = str(info['Session_No'])
        # input file
        data_file = path_to_dat + exp + name + session + '.txt'
        
        if os.path.isfile(data_file):
            pass
        else: 
            return data_file, name, session, exp

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


###################################
## Set Parameters for experiment ##
###################################

# path
path_to_exp    = 'C://Users//Clara//Documents//Projects//CompelledMovements//'
path_to_dat    = path_to_exp + 'data//'

# waiting times
prep_time_pre  = 0.2
prep_time_post = 0.2 ## not used 

# repetition and blocks
reps   = 1
nblock = 1


##################
## Setup screen ##
##################

mykb    = io.devices.keyboard
display = pl.getDisplayInformation()
mykb.reporting = False

disp_pix       = [display.width, display.height]
fullscreen     = True
background_rgb = [1,1,1] #white
scrcenter      = [0,0]
scrdist        = 52

monitor_name   = ''

fix_bound_px  = 0.5

###################
## Setup stimuli ##
###################

# the speed of the ball
speed          = 0.5
# translation to left/right
shift_size     = [-5,+5]
# start position of the ball
ball_start     = 3
# how long is the flight
goal_distance  = 9
# how broad is the goal
goal_size      = 5
# distance of change
dir_change     = drange(0.0, 0.6, 0.1)

# jitter time
jitter_time    = drange(0.3,1.0,0.15)

#################
## Participant ##
#################

# get participant data
data_file, name, session, exp = get_data(path_to_dat)

edf_filename = 'et_' + name + session + '.edf'


####################
## Tracker Setup ###
####################

tracking = False

if tracking:
    tracker = pl.EyeLink('100.1.1.1')
    sampling_rate = 1000
    import online_sac_detect_module
    sac_event = online_sac_detect_module.online_sac_detect()
    sac_event.set_parameters(samp_rate = sampling_rate )
else:
    tracker = pl.EyeLink(None)


#################
## Make design ##
#################

dfs = []
cond_i = 0

for rep in range(reps):
    for shift in shift_size:
        for dir_ch in dir_change:
            cond_i = cond_i + 1
            trial_goal_dis   = goal_distance
            trial_speed      = speed
            trial_ball       = ball_start
            trial_shift      = shift
            trial_goal_size  = goal_size
            trial_jitter     = np.random.choice(jitter_time,1)[0]
            
            df = pd.DataFrame(data = [[cond_i,trial_speed,trial_ball,trial_goal_dis,trial_goal_size,trial_jitter,dir_ch, trial_shift]], columns = ['trial','speed','ball_pos','distance','broad','jitter','gap_time', 'shift_pos'])
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
full_df.to_csv(path_to_dat + exp + 'des' + name + session + ".txt",sep='\t', encoding='utf-8', index = False)

###################################
## Setup display and calibration ##
###################################

def set_screen(): # screen properties
    
    # change monitor settings:
    mon = monitors.Monitor(monitor_name)
    mon.setDistance(scrdist)
    mon.setSizePix(disp_pix)
    
    fix_bound_start  = monitorunittools.deg2pix(fix_bound, mon)
    fix_bound_end    = monitorunittools.deg2pix(fix_bound+0.5, mon)
    

    ########################
    ## initialize stimuli ##
    ########################
    
    mywin    = visual.Window(disp_pix, allowGUI = True, fullscr = fullscreen, monitor = 'testMonitor', units = 'pix')
    
    if eye_track == True:
        mymouse = event.Mouse(visible=False, newPos=scrcenter, win=win)
    else:
        mymouse = event.Mouse(visible=True, win=win)
        
    mygoal   = visual.Line(win = mywin, start = (0,0),end = (0,0))
    myball   = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='white') 
    mykeeper = visual.Line(win = mywin, start = (0,0),end = (0,0),lineColor = 'black')
    trial_timer    = core.Clock()
    gap_timer      = core.Clock()
 
    win.flip() # initiate first screen paint
    
    setup_eye_track()


def setup_eye_track():

    # Start file and write first command
    tracker.openDataFile(edf_filename)
    pylink.flushGetkeyQueue()
    tracker.sendCommand("add_file_preamble_text 'Psychopy Test'")
    
    #??? Whats that doing?##
    genv = EyeLinkCoreGraphicsPsychoPy(tk, win) 
    pylink.openGraphicsEx(genv)
    
    # Tracker in offline mode
    tracker.setOfflineMode()
    
    #######################
    ## Tracker settings ###
    #######################
    
    # Set sampling rate
    tracker.sendCommand('sample_rate 1000')
    # Display resolution
    tracker.sendCommand("screen_pixel_coords = 0 0 %d %d" % (screen_w-1, screen_h-1))
    tracker.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (screen_w-1, screen_h-1))
    tracker.sendMessage("DISPLAY_COORDS = 0 0 %d %d" % (screen_w-1, screen_h-1))
    
    # Calibration type
    tracker.sendCommand("calibration_type = HV9")
    tracker.sendCommand("calibration_area_proportion 0.7 0.7")
    tracker.sendCommand("validation_area_proportion  0.7 0.7")
    
    # Tracker model
    eyelinkVer = tracker.getTrackerVersion()
    
    #turn off scenelink camera stuff (EyeLink II/I only)
    if eyelinkVer == 2: tracker.sendCommand("scene_camera_gazemap = NO")
    # Parse Events using "GAZE" (or "HREF") data
    tracker.sendCommand("recording_parse_type = GAZE")
    # Online parser configuration: 0-> standard/cognitve, 1-> sensitive/psychophysiological
    if eyelinkVer>=2: tracker.sendCommand('select_parser_configuration 0')
    # get Host tracking software version
    hostVer = 0
    if eyelinkVer == 3:
        tvstr = tracker.getTrackerVersionString()
        vindex = tvstr.find("EYELINK CL")
        hostVer = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
        
    # EVENT and SAMPLE data stored in EDF/retrievable from link
    
    tracker.sendCommand("file_event_filter = LEFT,RIGHT,BLINK,MESSAGE")
    tracker.sendCommand("link_event_filter = LEFT,RIGHT,BLINK,MESSAGE")
    if hostVer>=4:
        tracker.sendCommand("file_sample_data = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT")
        tracker.sendCommand("link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT")
    else:
        tracker.sendCommand("file_sample_data = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,INPUT")
        tracker.sendCommand("link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT")
        
    fix_box_size = fix_bound_px

def calibr():
    global eye_tracked
    win.flip()
    tk.doTrackerSetup()
    #determine which eye(s) are available
    eye_tracked = tk.eyeAvailable()
    if eye_tracked==2: eye_tracked = 1

###########################################
### functions for timing and presenting ###
###########################################

def feedback(waiting_time, feedback , points):
    '''
    take to stimuli and print them alternating while showing the word "caught"
    '''
    
    basic_feedback = visual.TextStim(win = mywin,text = feedback, pos = (0,0))
    point_feedback = visual.TextStim(win = mywin,text = str(points), pos = (0,1))
    timer = core.Clock()
    timer.reset()
    timer.add(waiting_time)
    while timer.getTime() < 0:
        basic_feedback.draw()
        point_feedback.draw()
        mywin.flip()
        point_feedback.setPos([0.0,0.1],'+')


def block_intro(nblock,mywin):
    '''
    print sth as block introduction
    '''
    write = "Block %s" %(nblock+1)
    visual.TextStim(win = mywin,text = write, pos = (0,0)).draw()

def check_correct(resp,new_loc):
    if resp == 'n': 
        if new_loc > 0:
            return 1
        else:
            return 0
    if resp == 'v':
        if new_loc < 0:
            return 1
        else: 
            return 0

##################################
##### Single Trial Function ######
##################################

def play_trial(mywin , trial_data, trial_id):
    '''
    serial presentation of stimuli with given parameter, monitor timing
    returns information about participant behaviour
    '''
    ########################
    ## Eye Tracking to Do ##
    ########################
    
    #Create a data message (TRIALID) and title to identify the trial
    #Create background graphics on the eye tracker display
    #Perform a drift correction, or display a fixation target
    #Start the EyeLink recording to the EDF file
    #Display graphics for the trial.  (These may have been prepared as a bitmap before the trial).
    #Loop  until  the  trial  time  is  up,  a  button  is  pressed on the tracker, or the recording is interrupted from  the  tracker.
    #The  display  may  be  changed  as  required  for  the  trial  (i.e.  moving  a  target  to elicit saccades) in this loop.
    #Real-time eye-position and saccade/fixation data are also available for gaze-contingent displays and control.
    #Stop  recording,  and  handle  any  special  exit  conditions.
    #Report  trial  success  or  errors  by  adding messages to the EDF file.
    #Optionally, play back the data from the trial for on-line analysis. 
    
    
    # define a timer
    trial_prepared = False
    trial_timer.reset()
    trial_timer.add(prep_time_pre)
    
    while trial_timer.getTime()<0:
        if not trial_prepared:
            ##### timing parameters #####
            t_start      = 0
            t_set        = 0
            t_ball       = 0
            t_release    = 0
            t_change     = 0
            t_response   = 0
            t_goal       = 0
            score        = 0
            correct      = 'na'
            
            # set position of stimuli
            myball.setPos([0,int(trial_data['ball_pos'])])
            mygoal.setStart([-int(trial_data['broad']),-int(trial_data['distance'])])
            mygoal.setEnd([+int(trial_data['broad']),-int(trial_data['distance'])])
            keeper_cover = int(trial_data['broad'])
            mykeeper.setStart([mygoal.start[0]+(keeper_cover/2),mygoal.start[1]])
            mykeeper.setEnd([mygoal.end[0]-(keeper_cover/2),mygoal.start[1]])
            # reset answers
            key_hit = False
            # reset keyboard
            io.clearEvents('all')
            # When does the ball change direction
            dirchange = trial_data['gap_time'].values
            # shifted position 
            new_pos   = trial_data['shift_pos'].values
            
            # initiate a list that will save the pressed keys
            keypress  = []
            
            # labels for while loops
            jumped         = False
            goal_reached   = False
            trial_prepared = True
            
        else:
            pass

    # wait for keypress
    mykb.reporting = True
    # draw goal
    mygoal.draw()
    # draw ball on screen
    myball.draw()
    t_start = mywin.flip()
    
    keys = io.devices.keyboard.waitForKeys(keys = ['b'])
    mykb.reporting = False
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
        gap_timer.reset()
        gap_timer.add(dirchange)
        
        mykb.reporting = True
        t_ball = core.getTime()
        while gap_timer.getTime() < 0:
            # ball flight straight
            # update the position of the ball
            myball.setPos([0.0,speed],'-')
            mygoal.draw()
            # draw keeper
            mykeeper.draw()
            # draw ball on screen
            myball.draw()
            # update window
            mywin.flip()
            if not key_hit:
                for kb_event in mykb.getEvents():
                    keypress = kb_event.char
                    if keypress == 'n':
                        # print response right
                        mykeeper.setStart(mygoal.end)
                        mykeeper.setEnd([mygoal.end[0]-keeper_cover,mygoal.end[1]])
                    if keypress == 'v':
                        #print response left
                        mykeeper.setStart(mygoal.start)
                        mykeeper.setEnd([mygoal.start[0]+keeper_cover,mygoal.start[1]])
                    if keypress == 'v' or 'n':
                        correct = check_correct(keypress,new_pos)
                        mykb.reporting = False
                        t_response = kb_event.time
                        key_hit=True
            if int(myball.pos[1]) == int(mygoal.start[1]):
                break

        myball.setPos([new_pos,0.0],'+')
        t_change = core.getTime()
        
        last_rescue = core.Clock()
        last_rescue.add(5.0)
        
        while not goal_reached:
            # update the position of the ball
            myball.setPos([0.0,speed],'-')
            # draw goal
            mygoal.draw()
            # draw keeper
            mykeeper.draw()
            # draw ball on screen
            myball.draw()
            # update window
            mywin.flip()
            if not key_hit:
                for kb_event in mykb.getEvents():
                    keypress = kb_event.char
                    if keypress == 'n':
                        # print response right
                        mykeeper.setStart(mygoal.end)
                        mykeeper.setEnd([mygoal.end[0]-keeper_cover,mygoal.end[1]])
                    if keypress == 'v':
                        #print response left
                        mykeeper.setStart(mygoal.start)
                        mykeeper.setEnd([mygoal.start[0]+keeper_cover,mygoal.start[1]])
                    if keypress == 'v' or 'n':
                        correct = check_correct(keypress,new_pos)
                        mykb.reporting = False
                        t_response = kb_event.time
                        key_hit=True
            # check keyboard presses
            if int(myball.pos[1]) == int(mygoal.start[1]):
                t_goal = core.getTime()
                if correct == 1:
                    feedback(0.5, 'caught','+5')
                    score = 5
                if correct == 0:
                    feedback(0.5, 'missed','0')
                if correct == 'na':
                    feedback(0.5, 'too slow!!','-10')
                    score = -10
                mykb.reporting = False
                goal_reached   = True
            
            if last_rescue.getTime()>0:
                goal_reached   = True
                
        break
    resp_data = pd.DataFrame(data = [[keypress,trial_id+1,t_start,t_set, t_ball, t_release, t_response, t_goal, t_change, new_pos, correct]], columns = ['response','trial_nr','t_start','t_set','t_ball','t_release','t_response','t_goal','t_change','new_pos','correct'])
    
    core.wait(0.5)
    
    return resp_data, score

# define a function that gets the trial information and plays alls trial in a row
# play all trials in a block

def play_block(full_df, block_id):
    responses = []
    # play all trials in one block
    # initialize data frame
    block_data = full_df.query('block == %s' %(block_id))
    trial_number = len(block_data)
    block_score  = 0
    
    calibr()

    for trial in range(trial_number):
        trial_data = block_data.query('trial_nr == %s'%(trial+1))
        # play trials and get the pressed keys
        resp_dat, score   = play_trial(mywin,trial_data,trial)
        responses.append(resp_dat)
        
        block_score = block_score + score
        # clear screen after trial is played
        mywin.flip()
        core.wait(0.5)
    all_responses = pd.concat(responses)
    feedback(1.5, 'You scored %s' %(block_score),' ')
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
response_data.to_csv(data_file, delimiter='\t', encoding='utf-8', index = False)

# end and close after 3 secs
core.wait(1.0)
mywin.saveFrameIntervals(fileName = path_to_dat + '/' + 'framtime.log', clear = True)
mywin.close()

io.quit()
core.quit()