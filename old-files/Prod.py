# Prod.py - A reasonably intelligent rule-based expert system Xpilot agent
# Jack Beal and Lydia Morneault, February 2018

import libpyAI as ai
import math

def angleDiff(m, n):
    """ Measures the difference between two arbitrary angles.
        m, n are the two angles, measured in degrees.
        Returns their difference, in degrees.
    """
    return int(180-abs(abs(m-n)-180))

def headingDiff(m, n):
    """ Measures the difference between two headings.

        m, n are the two headings, measured in degrees.
        Returns their difference, in degrees.
    """
    return ((m-n)+180)%360 - 180

def angleToPointDeg(p1, p2):
    """ Compute the angle between two Cartesian points, relative to horizontal.
        p1, p2 are the two points, given as duples.
    """
    dx = p1[0]-p2[0]
    dy = p2[1]-p1[1]
    m = -1*(int(math.degrees(math.atan2(dy, dx)))+180)%360
    return headingDiff(m, ai.selfHeadingDeg())

def AI_loop():
    """ The main loop for this agent!
        Prod.py is a rule-based expert system.
    """

    # Release keys
    ai.thrust(0)
    ai.turnLeft(0)
    ai.turnRight(0)

    # Heuristics
    sideFeelerOffset = 65 # Offsets from heading for wall feelers (degrees)
    perpFeelerOffset = 90 # (degrees)
    trackFeelerOffset = 45 # (degrees)

    nearLimit = 150 # Threshold for a relatively "close" object (xp distance units)
    nearLimitThreat = 300 # Threshold for a "very close" object (xp distance units)
    shotDanger = 130 # Threshold for relatively "close" bullets (xp distance units)

    speedLimit = 5 # (xp speed units)
    powerHigh = 45 # (xp thrust power units)
    powerLow = 20 # (xp thrust power units)
    targetingAccuracy = 5 # Tolerance from heading within which firing is OK (degrees)

    # Reset everything else
    ai.setTurnSpeedDeg(20) # Artificial handicap!
    ai.setPower(powerLow)

    # Acquire information
    heading = int(ai.selfHeadingDeg())
    tracking = int(ai.selfTrackingDeg())

    feelers = []
    heading = int(ai.selfHeadingDeg())
    tracking = int(ai.selfTrackingDeg())
    frontWall = ai.wallFeeler(500,heading)
    leftWall = ai.wallFeeler(500,heading+perpFeelerOffset)
    rightWall = ai.wallFeeler(500,heading-perpFeelerOffset)
    trackWall = ai.wallFeeler(500,tracking)
    rearWall = ai.wallFeeler(500,heading-180)
    backLeftWall = ai.wallFeeler(500,heading+135)
    backRightWall = ai.wallFeeler(500,heading-135)
    frontLeftWall = ai.wallFeeler(500,heading+45)
    frontRightWall = ai.wallFeeler(500,heading-45)

    feelers.append(frontWall)
    feelers.append(leftWall)
    feelers.append(rightWall)
    feelers.append(trackWall)
    feelers.append(rearWall)
    feelers.append(backLeftWall)
    feelers.append(backRightWall)
    feelers.append(frontLeftWall)
    feelers.append(frontRightWall)

    # Collect distances
    if ai.enemyDistanceId(ai.closestShipId()) > 0:
        closestPlayerDistance = ai.enemyDistanceId(ai.closestShipId())
    else:
        closestPlayerDistance = math.inf

    if ai.shotDist(0) > 0:
        closestBulletDistance = ai.shotDist(0)
    else:
        closestBulletDistance = math.inf

    dcw = min(feelers)
    distToNearestThreat = min(closestPlayerDistance, closestBulletDistance)

    # Assign priority to nearest threat
    if closestBulletDistance <= dcw and closestBulletDistance <= closestPlayerDistance: # if closest threat is a bullet
        priority = 1
    elif dcw <= closestPlayerDistance and dcw <= closestBulletDistance: # if closest threat is a wall
        priority = 2
    else: # closest threat is a player
        priority = 3

    if distToNearestThreat < nearLimitThreat:
        ai.setPower(powerHigh)

    # If the closest threat is a bullet
    if priority == 1:
        m = angleToPointDeg((ai.selfX(), ai.selfY()), (ai.shotX(0), ai.shotY(0)))
        if m >=0:
            ai.turnRight(1)
        else:
            ai.turnLeft(1)

        if ai.shotAlert(0) < shotDanger:
            ai.thrust(1)

    # If the closest threat is a wall
    elif priority == 2:
        # Thrust
        if ai.selfSpeed() <= speedLimit:
            ai.thrust(1)
        elif trackWall < nearLimit and angleDiff(heading, tracking)>90:
            ai.thrust(1)
        elif rearWall < nearLimit and angleDiff(heading, tracking)>90:
            ai.thrust(1)

        # Turn
        if trackWall < nearLimit and leftWall < rightWall:
            ai.turnRight(1)
        elif trackWall < nearLimit and rightWall < leftWall:
            ai.turnLeft(1)
        elif backLeftWall < nearLimit and rightWall > 50:
            ai.turnRight(1)
        elif backRightWall < nearLimit and leftWall > 50:
            ai.turnLeft(1)
        elif frontRightWall < nearLimit:
            ai.turnLeft(1)
        elif frontLeftWall < nearLimit:
            ai.turnRight(1)

    # If the closest threat is a player
    elif priority == 3:
        m = angleToPointDeg((ai.selfX(), ai.selfY()), (ai.shotX(0), ai.shotY(0)))
        if m <=0:
            ai.turnRight(1)
        else:
            ai.turnLeft(1)

        if ai.selfHeadingDeg() <= (targetingAccuracy + angleToPointDeg((ai.selfX(), ai.selfY()), (ai.screenEnemyX(0), ai.screenEnemyY(0)))) and ai.selfHeadingDeg() >= (targetingAccuracy - angleToPointDeg((ai.selfX(), ai.selfY()), (ai.screenEnemyX(0), ai.screenEnemyY(0)))):
            ai.fireShot()


ai.start(AI_loop,["-name","Prod","-join","localhost"])
