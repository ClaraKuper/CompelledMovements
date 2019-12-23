function blockData = runBlock(b)

    global visual design
    message = sprintf('This is block no. %i', b);
    DrawFormattedText(visual.window, message, 'center', 200, visual.textCol);
    Screen('Flip',visual.window)
    WaitSecs(2)
    
    for t =  1:design.nTrialsPB
        
        blockData.trial(t) = runSingleTrial(t,b);
        
    end
    
    Screen('Flip', visual.window);
    WaitSecs(2);
end
