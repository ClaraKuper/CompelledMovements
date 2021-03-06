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
global settings visual design

settings.TEST = 0;
settings.MODE = 1; % 1 = Hands, 2 = Eyes

%% start the experiment loop, errors in this loop will be caught
try
    newFile = 0;
        while ~newFile
            if ~settings.TEST
                subCode = getID(expCode);
            else
                subCode = '##';
            end
            subPath = strcat('Data/',subCode);

            % create data file
            datFile = sprintf('%s.dat',subPath);
            if ~settings.TEST && exist(datFile,'file')
                o = input('>>>> This file exists already. Should I overwrite it [y / n]? ','s');
                if strcmp(o,'y')
                    newFile = 1;
                end
            else
                newFile = 1;
            end
        end
        
    setScreens
    
                                                                                
    % generate design 
    genDesign(subCode);

    % Add experiment Info after OpenWindow so it's under the text generated by Screen
    fprintf('\nTOUCHPixx Basic Demo\n');

    % For testing: do we want continuous logging?:
    include_continuous = true;

    % Configure DATAPixx/TOUCHPixx
    Datapixx('SetVideoMode', 0);                        % Normal passthrough
    Datapixx('EnableTouchpixx');                        % Turn on TOUCHPixx hardware driver
    Datapixx('SetTouchpixxStabilizeDuration', 0.01);    % stable coordinates in secs before recognising  touch
    Datapixx('RegWrRd');
    
    calibrate_touchpixx();

    
    %% Run trials
    % Display Instructions:
    DrawFormattedText(visual.window, 'Touch the ball to start. Hit the target when the ball moves.', 'center', 200, visual.textCol);
    Screen('Flip',visual.window)
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
            jumpPos     = visual.ballPos_start + [0,trial.jumpPos];
            pos_at_jump = [visual.goals(trial.goalPos,1),jumpPos(2)];

            % Assign ball position to be at start
            ballPos = visual.ballPos_start;

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
            Screen('DrawDots', visual.window, visual.goals(1,:), visual.goalSize, visual.goalColor, [], 2);
            Screen('DrawDots', visual.window, visual.goals(2,:), visual.goalSize, visual.goalColor, [], 2);
            Screen('DrawDots', visual.window, ballPos, visual.ballSize, visual.ballColor, [], 2);
            Screen('Flip', visual.window);
            t_draw = Datapixx('GetTime');

            % while the finger is not yet on the starting position, monitor for
            % that
            while ~ on_ball
                Datapixx('RegWrRd');
                status = Datapixx('GetTouchpixxStatus');
                if include_continuous && isfield(status, 'newLogFrames') && status.newLogFrames > 0  % We have new TOUCHPixx logged data to read?
                    [touches, timetag] = Datapixx('ReadTouchpixxLog',status.newLogFrames);
                    touch_X = visual.mx*touches(1)+visual.by;
                    touch_Y = visual.my*touches(2)+visual.by;
                    if touch_X > ballPos(1) - visual.range_accept && touch_X < ballPos(1) + visual.range_accept && ...
                            touch_Y > ballPos(2) - visual.range_accept && ...
                            touch_Y < ballPos(2) + visual.range_accept
                        Screen('DrawDots', visual.window, visual.goals(1,:), goalSize, goalColor, [], 2);
                        Screen('DrawDots', visual.window, visual.goals(2,:), goalSize, goalColor, [], 2);
                        Screen('DrawDots', visual.window, ballPos, ballSize, ballColor, [], 2);
                        Screen('Flip', visual.window);
                        on_ball = true;
                        t_touched   = timetag(status.newLogFrames);
                        WaitSecs(trial.fixT)
                    end
                end
            end;

            t_go = Datapixx('GetTime');
            Datapixx('SetMarker');

            % the jumping location is not reached, run down
            while on_ball && ballPos(2) < visual.goals(trial.goalPos,2) 
                if ballPos(2) < jumpPos(2) || jumped
                    ballPos = ballPos+[0,move_at_speed];
                else
                    ballPos = pos_at_jump;
                    jumped  = true;
                end

                Screen('DrawDots', visual.window, visual.goals(1,:), goalSize, goalColor, [], 2);
                Screen('DrawDots', visual.window, visual.goals(2,:), goalSize, goalColor, [], 2);
                Screen('DrawDots', visual.window, ballPos, ballSize, ballColor, [], 2);
                Screen('Flip', visual.window);        

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
                    touch_X = visual.mx*touches(1,1)+visual.by;                               % we want the coordinates from the first time the target has been touched
                    touch_Y = visual.my*touches(2,1)+visual.by;
                    if touch_X > visual.goals(trial.goalPos,1) - visual.range_accept && ...
                            touch_X < visual.goals(trial.goalPos,1) + visual.range_accept &&...
                            touch_Y > visual.goals(trial.goalPos,2) - visual.range_accept &&...
                            touch_Y < visual.goals(trial.goalPos,2) + visual.range_accept
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
                if mov_time > design.alMovT
                    DrawFormattedText(visual.window, 'Do not hover in the air!', 'center', 'center', visual.textCol);
                else
                    DrawFormattedText(visual.window, 'Well done!', 'center', 'center', visual.textCol);
                end
            else
                DrawFormattedText(visual.window, 'Target was missed!', 'center', 'center', visual.textCol);
            end

            Screen('Flip', visual.window);
            data.b(b).trial(t).rea_time        = rea_time;
            data.b(b).trial(t).rea_time_alt    = rea_time_alt;
            data.b(b).trial(t).rea_time_marker = rea_time_marker;
            data.b(b).trial(t).mov_time        = mov_time;
            WaitSecs(2)

        end
    end    
catch me
    rethrow(me);
    %reddUp; %#ok<UNRCH>
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