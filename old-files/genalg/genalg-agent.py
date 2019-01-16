# Jack Beal and Lydia Morneault
# COM-407 CI
# 2018-04-21
# Gen alg agent

import libpyAI as ai
import math
from random import *
import operator
import sys

class Individual:

    def __init__(self, chromosome):
        self.filename = "fitness.txt"
        self.chromosome = chromosome

        # Decode chromosome...
        # Eight bits per value
        self.nearLimit = int(self.chromosome[:8], 2)
        self.veryNearLimit = int(self.chromosome[8:16], 2)
        self.shotTooClose = int(self.chromosome[16:24],2)
        self.enemyTooClose = int(self.chromosome[24:32],2)
        # Five bits per value
        print("Selection:", self.chromosome)#debug
        self.frontFeelerOffset = self.rangeMap(int(self.chromosome[32:37],2), 0,32, 1,90) # [0,32)->[1,90]
        self.rearFeelerOffset = self.rangeMap(int(self.chromosome[37:42],2), 0,32, 91,179) # [0,32)->[91,179]
        # Three bits
        self.speedLimit = (int(self.chromosome[42:45],2))
        # Two bits
        self.speedLimit = (int(self.chromosome[45:47],2))

        self.counter = 0
        name = "bot"
        ai.start(self.AI_loop,["-name",name,"-join","localhost"])


    # Arithmetic functions ======================================================

    def angleDiff(self, m, n):
        return int(180-abs(abs(m-n)-180))

    def headingDiff(self, m, n):
        return ((m-n)+180)%360 - 180

    def angleToPointDeg(self, p1, p2):
        # Assumes p1, p2 are duples with coordinates
        dx = p1[0]-p2[0]
        dy = p2[1]-p1[1]
        m = -1*(int(math.degrees(math.atan2(dy, dx)))+180)%360
        return self.headingDiff(m, ai.selfHeadingDeg())

    def enemyBehindWall(self, idx):
        if ai.wallBetween(ai.selfX(), ai.selfY(), ai.screenEnemyX(idx), ai.screenEnemyY(idx)) == -1:
            return False
        return True

    def rangeMap(self, val, srcMin, srcMax, destMin, destMax):
        scaledVal = (val - srcMin)/(srcMax - srcMin)
        return destMin + scaledVal*(destMax-destMin)


    # Fuzzy Logic ===============================================================

    def getMembership(self, c, pair):
        # Assumes pair is x coords in increasing order of y coords
        # This is kind of awkward, but it works!
        # e.g. the line 3,0 to 5,1 -> [3,5] and 6,1 to 10,0 -> [10,6]
        if pair[0] < pair[1]:
            return (c-pair[0])/(pair[1]-pair[0])
        else:
            return abs(((c-pair[1])/(pair[0]-pair[1])-1))

    def mfSpeed(self, c):
        # This hard codes a particular set!!
        # Will return a triple will all 3 memberships
        #   m1 = slow / m2 = medium / m3 = fast

        # SLOW SET
        if 0<=c<=5:
            m1 = self.getMembership(c,[5,0])
        else:
            m1 = 0

        # MEDIUM SET
        if 3<=c<=6:
            m2 = self.getMembership(c,[3,6])
        elif 6<c<=9:
            m2 = self.getMembership(c,[9,6])
        else:
            m2 = 0

        # FAST SET
        if 8<=c<=12:
            m3 = self.getMembership(c,[8,12])
        elif 12<c<=100:
            m3 = 1
        else:
            m3 = 0

        return [m1, m2, m3]

    def mfDanger(self, c):
        # Also hard codes a specific set!

        # High danger
        if 0<=c<=30:
            m1 = self.getMembership(c,[30,0])
        else:
            m1 = 0

        # Moderate danger
        if 20<=c<=80:
            m2 = self.getMembership(c,[10,80])
        elif 80<c<140:
            m2 = self.getMembership(c,[140,80])
        else:
            m2 = 0

        # High danger
        if 130<=c<=210:
            m3 = self.getMembership(c,[130,210])
        elif 210<c<=30000:
            m3 = 1
        else:
            m3 = 0

        return [m1, m2, m3]

    def crispify(self, mships, cquents):
        # Take a weighted average of the things
        # Params are list of consequent memberships and list of singleton vals

        if len(mships) != len(cquents):
            print("self.crispify: bad params")
            return -1

        numerator = 0
        for i in range(len(mships)):
            numerator += mships[i]*cquents[i]

        if sum(mships) == 0:
            return 0
        else:
            return (numerator/sum(mships))


    # MAIN LOOP =================================================================

    def AI_loop(self):

        # print("AI_LOOP")

        if ai.selfAlive() == 0:
            print("selfAlive is 0")

        # if ai.selfAlive() == 0 and time2quit:
            outputFile = open("output.txt", "w")
            outputFile.write(str(self.counter))
            outputFile.close()
            # ai.quitAI()

        # print(countFrames)

        # Release keys
        ai.thrust(0)
        ai.turnLeft(0)
        ai.turnRight(0)
        ai.setTurnSpeed(55)

        turnSpeedMin = 15
        turnSpeedMax = 64

        # Heuristics
        #frontFeelerOffset = 35
        ffo = self.frontFeelerOffset
        rfo = self.rearFeelerOffset
        perpFeelerOffset = 90
        #rearFeelerOffset = 135

        # speedLimit = 5
        lowSpeedLimit = 2
        targetingAccuracy = 4 # 1/2 tolerance in deg for aiming accuracy
        shotIsDangerous = 130

        # Acquire information
        heading = int(ai.selfHeadingDeg())
        tracking = int(ai.selfTrackingDeg())

        # Wall feeling
        feelers = []

        frontWall = ai.wallFeeler(750,heading)
        leftWall = ai.wallFeeler(500,heading+perpFeelerOffset)
        rightWall = ai.wallFeeler(500,heading-perpFeelerOffset)
        trackWall = ai.wallFeeler(750,tracking)
        rearWall = ai.wallFeeler(250,heading-180)
        backLeftWall = ai.wallFeeler(500,heading+round(rfo))
        backRightWall = ai.wallFeeler(500,heading-round(rfo))
        frontLeftWall = ai.wallFeeler(500,heading+round(ffo))
        frontRightWall = ai.wallFeeler(500,heading-round(ffo))

        feelers.append(frontWall)
        feelers.append(leftWall)
        feelers.append(rightWall)
        feelers.append(trackWall)
        feelers.append(rearWall)
        feelers.append(backLeftWall)
        feelers.append(backRightWall)
        feelers.append(frontLeftWall)
        feelers.append(frontRightWall)

        if min(feelers) < self.veryNearLimit:
            self.speedLimit = lowSpeedLimit

        # Movement controls

        # Compute angles to the nearest things
        m = self.angleToPointDeg((ai.selfX(), ai.selfY()), (ai.shotX(0), ai.shotY(0)))
        n = self.angleToPointDeg((ai.selfX(), ai.selfY()), (ai.shotX(0), ai.shotY(0)))

        # Sets turn speed and degree to the enemy
        if ai.screenEnemyX(0) >= 0:
            enemyDeg = self.angleToPointDeg((ai.selfX(), ai.selfY()),(ai.screenEnemyX(0), ai.screenEnemyY(0)))
            ai.setTurnSpeed(self.rangeMap(abs(enemyDeg),0,180,turnSpeedMin,turnSpeedMax))
        else:
            enemyDeg = self.angleToPointDeg((ai.selfRadarX(),ai.selfRadarY()),(ai.closestRadarX(),ai.closestRadarY()))
            ai.setTurnSpeed(self.rangeMap(abs(enemyDeg),0,180,turnSpeedMin,turnSpeedMax))

        # Turn towards unoccluded enemies while in open space
        if ai.aimdir(0) >= 0 and self.headingDiff(heading, ai.aimdir(0)) > 0 and not self.enemyBehindWall(0):
            ai.turnRight(1)
        elif ai.aimdir(0) >= 0 and self.headingDiff(heading, ai.aimdir(0)) < 0 and not self.enemyBehindWall(0):
            ai.turnLeft(1)
        # Turn away from nearby walls
        elif min(feelers) < ai.enemyDistance(0) and trackWall < self.nearLimit and leftWall < rightWall: #DONE
            ai.turnRight(1)
        elif min(feelers) < ai.enemyDistance(0) and trackWall < self.nearLimit and rightWall < leftWall: #DONE
            ai.turnLeft(1)
        elif min(feelers) < ai.enemyDistance(0) and backLeftWall < self.nearLimit and rightWall > self.nearLimit:
            ai.turnRight(1)
        elif min(feelers) < ai.enemyDistance(0) and backRightWall < self.nearLimit and leftWall > self.nearLimit:
            ai.turnLeft(1)
        elif min(feelers) < ai.enemyDistance(0) and frontRightWall < self.nearLimit:
            ai.turnLeft(1)
        elif min(feelers) < ai.enemyDistance(0) and frontLeftWall < self.nearLimit:
            ai.turnRight(1)
        # TODO: NEED RULES FOR WHEN ENEMY IS OCCLUDED
        elif self.enemyBehindWall and enemyDeg < 0:
            ai.turnRight(1)
        elif self.enemyBehindWall and enemyDeg >= 0:
            ai.turnLeft(1)
        # Turn away from shots
        elif m > 0:
            ai.turnRight(1)
        elif m < 0:
            ai.turnLeft(1)

        # THRUST (includes fuzzy controller)

        # Power levels
        power1 = 55
        power2 = 45
        power3 = 55
        power4 = 36
        power5 = 36
        power6 = 28
        power7 = 24
        power8 = 30

        mfS = self.mfSpeed(ai.selfSpeed())
        mfD = self.mfDanger(ai.shotAlert(0))

        # Aggregation

        # if S is high and D is moderate or high:
        p1 = max(mfS[2], min(mfD[1], mfD[2]))
        # if S is moderate and D is moderate:
        p2 = max(mfS[1], mfD[1])
        # if S is low and D is high:
        p3 = max(mfS[0], mfD[2])
        # if S is moderate and D is moderate:
        p4 = max(mfS[1], mfD[1])
        # if S is low and D is moderate:
        p5 = max(mfS[0], mfD[1])
        # if S is high and D is low:
        p6 = max(mfS[2], mfD[0])
        # if S is moderate and D is low:
        p7 = max(mfS[1], mfD[0])
        # if S is low and D is low:
        p8 = max(mfS[0], mfD[0])

        consequents = [power1,power2,power3,power4,power5,power6,power7,power8]
        memberships = [p1,p2,p3,p4,p5,p6,p7,p8]

        # Defuzzification
        ai.setPower(self.crispify(memberships, consequents))

        # Further thrusting rules
        if ai.shotAlert(0) < 130 and ai.shotAlert(0) != -1 and ai.wallBetween(ai.selfX(), ai.selfY(), ai.shotX(0), ai.shotY(0)) == -1:
            ai.thrust(1)
        elif ai.selfSpeed() <= self.speedLimit:
            ai.thrust(1)
        elif trackWall < self.nearLimit and self.angleDiff(heading, tracking)>75:
            ai.thrust(1)
        elif rearWall < self.nearLimit and self.angleDiff(heading, tracking)>90:
            ai.thrust(1)

        # FIRE

        # Restrict firing to reasonably accurate attempts
        if self.headingDiff(heading, ai.aimdir(0)) < targetingAccuracy and not self.enemyBehindWall(0):
            ai.fireShot()

        self.counter += 1

def main(*args):
    # chrom = "10011101111111110010110101100010000110001101010"
    # agent = Individual(chrom)#chosen indiviual
    print(sys.argv)#debug
    agent = Individual(sys.argv[2])   # for training with GA


if __name__ == "__main__":
    main()
