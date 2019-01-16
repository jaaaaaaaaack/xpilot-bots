# Jack Beal and Lydia Morneault
# COM-407 CI
# 2018-05-07 Final project
# Based fuzzysystem.py by Jessy Quint and Rishma Mendhekar

# Determines membership in the wall distance linguistic variable.
# Contains sets "close, moderate, and far".
def wallDistance(feeler, fuzzySet): # takes in a feeler and a fuzzy set (close, medium, or far) to determine membership
    distMembership = -1
    if fuzzySet == "close": # a wall has membership in close if the feeler returns a distance between 0 and 100
        if feeler < 20 :
            distMembership = 1
        elif feeler >= 100:
            distMembership = 0
        else:
            distMembership =  1 - ((feeler-20)/80)

    elif fuzzySet == "moderate": # a wall has membership in moderate if the feeler returns a distance between 60 and 250
        if feeler == 175:
            distMembership = 1
        elif feeler <= 60 or feeler >= 250:
            distMembership = 0
        elif feeler > 60 and feeler < 175:
            distMembership =  1 - ((feeler-60)/115)
        elif feeler > 175 and feeler < 250:
            distMembership = 1 -((feeler-175)/75)

    elif fuzzySet == "far": # a wall has membership in far if the feeler returns a distance between 18 and 500
        if feeler > 500:
            distMembership = 1
        elif feeler <= 180:
            distMembership = 0
        else:
            distMembership = 1 - ((feeler-180)/320)

    return distMembership


# This function determines membership in the speed linguistic variable.
# Contains sets "slow, moderate, and fast".
def speed(fuzzySet, botSpeed):
    speedMembership = -1
    ivanSpeed = botSpeed
    if fuzzySet == "slow": # a ship has membership in slow if its speed is between 0 and 10
        if ivanSpeed < 5:
            speedMembership = 1
        elif ivanSpeed >= 10:
            speedMembership = 0
        else:
            speedMembership =  1 - ((ivanSpeed-5)/5)

    elif fuzzySet == "moderate": # a ship has membership in moderate if its speed is between 7 and 20
        if ivanSpeed == 15:
            speedMembership = 1
        elif ivanSpeed <= 7 or ivanSpeed >= 20:
            speedMembership = 0
        elif ivanSpeed > 7 and ivanSpeed < 15:
            speedMembership =  1 - ((ivanSpeed-7)/8)
        elif ivanSpeed > 15 and ivanSpeed < 20:
            speedMembership = 1 -((ivanSpeed-15)/5)

    elif fuzzySet == "fast": # a ship has membership in fast if its speed is between 18 and 35
        if ivanSpeed > 35:
            speedMembership = 1
        elif ivanSpeed <= 18:
            speedMembership = 0
        else:
            speedMembership = 1 - ((ivanSpeed-18)/17)

    return speedMembership


# This function determines risk for each rule by taking the max of wall distance and speed for each rule.
def riskEval(feeler, botSpeed): # takes in a wall feeler and speed to determine risk
    wallClose = wallDistance(feeler, "close")
    wallModerate = wallDistance(feeler, "moderate")
    wallFar = wallDistance(feeler, "far")
    speedSlow = speed("slow", botSpeed)
    speedModerate = speed("moderate", botSpeed)
    speedFast = speed("fast", botSpeed)

    ### fuzzy rules ###
    # wall close & speed slow, risk = moderate
    risk1 = max(wallClose, speedSlow)

    # wall close & speed moderate, risk = high
    risk2 = max(wallClose, speedModerate)

    # wall close & speed fast, risk = high
    risk3 = max(wallClose, speedFast)

    # wall moderate & speed slow, risk = low
    risk4 = max(wallModerate, speedSlow)

    # wall moderate & speed moderate, risk = moderate
    risk5 = max(wallModerate, speedModerate)

    # wall moderate & speed fast, risk = high
    risk6 = max(wallModerate, speedFast)

    # wall far & speed slow, risk = low
    risk7 = max(wallFar, speedSlow)

    # wall far & speed moderate, risk = moderate
    risk8 = max(wallFar, speedModerate)

    # wall far & speed fast, risk = moderate
    risk9 = max(wallFar, speedFast)

    # find weighted average of risk from all rules
    WA = ((risk1*0.47)+(risk2*0.86)+(risk3*0.86)+(risk4*0.14)+(risk5*0.47)+(risk6*0.86)+(risk7*0.14)+(risk8*0.47)+(risk9*0.47))/(risk1+risk2+risk3+risk4+risk5+risk6+risk7+risk8+risk9)
    return WA
