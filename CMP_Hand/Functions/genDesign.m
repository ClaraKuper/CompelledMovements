function genDesign(vpcode)
%
% 2017 by Martin Rolfs
% 2019 mod by Clara Kuper

global design settings scr

% randomize random
rand('state',sum(100*clock));

design.vpcode    = vpcode;

% hand movement required?
% 1 = move, 0 = don't move
design.sacReq = 1;
design.fixReq = 0;

% include fixation point?
% 1 = include, 0 = ommit
design.InclFix = 1;

% Timing %
design.fixDur    = 0.5; % Fixation duration till trial starts [s]
design.fixDurJ   = 0.5; % Additional jitter to fixation

design.iti       = 0.2; % Inter stimulus interval

if settings.TEST
    load(sprintf('./Data/%s_timParams.mat',design.vpcode)); % load a matfile with subject name and code
    design.alResT    = tim.rea + 2*tim.rea_sd;      % Allowed response time
    design.alMovT    = tim.mov + 2*tim.mov_sd;      % Allowed movement time
    design.jumpTim   = design.alResT;               % random time after which target jumps, maximum is the allowed response time 
else
    design.jumpTim   = 0.1;
    design.alResT    = 1.0;      % Allowed response time
    design.alMovT    = 1.0;      % Allowed movement time
end
    

% overall information %
% number of blocks and trials in the first round
if settings.TEST == 0
    design.nBlocks = 1;
    design.nTrials = 10;
else
    design.nBlocks = 5;
    design.nTrials = 30;
end


% fixation point


% conditions
design.goalPos    = [1,2]; % 1 is left, 2 is right goal
design.ballMoved  = -300;  % ball moved relative from fixation point
design.stimsize   = 20;
design.move_at_speed     = 5;     % how many pixels does the ball cross with each jump?

% measured_variables
    


% build
for b = 1:design.nBlocks
    t = 0;
    for triali = 1:design.nTrials
        for goal = design.goalPos
            t = t+1;
            % define goal position
            trial(t).goalPos = goal;
            % define jump time
            trial(t).jumpTim = rand(1)*design.jumpTim;
            % define jump pos
            trial(t).jumpPos = trial(t).jumpTim*design.move_at_speed*scr.hz;
            % define fixation duration
            trial(t).fixT    = design.fixDur + rand(1)*design.fixDurJ;
        end
    end
    % randomize
    r = randperm(t);
    design.b(b).trial = trial(r);
end

design.blockOrder = 1:b;
design.nTrialsPB  = t;

% save 
save(sprintf('./Design/%s.mat',vpcode),'design');
