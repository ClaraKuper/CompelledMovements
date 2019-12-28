function [trialData,dataLog]  = runSingleTrial(t,b)
    
    global design visual settings
    
    trial = design.b(b).trial(t); 

    Datapixx('SetTouchpixxLog');                                    % Configure TOUCHPixx logging with default buffer
    Datapixx('EnableTouchpixxLogContinuousMode');                   % Continuous logging during a touch. This also gives you long output from buffer reads
    Datapixx('StartTouchpixxLog');


    % Prepare the trial
    jumpPos     = visual.ballPos_start + [0,trial.jumpPos];
    pos_at_jump = [visual.goals(trial.goalPos,1),jumpPos(2)];

    % Assign ball position to be at start
    ballPos = visual.ballPos_start;
    fixPos  = visual.fixPos;

    % Initialize timing and monitoring parameters

    on_fix       = false;
    jumped       = false;
    hit_target   = false;
    fix_released = false;

    % timing
    t_draw     = NaN;  % the stimulus was on screen
    t_touched  = NaN;  % the ball was touched
    t_go       = NaN;  % the ball started moving
    t_movStart = NaN;  % the movement started
    t_movEnd   = NaN;  % the movements ended
    t_goal     = NaN;  % the ball reached the goal
    
    % dataLog - write all the available logging data here
    Datapixx('RegWrRd');
    status             = Datapixx('GetTouchpixxStatus');
    [touches,timetag]  = Datapixx('ReadTouchpixxLog');
    dataLog.timetag    = timetag;
    dataLog.touches    = touches;
    dataLog.message    = ['Data Log initiated', Datapixx('GetTime')];


    % Run the trial. Display the goal and a moving ball
    Screen('DrawDots', visual.window, visual.goals(1,:), visual.goalSize, visual.goalColor, [], 2);
    Screen('DrawDots', visual.window, visual.goals(2,:), visual.goalSize, visual.goalColor, [], 2);
    Screen('DrawDots', visual.window, ballPos, visual.ballSize, visual.ballColor, [], 2);
    Screen('DrawLine', visual.window, visual.goalColor, fixPos(1)-50 , fixPos(2), fixPos(1) +50, fixPos(2));
    t_draw = Screen('Flip', visual.window);

    % while the finger is not yet on the starting position, monitor for that
    while ~ on_fix
        Datapixx('RegWrRd');
        status = Datapixx('GetTouchpixxStatus');
        
        if isfield(status, 'newLogFrames') && status.newLogFrames > 0  % We have new TOUCHPixx logged data to read?
            [touches, timetag] = Datapixx('ReadTouchpixxLog');
            dataLog.touches    = [dataLog.touches,touches];
            dataLog.timetag    = [dataLog.timetag, timetag];
            touch_X = visual.mx*touches(1,status.newLogFrames)+visual.bx;
            touch_Y = visual.my*touches(2,status.newLogFrames)+visual.by;
            if touch_X > fixPos(1) - visual.range_accept && touch_X < fixPos(1) + visual.range_accept && ...
                    touch_Y > fixPos(2) - visual.range_accept && ...
                    touch_Y < fixPos(2) + visual.range_accept
                on_fix = true;
                t_touched   = timetag(status.newLogFrames);
                dataLog.message = [dataLog.message, ['The fixation point was touched', Datapixx('GetTime')]];
                WaitSecs(trial.fixT);
            end
            Screen('DrawDots', visual.window, visual.goals(1,:), visual.goalSize, visual.goalColor, [], 2);
            Screen('DrawDots', visual.window, visual.goals(2,:), visual.goalSize, visual.goalColor, [], 2);
            Screen('DrawDots', visual.window, ballPos, visual.ballSize, visual.ballColor, [], 2);
            Screen('DrawLine', visual.window, visual.goalColor, fixPos(1)-50 , fixPos(2), fixPos(1) +50, fixPos(2));
            Screen('Flip', visual.window);
        end
    end;

    % the jumping location is not reached, run down
    while on_fix && isnan(t_goal)
        if isnan(t_go)
            Datapixx('RegWrRd');
            t_go = Datapixx('GetTime');
            dataLog.message = [dataLog.message, ['The motion started', Datapixx('GetTime')]];
        end
        Datapixx('RegWrRd');
        if Datapixx('GetTime')-t_go < trial.jumpTim || jumped
            ballPos = ballPos+[0,design.move_at_speed];
        else
            ballPos = pos_at_jump;
            jumped  = true;
            dataLog.message = [dataLog.message, ['The ball jumped', Datapixx('GetTime')]];
        end

        Screen('DrawDots', visual.window, visual.goals(1,:), visual.goalSize, visual.goalColor, [], 2);
        Screen('DrawDots', visual.window, visual.goals(2,:), visual.goalSize, visual.goalColor, [], 2);
        Screen('DrawDots', visual.window, ballPos, visual.ballSize, visual.ballColor, [], 2);
        Screen('DrawLine', visual.window, visual.goalColor, fixPos(1)-50 , fixPos(2), fixPos(1) +50, fixPos(2));
        Screen('Flip', visual.window);
        
        % Get the touchpixx status
        Datapixx('RegWrRd');
        status = Datapixx('GetTouchpixxStatus');

        if status.newLogFrames                                              % something new happened
            [touches, timetag] = Datapixx('ReadTouchpixxLog');
            dataLog.touches    = [dataLog.touches,touches];
            dataLog.timetag    = [dataLog.timetag, timetag];
            touch_X = visual.mx*touches(1,status.newLogFrames)+visual.bx;   % we want the coordinates from the first time the target has been touched
            touch_Y = visual.my*touches(2,status.newLogFrames)+visual.by;
            fixPos  = [touch_X,touch_Y];
            % check if movement started
            if isnan(t_movStart) && touch_X < visual.fixPos(1) - visual.range_accept || ...
                    isnan(t_movStart) && touch_X > visual.fixPos(1) + visual.range_accept ||...
                    isnan(t_movStart) && touch_Y < visual.fixPos(2) - visual.range_accept ||...
                    isnan(t_movStart) && touch_Y > visual.fixPos(2) + visual.range_accept
                    
                t_movStart = timetag(status.newLogFrames);
                Datapixx('RegWrRd');
                dataLog.message = [dataLog.message, ['The hand moved', Datapixx('GetTime')]];
            
            elseif touch_X > visual.goals(trial.goalPos,1) - visual.range_accept && ...
                    touch_X < visual.goals(trial.goalPos,1) + visual.range_accept &&...
                    touch_Y > visual.goals(trial.goalPos,2) - visual.range_accept &&...
                    touch_Y < visual.goals(trial.goalPos,2) + visual.range_accept
               t_movEnd  = timetag(status.newLogFrames);                    % we want a time tag when the target was touched for the first time
               Datapixx('RegWrRd');
               dataLog.message = [dataLog.message, ['The hand reached the target', Datapixx('GetTime')]];
               hit_target = true;
            end
            
         if ballPos(2) >= visual.goals(trial.goalPos,2)
             Datapixx('RegWrRd');
             t_goal   = Datapixx('GetTime');
             dataLog.message = [dataLog.message, ['The ball hit the target', Datapixx('GetTime')]];
         end
         
        end
    end
    
    Datapixx('RegWrRd');
    dataLog.message = [dataLog.message, ['Trial End', Datapixx('GetTime')]];
    Datapixx('StopTouchpixxLog');  

    rea_time = t_movStart - t_go;
    mov_time = t_movEnd - t_movStart; 
    
    % present feedback
    if rea_time > design.alResT
        DrawFormattedText(visual.window, 'Reaction to slow!', 'center', 'center', visual.textCol);
    elseif isnan(rea_time)
        DrawFormattedText(visual.window, 'Do not wait at the start.', 'center', 'center', visual.textCol);
    elseif mov_time > design.alMovT
        DrawFormattedText(visual.window, 'Move faster!', 'center', 'center', visual.textCol);
    elseif hit_target 
        DrawFormattedText(visual.window, 'Well done!', 'center', 'center', visual.textCol);
    else
        DrawFormattedText(visual.window, 'Target was missed!', 'center', 'center', visual.textCol);
    end

    if settings.DEBUG == 1
        %Screen('FrameRect', visual.window, visual.white, [visual.goals(trial.goalPos,1) - visual.range_accept, ...
        %    visual.goals(trial.goalPos,1) + visual.range_accept,...
        %    visual.goals(trial.goalPos,2) - visual.range_accept,...
        %    visual.goals(trial.goalPos,2) + visual.range_accept])
        Screen('DrawDots', visual.window, [touch_X, touch_Y], visual.ballSize, visual.white)
    end

    Screen('Flip', visual.window);
    WaitSecs(1)
    
    trialData.rea_time        = rea_time;
    trialData.mov_time        = mov_time;
    trialData.t_draw          = t_draw;
    trialData.t_touched       = t_touched;
    trialData.t_go            = t_go;
    trialData.t_movStart      = t_movStart;
    trialData.t_movEnd        = t_movEnd;
    trialData.t_goal          = t_goal;
    
    WaitSecs(design.iti);
end