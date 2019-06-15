# Compelled movements - Sudden position jump 
# Clara Kuper 2019
#########################################
#########################################
# To Dos:
# release key tracking
# ioHub needs to work on PC
# stimulus moves straight, then jumps to the left
# /to the right
# distance to the goal is fixed
##########################################
##########################################
##### Changes/Future Versions ############
##########################################
# Probabilty
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
        info = {'Participant':'Your Code','Experiment':'LNDW','Session_No':0}
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


##########################################
## Set Parameters for experiment #########
##########################################

# path
path_to_exp    = 'C://Users//Clara//Documents//Projects//CompelledMovements//'
path_to_dat    = path_to_exp + 'data//'

# waiting times
prep_time_pre  = 0.2
prep_time_post = 0.2 ## not used 

# repetition and blocks
reps   = 1
nblock = 2

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

# rank list
rank           = []

#################
## Participant ##
#################

# get participant data
data_file, filename, session, exp = get_data(path_to_dat)

########################
## initialize stimuli ##
########################

io      = launchHubServer(psychopy_monitor_name = 'default')
mykb    = io.devices.keyboard
display = io.devices.display
mykb.reporting = False
mywin    = visual.Window(display.getPixelResolution(), allowGUI = True, fullscr = fullscreen, monitor = 'testMonitor', units = 'cm')
mywin.MouseVisible = False
mygoal   = visual.Line(win = mywin, start = (0,0),end = (0,0))
myball   = visual.GratingStim(win=mywin, mask = 'circle', pos = [0,0], size = 1, sf = 0, color='white') 
mykeeper = visual.Line(win = mywin, start = (0,0),end = (0,0),lineColor = 'black')
trial_timer    = core.Clock()
gap_timer      = core.Clock()

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


dfs_2 = []
cond_i = 0

for rep in range(reps):
    for shift in shift_size:
        for dir_ch in dir_change:
            cond_i = cond_i + 1
            trial_goal_dis   = goal_distance
            trial_speed      = speed
            trial_ball       = ball_start
            trial_goal_size  = goal_size
            trial_jitter     = np.random.choice(jitter_time,1)[0]
            if cond_i%3 == 0:
                shift = -5
            trial_shift      = shift
            
            df = pd.DataFrame(data = [[cond_i,trial_speed,trial_ball,trial_goal_dis,trial_goal_size,trial_jitter,dir_ch, trial_shift]], columns = ['trial','speed','ball_pos','distance','broad','jitter','gap_time', 'shift_pos'])
            dfs_2.append(df)

# arrange in blocks

blocks = []
repl   = shift_size[0]
repl_by= shift_size[1]


for block in range (nblock):
    if block == 1:
        matrix = dfs_2
    else:
        matrix = dfs
    np.random.shuffle(matrix)
    for trial in range(ntrials):
        df_temp = matrix[trial]
        df_temp['trial_nr'] = trial+1
        dfs[trial]  = df_temp
    block_temp = pd.concat(matrix)
    block_temp['block']= block
    
    blocks.append(block_temp)

full_df       = pd.concat(blocks)

# save design 
full_df.to_csv(path_to_dat + exp + 'des' + filename + session + ".txt",sep='\t', encoding='utf-8', index = False)

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

def ask_for_text(intro):
    
    inputText = ''
    mykb.getEvents()
    continueRoutine = True
    mykb.reporting = True
    
    while continueRoutine:
        
        visual.TextStim(win = mywin, text = intro, pos = (0,0)).draw()
        visual.TextStim(win = mywin, text = (inputText), pos = (0,-2)).draw()
        mywin.flip()
        
        for kb_event in mykb.getEvents():
            
            if kb_event.type == 22:
                
                if kb_event.key == 'return':
                    # pressing RETURN means time to stop
                    continueRoutine = False
                    break
                elif kb_event.key == 'backspace':
                    inputText = inputText[:-1]
                    
                elif kb_event.key == 'space':
                    inputText += ' '
                else:
                    if len(kb_event.char) == 1:
                        # we only have 1 char so should be a normal key, 
                        # otherwise it might be 'ctrl' or similar so ignore it
                        inputText += kb_event.char
    mykb.reporting = False
    return inputText

def show_menue():
    go      = False
    LNDW    = True
    pressed = False
    visual.TextStim(win = mywin,text = 'Willst Du ein Spiel spielen? Dann drücke \'g\' und es geht los!', pos = (0,0)).draw()
    mywin.flip()
    mykb.reporting = True
    player_name    = ''
    age            = ''
    
    while not pressed:
        for kb_event in mykb.getEvents():
            if kb_event.char == 'g':
                player_name = ask_for_text('Cool! Wer spielt denn?')
                age  = ask_for_text('Und wie alt bist Du, %s?' %(player_name))
                go = True
                pressed = True
            if kb_event.key == 'return':
                LNDW = False
                pressed = True
    return go, LNDW, player_name, age
    

def play_again():
    mywin.flip()
    resp = False
    visual.TextStim(win = mywin,text = 'Willst Du nochmal spielen? Dann drücke \'j\' (ja) oder \'n\' (nein)', pos = (0,0)).draw()
    mywin.flip()
    mykb.reporting = True
    while not resp:
        for kb_event in mykb.getEvents():
            if kb_event.char == 'n':
                visual.TextStim(win = mywin,text = 'War schön mit Dir! Tschüss!', pos = (0,0)).draw()
                mywin.flip()
                go = False
                resp = True
            if kb_event.char == 'j':
                visual.TextStim(win = mywin,text = 'Cool, dann nochmal!', pos = (0,0)).draw()
                mywin.flip()
                go = True
                resp = True
    return go


