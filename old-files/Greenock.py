# Greenock.py - Tries its best to attack, avoid walls, and stay alive!
# Jack Beal, 2018

import libpyAI as ai
import math

def angleDiff(m, n):
    """ Measures the difference between two angles.
        m, n are the two angles, measured in degrees.
        Returns their interior angle, in degrees.
    """
    return int(180-abs(abs(m-n)-180))

def headingDiff(m, n):
    """ Measures the difference between two headings.
        m, n are the two headings, measured in degrees.
        Returns their difference, in degrees.
    """
    r = (m-n) % 360
    if r >= 180:
        r -= 360
    return r


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
        Greenock is a rule-based expert system.
    """

    # Release keys
    ai.thrust(0)
    ai.turnLeft(0)
    ai.turnRight(0)

    # Heuristics
    sideFeelerOffset = 15 # Offsets from heading for wall feelers (degrees)
    nearLimit = 20 * ai.selfSpeed() # Threshold for close objects (xp distance units)
    shotDanger = 80 # Threshold for close bullets (xp distance units)

    # Reset everything else
    ai.setTurnSpeedDeg(20) # Artificial handicap!

    # Acquire information
    heading = int(ai.selfHeadingDeg())
    tracking = int(ai.selfTrackingDeg())

    frontLeftWall = ai.wallFeeler(500,heading + sideFeelerOffset)
    frontRightWall = ai.wallFeeler(500,heading - sideFeelerOffset)

    rshipnum = ai.closestShipId()

    # Combat decisions
    if (ai.shotAlert(0) > -1) and (ai.shotAlert(0) < shotDanger):
        ai.turnToDeg(angleDiff(heading, ai.angleAdd(ai.shot_idir(0), 90)))
        ai.thrust(1)
    elif (ai.closestShipId() > -1):
        ai.turnToDeg(angleDiff(heading, ai.aimdir(ai.closestShipId())))
        ai.fireShot()
    elif (rshipnum > -1):
        ai.turnToDeg(angleDiff(heading, ai.aimdir(ai.closestShipId)))
        if (ai.selfSpeed() < 10):
            ai.thrust(1)
        else:
            ai.fireShot()

    # Navigation decisions
    if ((frontRightWall == frontLeftWall) and (frontRightWall < nearLimit) and (ai.selfSpeed() > 1)):
        ai.turnToDeg(angleDiff(heading, ai.angleAdd(180, ai.selfTrackingDeg())))
        ai.thrust(1)
    elif ((frontRightWall < frontLeftWall) and (frontRightWall < nearLimit) and (ai.selfSpeed() > 1)):
        ai.turnToDeg(angleDiff(heading, ai.angleAdd(180, ai.angleAdd(-15, ai.selfTrackingDeg()))))
        ai.thrust(1)
    elif ((frontRightWall > frontLeftWall) and (frontRightWall < nearLimit) and (ai.selfSpeed() > 1)):
        ai.turnToDeg(angleDiff(heading, ai.angleAdd(180, ai.angleAdd(15, ai.selfTrackingDeg()))))
        ai.thrust(1)


ai.start(AI_loop,["-name","Greenock","-join","localhost"])
