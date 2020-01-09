function [blockData,dataLog] = runBlock(b)

    global visual design
    message = sprintf('This is block no. %i', b);
    DrawFormattedText(visual.window, message, 'center', 200, visual.textCol);
    trials_total = design.nTrialsPB;
    t            = 1;
    
    Screen('Flip',visual.window);
    WaitSecs(2);
    
    while t <=  trials_total
        
        trial = design.b(b).trial(t); 
        
        [blockData.trial(t),dataLog.trial(t)] = runSingleTrial(trial);
        
        if blockData.trial(t).success
            
            trials_total                    = trials_total + 1;
            design.b(b).trial(trials_total) = trial;
        
        end
        
        t = t+1;
        
    end
    
    Screen('Flip', visual.window);
    WaitSecs(2);
end
