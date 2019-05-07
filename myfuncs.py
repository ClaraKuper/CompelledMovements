# get participant data
def get_data():
    '''
    Function calls GUI, asks for data, defines name for data file 
    and checks if the file already exists.
    
    Returns the name of the data file.
    '''
    from psychopy import gui
    import os 
    
    while True:
        info = {'Participant':'Your Code','Experiment':'CompelledMovements','Session_No':0}
        infoDlg = gui.DlgFromDict(dictionary = info, title = 'participant data', fixed = ['Experiment'])
        
        name = info['Participant']
        session = str(info['Session_No'])
        # input file
        data_file = name + session + '.txt'
        
        if os.path.isfile(data_file):
            pass
        else: 
            break
            
    return data_file, name, session



def join_data_file(data,data_file):
    '''
    writes information to fila - can be done for data and design
    '''
    # is there already a data file?
    if os.path.isfile(data_file):
        old_data = pd.read_csv(data_file, sep = '\t')
        data     = pd.concat([old_data,data])
    else:
        pass
    # 
    return data


# define a range function for decimals
def drange(x,y,jump):
    out = []
    while x < y:
        out.append(x)
        x = x+jump
    return out


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

def block_intro(nblock):
    from psychopy import visual
    
    write = "Block %s" %(nblock+1)
    visual.TextStim(win = mywin,text = write, pos = (0,0)).draw()