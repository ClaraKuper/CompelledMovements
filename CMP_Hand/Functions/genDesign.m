function genDesign(vpcode)
%
% 2017 by Martin Rolfs
% 2019 mod by Clara Kuper

global design settings

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

% conditions
design.goalPos    = [1,2]; % 1 is left, 2 is right goal

% position and size variables, in dva
design.stimSize   = 1;     % in dva
design.keeperSize = 2;     % in dva

design.ballStart   = -10;   % ball moved relative from screen centre in dva
design.tarPosY     = 10;    % target position from screen centre in dva
design.tarPosX     = 10;    % how much are the targets moved left/right

design.keeperY     = 10;    % where is the starting position of the keeper? 

design.rangeAccept = 2;
design.rangeCalib  = 1;

% speed variables, in dva/s
design.runDur =  0.6;      % how long should one trial (movement from start to end) last (in s)
design.speed = (abs(design.ballStart)+abs(design.tarPosY))/design.runDur;  % dva/s how much does the ball move in one second?

% overall information %
% number of blocks and trials in the first round
if settings.TEST == 0
    design.nBlocks = 1;
    design.nTrials = 10;
else
    design.nBlocks = 5;
    design.nTrials = settings.TRIALS;
end

if settings.TEST
    if settings.CODE
        load(sprintf('./Data/%s_timParams.mat',settings.testCode)); % load a matfile with subject name and code
    else
        load(sprintf('./Data/%s_timParams.mat',design.vpcode)); % load a matfile with subject name and code
    end
    design.alResT    = tim.rea + 2*tim.rea_sd;      % Allowed response time
    design.alMovT    = tim.mov + 2*tim.mov_sd;      % Allowed movement time
    design.jumpTim   = design.alResT;               % random time after which target jumps, maximum is the allowed response time 
    if settings.BLOCK
        blockBy    = design.alResT/design.nBlocks;
        jumpBlocks = [0:blockBy:design.alResT];
    end
else
    design.jumpTim   = 0.1;
    design.alResT    = 1.0;      % Allowed response time
    design.alMovT    = 1.0;      % Allowed movement time
end
    

% build
for b = 1:design.nBlocks
    t = 0;
    for triali = 1:design.nTrials
        for goal = design.goalPos
            t = t+1;
            % define goal position
            trial(t).goalPos = goal;
            % define jump time
            if settings.BLOCK
                trial(t).jumpTim = blockBy*rand(1)+jumpBlocks(b);
            else
                trial(t).jumpTim = rand(1)*design.jumpTim;
            % define jump pos
            end
            trial(t).jumpPos = trial(t).jumpTim*design.speed;
            % define fixation duration
            trial(t).fixT    = design.fixDur + rand(1)*design.fixDurJ;
        end
    end
    % randomize
    r = randperm(t);
    design.b(b).trial = trial(r);
end

blockOrder = [1:b];

design.blockOrder = blockOrder(randperm(length(blockOrder)));
design.nTrialsPB  = t;

% save 
save(sprintf('./Design/%s.mat',vpcode),'design');

end

