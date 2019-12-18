% Basic TouchPixx Demo
% 2019 by Clara Kuper
% based on ptb demos by Peter Scarfe http://peterscarfe.com/ptbtutorials.html
% and vpixx demo 17 http://www.vpixx.com/manuals/psychtoolbox/html/Demo17.html

% System setup
% Clear the workspace and the screen
sca;
clear all;
clear mex;
clear functions;
% cursor goes home, command window scrolled up
home

% Which experiment are we running?
expCode = 'CMP_Hand';
sprintf('Now running experiment %s',expCode);

% add the functions folder to searchpath and define storage paths
addpath('Functions')

% Unify keys in case sb codes with a different system
KbName('UnifyKeyNames');

% Here we call some default settings for setting up Psychtoolbox

PsychDefaultSetup(2);

% Init random
rand('seed', sum(100 * clock));

%start a timer for the experiment
expStart = tic;

% define some settings for the experiment
global settings

settings.TEST = 0;
settings.MODE = 1; % 1 = Hands, 2 = Eyes

%% start the experiment loop, errors in this loop will be caught
try
    newFile = 0;
        while ~newFile
            if ~setting.TEST
                subCode = getID(expCode);
            else
                subCode = '##';
            end
            subPath = strcat('Data/',subCode);

            % create data file
            datFile = sprintf('%s.dat',subPath);
            if ~setting.TEST && exist(datFile,'file')
                o = input('>>>> This file exists already. Should I overwrite it [y / n]? ','s');
                if strcmp(o,'y')
                    newFile = 1;
                end
            else
                newFile = 1;
            end
        end
        
    setScreens
    
    % Open datapixx and init PsychImaging
    Datapixx('Open');                                                           %% Opens the Datapixx
    PsychImaging('PrepareConfiguration');
    %PsychImaging('AddTask', 'General', 'UseDataPixx');                         %% Would internally open the Datapixx a second time, ...
                                                                                % uses PSYNC that can crash with certain system settings
    % generate design 
    design = genDesign(vpcode);


    % Timing Parameters
    allowed_mov_time  = design.alMovT;
    allowed_resp_time = design.alResT;

    % Parameters for stimuli
    ball_moved       = -100; % shift of moving stim from centre, negative values above screen center
    distr_moved_side = 300; %how much are the non-targets moved sideways
    distr_moved_down = 300; %how much is the distractor moved down 

    ballPos_start   = [xCenter, yCenter] + [0, ball_moved];
    ballColor = white;
    ballSize  = 20;

    goalPos1  = [xCenter, yCenter] + [-distr_moved_side,distr_moved_down]; 
    goalPos2  = [xCenter, yCenter] + [distr_moved_side,distr_moved_down]; 
    goals     = [goalPos1;goalPos2];
    goalColor = white;
    goalSize  = ballSize;

    range_accept = 100;

    % when should the jump occur?
    % draw a random value between ball_moved and distr_moved_down
    % in design: make a uniform distribution
    % full_distance = distr_moved_down - ball_moved;
    jump_after = 0;

    % how many pixels does the ball cross with each jump?
    move_at_speed = 5;

    % Add experiment Info after OpenWindow so it's under the text generated by Screen
    fprintf('\nTOUCHPixx Basic Demo\n');

    % For testing: do we want continuous logging?:
    include_continuous = true;

    % Configure DATAPixx/TOUCHPixx
    Datapixx('SetVideoMode', 0);                        % Normal passthrough
    Datapixx('EnableTouchpixx');                        % Turn on TOUCHPixx hardware driver
    Datapixx('SetTouchpixxStabilizeDuration', 0.01);    % stable coordinates in secs before recognising  touch
    Datapixx('RegWrRd');

    %% Calibration as in VPixx Demo 17
    % Put up first touch calibration target near top-left corner, and acquire TOUCHPixx coordinates
    calDispX1 = 100;
    calDispY1 = 100;
    calCol = [255 255 255];
    Screen('FillRect', window, calCol, [calDispX1-25 calDispY1-25 calDispX1+25 calDispY1+25]);
    textCol = [0.5 0.5 0.5];
    Screen('TextFont',window, 'Courier New');
    Screen('TextSize',window, floor(50 * winWidth/1920));
    DrawFormattedText(window, 'Touch center of first calibration square', 'center', 'center', textCol);
    Screen('Flip', window);
    touchPt = [0 0];                        % Wait for press
    while touchPt == [0 0]
        Datapixx('RegWrRd');
        touchPt = Datapixx('GetTouchpixxCoordinates');
    end;
    calTouchX1 = touchPt(1);
    calTouchY1 = touchPt(2);
    Screen('Flip', window);

    isPressed = 1;                          % Wait until panel release
    while isPressed
        Datapixx('RegWrRd');
        status =  Datapixx('GetTouchpixxStatus');
        isPressed = status.isPressed;
    end;

    % Do same for a second calibration target near bottom-right corner of display
    calDispX2 = winWidth - 100;
    calDispY2 = winHeight - 100;
    Screen('FillRect', window, calCol, [calDispX2-25 calDispY2-25 calDispX2+25 calDispY2+25]);
    Screen('Flip', window);
    touchPt = [0 0];                        % Wait for press
    while touchPt == [0 0]
        Datapixx('RegWrRd');
        touchPt = Datapixx('GetTouchpixxCoordinates');
    end;
    calTouchX2 = touchPt(1);
    calTouchY2 = touchPt(2);
    Screen('Flip', window);
    isPressed = 1;                          % Wait until panel release
    while isPressed
        Datapixx('RegWrRd');
        status =  Datapixx('GetTouchpixxStatus');
        isPressed = status.isPressed;
    end;

    % Calculate linear mapping between touch coordinates and display coordinates
    mx = (calDispX2 - calDispX1) / (calTouchX2 - calTouchX1);
    my = (calDispY2 - calDispY1) / (calTouchY2 - calTouchY1);
    bx = (calTouchX1 * calDispX2 - calTouchX2 * calDispX1) / (calTouchX1 - calTouchX2);
    by = (calTouchY1 * calDispY2 - calTouchY2 * calDispY1) / (calTouchY1 - calTouchY2);

    %% Run trials
    % Display Instructions:
    DrawFormattedText(window, 'Touch the ball to start. Hit the target when the ball moves.', 'center', 200, textCol);
    Screen('Flip',window)
    WaitSecs(2)
    for b = 1 %:design(nBlocks)
        for t =  1:design.nTrialsPB
            trial = design.b(b).trial(t); 
            if include_continuous
                Datapixx('SetTouchpixxLog');                                    % Configure TOUCHPixx logging with default buffer
                Datapixx('EnableTouchpixxLogContinuousMode');                   % Continuous logging during a touch. This also gives you long output from buffer reads
                Datapixx('StartTouchpixxLog');
            end


            % Prepare the trial
            jumpPos     = ballPos_start + [0,trial.jumpPos];
            pos_at_jump = [goals(trial.goalPos,1),jumpPos(2)];

            % Assign ball position to be at start
            ballPos = ballPos_start;

            % Now we have drawn to the screen and we wait for the participant to
            % touch the ball to start.

            on_ball    = false;
            jumped     = false;
            hit_target = false;
            fix_released = false;

            % Set the reaction time to non available
            t_draw     = NaN; 
            t_touched  = NaN;
            t_go       = NaN;
            t_released = NaN;
            t_target   = NaN;


            % Run the trial. Display the goal and a moving ball
            Screen('DrawDots', window, goals(1,:), goalSize, goalColor, [], 2);
            Screen('DrawDots', window, goals(2,:), goalSize, goalColor, [], 2);
            Screen('DrawDots', window, ballPos, ballSize, ballColor, [], 2);
            Screen('Flip', window);
            t_draw = Datapixx('GetTime');

            % while the finger is not yet on the starting position, monitor for
            % that
            while ~ on_ball
                Datapixx('RegWrRd');
                status = Datapixx('GetTouchpixxStatus');
                if include_continuous && isfield(status, 'newLogFrames') && status.newLogFrames > 0  % We have new TOUCHPixx logged data to read?
                    [touches, timetag] = Datapixx('ReadTouchpixxLog',status.newLogFrames);
                    touch_X = mx*touches(1)+bx;
                    touch_Y = my*touches(2)+by;
                    if touch_X > ballPos(1) - range_accept && touch_X < ballPos(1) + range_accept && ...
                            touch_Y > ballPos(2) - range_accept && ...
                            touch_Y < ballPos(2) + range_accept
                        Screen('DrawDots', window, goals(1,:), goalSize, goalColor, [], 2);
                        Screen('DrawDots', window, goals(2,:), goalSize, goalColor, [], 2);
                        Screen('DrawDots', window, ballPos, ballSize, ballColor, [], 2);
                        Screen('Flip', window);
                        on_ball = true;
                        t_touched   = timetag(status.newLogFrames);
                        WaitSecs(trial.fixT)
                    end
                end
            end;

            t_go = Datapixx('GetTime');
            Datapixx('SetMarker');

            % the jumping location is not reached, run down
            while on_ball && ballPos(2) < goals(trial.goalPos,2) 
                if ballPos(2) < jumpPos(2) || jumped
                    ballPos = ballPos+[0,move_at_speed];
                else
                    ballPos = pos_at_jump;
                    jumped  = true;
                end

                Screen('DrawDots', window, goals(1,:), goalSize, goalColor, [], 2);
                Screen('DrawDots', window, goals(2,:), goalSize, goalColor, [], 2);
                Screen('DrawDots', window, ballPos, ballSize, ballColor, [], 2);
                Screen('Flip', window);        

                % Get the touchpixx status
                Datapixx('RegWrRd');
                status = Datapixx('GetTouchpixxStatus');

                if ~ status.isPressed && ~ fix_released
                    % initialize the timer to reach the target
                    [touches, timetag] = Datapixx('ReadTouchpixxLog',status.newLogFrames);
                    t_release      = timetag(status.newLogFrames);
                    t_release_alt  = timetag(1);
                    t_release_mark = Datapixx('GetMarker');
                    % fprintf('\nfixation was released at %f\n', t_release);
                    fix_released = true;
                    Datapixx('RegWrRd');
                    status = Datapixx('GetTouchpixxStatus');
                end

                if include_continuous && fix_released && status.isPressed % fixation was released and something new was touched
                    [touches, timetag] = Datapixx('ReadTouchpixxLog',status.newLogFrames);
                    fprintf('\nsomething was touched\n')
                    touch_X = mx*touches(1,1)+bx;                               % we want the coordinates from the first time the target has been touched
                    touch_Y = my*touches(2,1)+by;
                    if touch_X > goals(trial.goalPos,1) - range_accept && ...
                            touch_X < goals(trial.goalPos,1) + range_accept &&...
                            touch_Y > goals(trial.goalPos,2) - range_accept &&...
                            touch_Y < goals(trial.goalPos,2) + range_accept
                       t_target  = timetag(1);                                 % we want a time tag when the target was touched for the first time
                       hit_target = true;
                       fprintf('\ntarget was hit at %f \n', t_target)
                       break
                    end
                end
            end

            if include_continuous
                Datapixx('StopTouchpixxLog');  
            end

            rea_time = t_release - t_go;
            rea_time_alt = t_release_alt-t_go;
            rea_time_marker = t_release_mark;
            mov_time = t_target - t_release; 
            % present feedback
            if hit_target
                if mov_time > allowed_mov_time
                    DrawFormattedText(window, 'Do not hover in the air!', 'center', 'center', textCol);
                else
                    DrawFormattedText(window, 'Well done!', 'center', 'center', textCol);
                end
            else
                DrawFormattedText(window, 'Target was missed!', 'center', 'center', textCol);
            end

            Screen('Flip', window);
            data.b(b).trial(t).rea_time        = rea_time;
            data.b(b).trial(t).rea_time_alt    = rea_time_alt;
            data.b(b).trial(t).rea_time_marker = rea_time_marker;
            data.b(b).trial(t).mov_time        = mov_time;
            WaitSecs(2)

        end
    end    
catch me
    rethrow(me);
    reddUp; %#ok<UNRCH>
end
    
% Clear the screen. "sca" is short hand for "Screen CloseAll". This clears
% all features related to PTB. Note: we leave the variables in the
% workspace so you can have a look at them if you want.
% For help see: help sca
if design.test
    save(sprintf('%s_data.mat',design.vpcode),'data');
else
    save(sprintf('%s_timParams',design.vpcode),'data');
end

Datapixx('DisableTouchpixx');
sca;

Datapixx('Close'); %call the close command after closing the screens