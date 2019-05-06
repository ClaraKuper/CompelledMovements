### test if io hub is working as expected

from psychopy.iohub.client import launchHubServer

io = launchHubServer()

key = io.devices.keyboard.waitForKeys(keys=[] , maxWait= 0, clear = True)
print("We are waiting for a keypress")

key = io.devices.keyboard.waitForKeys(keys=['q',],maxWait=10)

if key:
    print('a key was pressed')
else:
    print('nothing was pressed')
    
io.quit