#################################
#### Single Trial Function ######
#################################

def play_trial(mywin , trial_data, trial_id, player_name,player_age):
    '''
    serial presentation of stimuli with given parameter, monitor timing
    returns information about participant behaviour
    '''
    
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
    
    keys = mykb.waitForKeys(keys = ['b'])
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
                    feedback(0.5, 'Gut gemacht!','+5')
                    score = 5
                if correct == 0:
                    feedback(0.5, 'Daneben...','0')
                if correct == 'na':
                    feedback(0.5, 'Zu langsam!!','-10')
                    score = -10
                mykb.reporting = False
                goal_reached   = True
            
            if last_rescue.getTime()>0:
                goal_reached   = True
                
        break
    resp_data = pd.DataFrame(data = [[keypress,trial_id+1,t_start,t_set, t_ball, t_release, t_response, t_goal, t_change, new_pos, correct, player_name, player_age]], columns = ['response','trial_nr','t_start','t_set','t_ball','t_release','t_response','t_goal','t_change','new_pos','correct','name','age'])
    
    core.wait(0.5)
    
    return resp_data, score

# define a function that gets the trial information and plays alls trial in a row
# play all trials in a block

def play_block(full_df, block_id,player_name,player_age,rank):
    
    responses = []
    # play all trials in one block
    # initialize data frame
    block_data = full_df.query('block == %s' %(block_id))
    trial_number = len(block_data)
    block_score  = 0
    io.clearEvents('all')

    for trial in range(trial_number):
        trial_data = block_data.query('trial_nr == %s'%(trial+1))
        # play trials and get the pressed keys
        resp_dat, score   = play_trial(mywin,trial_data,trial,player_name,player_age)
        responses.append(resp_dat)
        
        block_score = block_score + score
        # clear screen after trial is played
        mywin.flip()
        core.wait(0.5)
    all_responses = pd.concat(responses)
    rank.append(block_score)
    rank.sort(reverse = True)
    feedback(1.5, 'Deine Punkte: %s' %(block_score),' ')
    feedback(1.5, 'Du bist auf Platz {} von {}'.format(int(np.mean(rank.index(block_score))+1),(len(rank))), ' ')
    # make data available
    return all_responses,rank


# Run the entire experiment
def play_experiment(blockn):
    # initialize data frame
    LNDW = True
    rank = []
    
    while LNDW:
        #clear screen
        mywin.flip()
        go, LNDW, player_name, age = show_menue()
        
        data = []
        
        while go:
            # for all blocks in the experiment
            for block in range(blockn):
                
                if block == 0:
                    # define the parameters based on the design matrix
                    mykb.reporting = True
                    visual.TextStim(win = mywin,text = 'Cool, los geht\'s! Wir spielen ein Torwart-Spiel. Mit \'g\' geht es weiter.', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = 'Um im Spiel den Torwart zu plazieren, drücke \' b\'. Dann beginnt die Runde.', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = 'Ein Ball bewegt sich dann auf das Tor zu, der zu einem zufälligen Zeitpunkt nach links oder rechts springt.', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = 'Mit den Tasten \' v\' und \'n\' bewegst du den Torwart nach links und rechts.', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = '5 Punkte gibt es, wenn du den Ball fängst, 0 Punkte, wenn du dich in die falsche Richtung bewegst und -10 Punkte, wenn du zu langsam bist.', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = 'Achtung! Der Ball springt manchmal erst sehr spät. Denke daran: Eine falsche Antwort (0 Punkte) ist besser als keine Antwort (-10 Punkte).', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = 'Fertig?', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = 'Los!', pos = (0,0)).draw()
                if block == 1:
                    mykb.reporting = True
                    visual.TextStim(win = mywin,text = 'Wir versuchen es nochmal - gleiches Spiel, aber der Ball springt jetzt öfter nach links als nach rechts.', pos = (0,0)).draw()
                    mywin.flip()
                    mykb.waitForKeys(keys = ['g'],etype = mykb.KEY_PRESS)
                    visual.TextStim(win = mywin,text = 'Viel Spaß!', pos = (0,0)).draw()
                    mywin.flip()
                io.clearEvents('all')
                mykb.getKeys(clear=True)
                mykb.reporting = False
                mywin.flip()
                core.wait(0.5)
                
                # play all blocks
                block_data,rank = play_block(full_df,block,player_name,age,rank)
                data.append(block_data)
                
                # clear screen after block is over and wait a little bit
                mywin.flip()
                core.wait(3.0)
            complete_data       = pd.concat(data)
            
            str_data            = complete_data.to_string()
            

            with open("backup.txt", "a") as myfile:
                myfile.write(str_data)
            
            go = play_again()
            
    return complete_data


# Play the experiment:
response_data = play_experiment(nblock)
response_data.to_csv(data_file, sep ='\t', encoding = 'utf-8', index = False)

# end and close after 3 secs
core.wait(1.0)
mywin.saveFrameIntervals(fileName = path_to_dat + '/' + 'framtime.log', clear = True)
mywin.close()

io.quit()
core.quit()