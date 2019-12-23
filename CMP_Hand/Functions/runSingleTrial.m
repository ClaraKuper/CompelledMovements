function trialData = runSingleTrial(t,b)
    
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

    % Initialize timing and monitoring parameters

    on_ball    = false;
    jumped     = false;
    hit_target = false;
    fix_released = false;

    % timing
    t_draw     = NaN;  % the stimulus was on screen
    t_touched  = NaN;  % the ball was touched
    t_go       = NaN;  % the ball started moving
    t_movStart = NaN;  % the movement started
    t_movEnd   = NaN;  % the movements ended
    t_goal     = NaN;  % the ball reached the goal


    % Run the trial. Display the goal and a moving ball
    Screen('DrawDots', visual.window, visual.goals(1,:), visual.goalSize, visual.goalColor, [], 2);
    Screen('DrawDots', visual.window, visual.goals(2,:), visual.goalSize, visual.goalColor, [], 2);
    Screen('DrawDots', visual.window, ballPos, visual.ballSize, visual.ballColor, [], 2);
    t_draw = Screen('Flip', visual.window);

    % while the finger is not yet on the starting position, monitor for that
    while ~ on_ball
        Datapixx('RegWrRd');
        status = Datapixx('GetTouchpixxStatus');
        
        if isfield(status, 'newLogFrames') && status.newLogFrames > 0  % We have new TOUCHPixx logged data to read?
            [touches, timetag] = Datapixx('ReadTouchpixxLog',status.newLogFrames);
            touch_X = visual.mx*touches(1)+visual.bx;
            touch_Y = visual.my*touches(2)+visual.by;
            if touch_X > ballPos(1) - visual.range_accept && touch_X < ballPos(1) + visual.range_accept && ...
                    touch_Y > ballPos(2) - visual.range_accept && ...
                    touch_Y < ballPos(2) + visual.range_accept
                on_ball = true;
                t_touched   = timetag(status.newLogFrames);
                Screen('DrawDots', visual.window, visual.goals(1,:), visual.goalSize, visual.goalColor, [], 2);
                Screen('DrawDots', visual.window, visual.goals(2,:), visual.goalSize, visual.goalColor, [], 2);
                Screen('DrawDots', visual.window, ballPos, visual.ballSize, visual.ballColor, [], 2);
                Screen('Flip', visual.window);
                WaitSecs(trial.fixT)
            end
        end
    end;

    % the jumping location is not reached, run down
    t_go = Datapixx('GetTime');
    while on_ball && ballPos(2) < visual.goals(trial.goalPos,2) 
        if Datapixx('GetTime')-t_go < trial.jumpTim || jumped
            ballPos = ballPos+[0,design.move_at_speed];
        else
            ballPos = pos_at_jump;
            jumped  = true;
        end

        Screen('DrawDots', visual.window, visual.goals(1,:), visual.goalSize, visual.goalColor, [], 2);
        Screen('DrawDots', visual.window, visual.goals(2,:), visual.goalSize, visual.goalColor, [], 2);
        Screen('DrawDots', visual.window, ballPos, visual.ballSize, visual.ballColor, [], 2);
        if isnan(t_go)
            t_go = Datapixx('GetTime');                                     % this timing should be more precise
        end
        Screen('Flip', visual.window);

        % Get the touchpixx status
        Datapixx('RegWrRd');
        status = Datapixx('GetTouchpixxStatus');

        if ~ status.isPressed && ~ fix_released
            % initialize the timer to reach the target
            [~, timetag] = Datapixx('ReadTouchpixxLog');
            t_movStart      = timetag(status.newLogFrames);                 % this assumes that the last time tag is when the screen has been released
            fix_released = true;
            Datapixx('RegWrRd');
            status = Datapixx('GetTouchpixxStatus');
        end

        if fix_released && status.isPressed && status.newLogFrames > 0 % fixation was released and something new was touched
            [touches, timetag] = Datapixx('ReadTouchpixxLog');
            touch_X = visual.mx*touches(1,1)+visual.bx;                               % we want the coordinates from the first time the target has been touched
            touch_Y = visual.my*touches(2,1)+visual.by;
            if touch_X > visual.goals(trial.goalPos,1) - visual.range_accept && ...
                    touch_X < visual.goals(trial.goalPos,1) + visual.range_accept &&...
                    touch_Y > visual.goals(trial.goalPos,2) - visual.range_accept &&...
                    touch_Y < visual.goals(trial.goalPos,2) + visual.range_accept
               t_movEnd  = timetag(1);                                 % we want a time tag when the target was touched for the first time
               hit_target = true;
            end
         if ballPos(2) <= visual.goals(trial.goalPos,2)
             t_goal   = Datapixx('GetTime');
         end
         
        end
    end

    Datapixx('StopTouchpixxLog');  

    rea_time = t_movStart - t_go;
    mov_time = t_movEnd - t_movStart; 
    
    % present feedback
    if rea_time > des.alReaT
        DrawFormattedText(visual.window, 'Reaction to slow!', 'center', 'center', visual.textCol);
    elseif isnan(rea_time)
        DrawFormattedText(visual.window, 'Do not keep the the target touched ', 'center', 'center', visual.textCol);
    elseif mov_time > design.alMovT
        DrawFormattedText(visual.window, 'Do not hover in the air!', 'center', 'center', visual.textCol);
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