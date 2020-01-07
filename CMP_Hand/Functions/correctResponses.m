% Define correct and incorrect responses from script
alljumpTime = [];
allHits     = [];
for b = 1:length(data.block)
  block = data.block(b);
  for t = 1:length(block.trial)
    trial   = block.trial(t);
    des     = design.b(b).trial(t);
    goalPos = des.goalPos;
    switch goalPos
      case goalPos == trial.resPos
        trial.hit = True;
    case goalPos != trial.resPos
        trial.hit = False;
    end
    alljumpTime = [alljumpTime, des.jumpTime];
    allHits     = [allHits, trial.hit];
  end
end 

scatter(alljumpTime,allHits)
% Clean Data

