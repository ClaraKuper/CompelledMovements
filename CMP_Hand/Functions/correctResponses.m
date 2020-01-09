% Define correct and incorrect responses from script
alljumpTime = [];
allHits     = [];

for b = 1:length(data.block)
  block = data.block(b);
  for t = 1:length(block.trial)
    hit         = 0;
    trial   = block.trial(t);
    des     = design.b(b).trial(t);
    goalPos = des.goalPos;
    switch goalPos
      case goalPos == trial.resPos
        hit = 1;
      case goalPos != trial.resPos
        hit = 0;
    end
    alljumpTime = [alljumpTime, des.jumpTim];
    allHits     = [allHits, hit];
  end
end 

% scatter(alljumpTime,allHits)

% Clean Data

% As moving mean
step = max(alljumpTime)/25;
plot_data = [];
start = 0.05;
while start < max(alljumpTime)
  stop        = start + step;
  sum_correct = sum(allHits(find(start<alljumpTime<stop)));
  hit_number  = length(allHits(find(start<alljumpTime<stop)));
  plot_data   = [plot_data, [start;sum_correct/hit_number]];
  start       = stop;
end

plot(plot_data(1,:),plot_data(2,:));