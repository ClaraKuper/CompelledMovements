% Set up screens
function setScreens

  global settings scr visual

  AssertOpenGL;

  % in case a test version is running on a different screen with
  % worse syncing properties
  if settings.TEST
      Screen('Preference', 'SkipSyncTests', 1);
  end

    % Define some parameters for the screen in cabin 8

  scr.subDist = 530;          % subject distance (mm)
  scr.refRate = 120;          % refresh rate (Hz)    
  scr.xres    = 1920;         % x resolution (px)
  scr.yres    = 1080;         % y resolution (px)
  scr.width   = 518.0;

  % width  of screen (mm) 
  scr.height  = 292.0;         % height of screen (mm)
  scr.colDept = 8;             % color depth per channel
  scr.nLums   = 2^scr.colDept; % number of possible luminance values

  % If there are multiple displays guess that one without the menu bar is the
  % best choice.  Dislay 0 has the menu bar.
  scr.allScreens = Screen('Screens');
  scr.expScreen  = max(scr.allScreens);

  % Assert correct screen resolution and color depth values
  res = Screen('Resolution', scr.expScreen);
  if scr.xres ~= res.width || scr.yres ~= res.height
      ListenChar(1);
      error('Screen resolution value is set incorrectly.\nIt should be: %d by %d', res.width, res.height);    
  elseif res.pixelSize ~= scr.colDept * 3
      ListenChar(1);
      error('Color depth per channel is set incorrectly.\nIt should be: %d', res.pixelSize/3);
  end
  
  switch settings.MODE
    case 1 % touchPixx
      % initialize the touchpixx 
      % Open datapixx and init PsychImaging
      Datapixx('Open');                                                           %% Opens the Datapixx
      PsychImaging('PrepareConfiguration');
      %PsychImaging('AddTask', 'General', 'UseDataPixx');                         %% Would internally open the Datapixx a second time, ...
                                                                                  % uses PSYNC that can crash with certain system settings
    
    case 2 % eyeLink
      % intialize the eyelink
      mode = 'link';
  end
  
  visual.white = WhiteIndex(scr.expScreen);
  visual.black = BlackIndex(scr.expScreen);
  
  visual.textCol = visual.white;
  
  visual.textCol = visual.white
  
  % Open windows
  [visual.window, visual.windowRect] = PsychImaging('OpenWindow', scr.expScreen, visual.black);
  [visual.xCenter, visual.yCenter] = RectCenter(visual.windowRect);
  Screen('BlendFunction', visual.window, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  visual.winWidth = visual.windowRect(3) - visual.windowRect(1);
  visual.winHeight = visual.windowRect(4) - visual.windowRect(2);
  
  % define stimulus properties as visuals
  % Parameters for stimuli
  visual.ball_moved       = -100; % shift of moving stim from centre, negative values above screen center
  visual.distr_moved_side = 300; %how much are the non-targets moved sideways
  visual.distr_moved_down = 300; %how much is the distractor moved down 

  visual.ballPos_start   = [visual.xCenter, visual.yCenter] + [0, visual.ball_moved];
  visual.ballColor = visual.white;
  visual.ballSize  = 20;

  visual.goalPos1  = [visual.xCenter, visual.yCenter] + [-visual.distr_moved_side,visual.distr_moved_down]; 
  visual.goalPos2  = [visual.xCenter, visual.yCenter] + [visual.distr_moved_side,visual.distr_moved_down]; 
  visual.goals     = [visual.goalPos1;visual.goalPos2];
  visual.goalColor = visual.white;
  visual.goalSize  = visual.ballSize;
  visual.range_accept = 25;
        
  visual.textCol   =  visual.white;     
  end
