function calibrate_touchpixx (reps)
    
    if nargin < 1
        reps = 3;
    end

    %% Calibration with validation
    % set the points, get a calibration on the same screen, ask if calibration was accepted or not  
    %% Calibration as in VPixx Demo 17
    % Put up first touch calibration target near top-left corner, and acquire TOUCHPixx coordinates
    global visual

    % define locations for touch targets
    % upper left
    calDispX1 = 100;
    calDispY1 = 100;
    % lower right 
    calDispX2 = visual.winWidth - 100;
    calDispY2 = visual.winHeight - 100;
   

    % settings for text display 
    Screen('TextFont',visual.window, 'Courier New');
    Screen('TextSize',visual.window, floor(50 * visual.winWidth/1920));

    % color of calibration targets like color of stimuli
    calCol  = visual.white;
    
    calibration_done = false;
    
    while ~calibration_done
        DrawFormattedText(visual.window, 'Please touch the center of calibration square', 'center', 'center', visual.textCol);
        Screen('Flip', visual.window);
        WaitSecs(1)
        
        for rep = 1:reps
            
            Screen('FillRect', visual.window, calCol, [calDispX1-visual.range_accept calDispY1-visual.range_accept...
                calDispX1+visual.range_accept calDispY1+visual.range_accept]);
            Screen('Flip', visual.window);

            touchPt = [0 0];  % Wait for press
            while touchPt == [0 0]
              Datapixx('RegWrRd');
              touchPt = Datapixx('GetTouchpixxCoordinates');
            end;
            touch.calTouchX.upleft(rep) = touchPt(1);
            touch.calTouchY.upleft(rep) = touchPt(2);
            Screen('Flip', visual.window);

            isPressed = 1;                          % Wait until panel release
            while isPressed
              Datapixx('RegWrRd');
              status =  Datapixx('GetTouchpixxStatus');
              isPressed = status.isPressed;
            end;

            % Do same for a second calibration target near bottom-right corner of display

            Screen('FillRect', visual.window, calCol, [calDispX2-visual.range_accept calDispY2-visual.range_accept...
                calDispX2+visual.range_accept calDispY2+visual.range_accept]);
            Screen('Flip', visual.window);
            touchPt = [0 0];                        % Wait for press
            while touchPt == [0 0]
              Datapixx('RegWrRd');
              touchPt = Datapixx('GetTouchpixxCoordinates');
            end;
            touch.calTouchX.lowright(rep) = touchPt(1);
            touch.calTouchY.lowright(rep) = touchPt(2);
            Screen('Flip', visual.window);
            isPressed = 1;                          % Wait until panel release
            while isPressed
              Datapixx('RegWrRd');
              status =  Datapixx('GetTouchpixxStatus');
              isPressed = status.isPressed;
            end;
        end
        if std(touch.calTouchX.lowright) < visual.range_accept/100 ...
                && std(touch.calTouchY.lowright) < visual.range_accept/100 ...
                && std(touch.calTouchX.upleft) < visual.range_accept/100 ...
                && std(touch.calTouchX.upleft) < visual.range_accept/100
            calibration_done = true;
            DrawFormattedText(visual.window, 'Calibration was successful', visual.textCol);
            calTouchX1 = mean(touch.calTouchX.upleft);
            calTouchY1 = mean(touch.calTouchX.upleft);
            calTouchX2 = mean(touch.calTouchX.lowright);
            calTouchY2 = mean(touch.calTouchX.lowright);
            sprintf('std(touch.calTouchX.lowright)= %i \nstd(touch.calTouchY.lowright) = %i \nstd(touch.calTouchX.upleft) = %i \nstd(touch.calTouchX.upleft) = %i', ...
                std(touch.calTouchX.lowright), std(touch.calTouchY.lowright), std(touch.calTouchX.upleft), std(touch.calTouchX.upleft))
        else
            DrawFormattedText(visual.window, 'Calibration will be repeated', visual.textCol);
        end
         Screen('Flip', visual.window);
         WaitSecs(1)
    end
    
    

    % Calculate linear mapping between touch coordinates and display coordinates
    visual.mx = (calDispX2 - calDispX1) / (calTouchX2 - calTouchX1);
    visual.my = (calDispY2 - calDispY1) / (calTouchY2 - calTouchY1);
    visual.bx = (calTouchX1 * calDispX2 - calTouchX2 * calDispX1) / (calTouchX1 - calTouchX2);
    visual.by = (calTouchY1 * calDispY2 - calTouchY2 * calDispY1) / (calTouchY1 - calTouchY2);
end