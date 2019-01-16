# Smartbo-base.py - A template for rule-based expert system agents
# by Jack Beal, 2018
# Like Dumbo.py by Evan Gray, but much more flexible and marginally more intelligent.

import libpyAI as ai
def AI_loop():

    # Welcome to Variable Zone
    feelerDistance = 500 # Length cap for wall feeler rays (xp distance units)
    sideFeelerOffset = 5 # Offset for left/right wall feelers (degrees)
    speedLimit = 10 # Speed threshold for rules (xp speed units)
    wallNearLimit = 50 # Distance threshold for rules (xp distance units)

    # Release keys
    ai.thrust(0)
    ai.turnLeft(0)
    ai.turnRight(0)
    
    # Acquire environmental information
    heading = int(ai.selfHeadingDeg())
    tracking = int(ai.selfTrackingDeg())
    frontWall = ai.wallFeeler(feelerDistance, heading)
    leftWall = ai.wallFeeler(feelerDistance, heading + sideFeelerOffset)
    rightWall = ai.wallFeeler(feelerDistance, heading - sideFeelerOffset)
    trackWall = ai.wallFeeler(feelerDistance, tracking)
    
    #Thrust rules
    if ai.selfSpeed() <= speedLimit and frontWall >= wallNearLimit:
        ai.thrust(1)
    elif trackWall < wallNearLimit:
        ai.thrust(1)
    
    #Turn rules
    if leftWall < rightWall:
        ai.turnRight(1)
    else:
        ai.turnLeft(1)
    
    #Just keep shooting
    ai.fireShot()

ai.start(AI_loop,["-name","Smartbo","-join","localhost"])
