# Jack Beal and Lydia Morneault
# COM-407 CI
# 2018-05-07 Final project
# Evolutionary strategy agent

from fuzzySystem import *
import libpyAI as ai
import math
from neuralNet import *
import operator
from random import *
import sys


class Individual:

    def __init__(self, chromosome):
        self.filename = "fitness.txt"

        self.chromosome = eval(chromosome)
        # print(chromosome)#debug
        # print(self.chromosome)#debug

        # BEGIN CHROMOSOME
        self.turnSpeedMin   = self.chromosome[0]
        self.speedLimit     = self.chromosome[1]
        self.enemyFireDist  = self.chromosome[2]
        self.maxAngleOffset = self.chromosome[3]
        self.resolution     = self.chromosome[4]
        self.nearLimit      = self.chromosome[5]
        self.enemyClose     = self.chromosome[6]
        # END CHROMOSOME

        # Some initializations
        self.totalDists = 0
        self.lastDist = math.inf
        self.currentDist = math.inf
        self.fitness = 0
        self.counter = 0

        # How about some more of those initializations?
        self.wallPenalty = 100
        self.crashPenalty = 50
        self.killedPenalty = 50
        self.scoreDiffBonusFactor = 1.1
        self.killerBonus = 150

        self.genericFeelerDist = 500

        self.framesDead = 0

        # ai.start(self.AI_loop,["-name","Beal-Morneault","-join","136.244.20.161"])
        # ai.headlessMode()
        self.team = randint(1,4) # pick a random team
        print("Joining team", self.team)#debug
        ai.start(self.AI_loop,["-name","Beal-Morneault","-join","localhost", "-team", str(self.team)])


    ###=== MATH-DOING THINGS ===###

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

    def sigmoid(self, x):
        return (1/(1+math.e**(-x)))

    def enemyRadarDist(self):
        if ai.enemyDistance(0) < 0:
            return math.sqrt((ai.selfRadarX()-ai.closestRadarX())**2 + (ai.selfRadarY()-ai.closestRadarY())**2)
        else:
            return ai.enemyDistance(0)

    # Sort keys for max, sort, etc.
    def returnFirst(self, tuple):
        return tuple[0]

    # Warning: extremely pedestrian
    def returnSecond(self, tuple):
        return tuple[1]


    ###=== NEURAL NET ===###

    def angleDif(self, a1,a2):
        return 180 - abs(abs(a1-a2)-180)

    def squisher(self, val):
        # function to squash wall feeler values to continuous [0, 1] range
        return ((self.genericFeelerDist-val)/self.genericFeelerDist)

    # output is value between 0 and 1 which will determine turning angle
    def trainedNeuralNetwork(self, sTrack, sLeft, sRight, sLeftStraight, sRightStraight):

          # weights from pre-trained neural net
          weightsA = [-3.063679014892556, 7.5330808256258, 0.00015757959002422536, -10.305292880517195, 1.2008061506347043, 1.823947396062319]
          weightsB = [-9.450444827200455, 2.166791273806103, 0.07709871512801356, -3.832065636964595, 8.715205026299607, -7.218993467818581]
          weightsC = [-4.624997352896617, 3.260116096903503, -1.5504548845274602, -4.572320999173, 2.847864653419937, -2.963599270789644]
          weightsFinal = [10.3642652760159, 10.234173892265435, -6.9339357538464315, 4.873999777289678]

          # list of squashed values of feelers
          train = [sTrack, sLeft, sRight, sLeftStraight, sRightStraight]

          # train using inputs from feelers and weights from pre-trained net
          outputA = perceptron2(train, weightsA)
          outputB = perceptron2(train, weightsB)
          outputC = perceptron2(train, weightsC)

          trainFinal = [outputA, outputB, outputC]

          # find output from the net to determine which way to turn
          output = perceptron2(trainFinal, weightsFinal)

          return output


    ###=== FUZZY LOGIC ===###

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
            outputFile = open("fitness.txt", "a")
            # outputFile.write(str((self.totalDists/self.counter))+"\t")
            outputFile.write(str(int((self.fitness**1.2)))+"\t")
            [print(str("%.5f" % g)+"\t", end="", file=outputFile) for g in self.chromosome]
            print("\n", end="", file=outputFile)
            outputFile.close()

        # Release keys
        ai.thrust(0)
        ai.turnLeft(0)
        ai.turnRight(0)
        ai.setTurnSpeed(55)

        # Heuristics
        frontFeelerOffset = 45
        perpFeelerOffset = 90
        rearFeelerOffset = 135
        # turnSpeedMin = 15       # learn     range: 4 - 24
        turnSpeedMax = 55
        speedLimit = 5          # learn     range: 2-6
        lowSpeedLimit = 2
        targetingAccuracy = 4 # 1/2 tolerance in deg for aiming accuracy
        shotIsDangerous = 130

        # Acquire information
        heading = int(ai.selfHeadingDeg())
        tracking = int(ai.selfTrackingDeg())

        ###=== ENEMY FEELERS ===###

        # gets angle to enemy
        enemyDeg = self.angleToPointDeg((ai.selfX(), ai.selfY()),(ai.screenEnemyX(0), ai.screenEnemyY(0)))
        enemyWallDistances = []

        # maxAngleOffset = 90     # learn     range: 30 - 120
        # resolution = 5          # learn     range: 2 - 10
        distAngleTuples = []

        # creates tuples of degrees and wallFeelers
        for m in (0, self.maxAngleOffset, self.resolution):
            distAngleTuples.append((enemyDeg-m, ai.wallFeeler(500, int(enemyDeg - m))))
            distAngleTuples.append((enemyDeg+m, ai.wallFeeler(500, int(enemyDeg + m))))

        # gets furthest feeler
        maxFeelerAngle = max(distAngleTuples, key=self.returnSecond)
        angleToOpenSpace = self.headingDiff(ai.selfHeadingDeg(), maxFeelerAngle[0])


        ###=== WALL FEELERS ===###

        frontWall = ai.wallFeeler(self.genericFeelerDist, heading) # wall feeler for wall directly ahead
        leftFrontWall = ai.wallFeeler(self.genericFeelerDist, heading+frontFeelerOffset) # wall feeler for wall 45 degrees to the left
        rightFrontWall = ai.wallFeeler(self.genericFeelerDist, heading-frontFeelerOffset) # wall feeler for wall 45 degrees to the right
        leftWall = ai.wallFeeler(self.genericFeelerDist, heading+perpFeelerOffset) # wall feeler for wall 90 degrees to the left
        rightWall = ai.wallFeeler(self.genericFeelerDist, heading-perpFeelerOffset) # wall feeler for wall 90 degrees to the right
        backWall = ai.wallFeeler(self.genericFeelerDist, heading-180) # wall feeler for wall straight back
        leftBackWall = ai.wallFeeler(self.genericFeelerDist, heading+rearFeelerOffset) # wall feeler for wall 135 degrees to the left
        rightBackWall = ai.wallFeeler(self.genericFeelerDist, heading-rearFeelerOffset) # wall feeler for wall 135 degrees to the right
        trackWall = ai.wallFeeler(self.genericFeelerDist, tracking) # wall in front of where ship is moving

        # Keep track of all the feeler distances
        feelers = [ frontWall,
                    leftFrontWall,
                    rightFrontWall,
                    leftWall,
                    rightWall,
                    backWall,
                    leftBackWall,
                    rightBackWall,
                    trackWall]

        # Aim assist
        leftDir = (heading+90)%360 # angle 90 degrees to the left of current heading
        rightDir = (heading-90)%360 # angle 90 degrees to the right of current heading
        aimer = ai.aimdir(0) #  direction that the ship needs to turn to in order to face the enemy in degrees
        shot = ai.shotAlert(0) # returns a danger rating of a shot, the smaller the number the more likely the shot is to hit the ship
        enemyX = ai.screenEnemyX(0) # returns the closest enemy's x-coord
        enemyY = ai.screenEnemyY(0) # returns the closest enemy's y-coord
        selfX = ai.selfX() # returns the ship's x-coord
        selfY = ai.selfY() # returns the ship's x-coord

        # Fuzzy variable declaration
        trackRisk = riskEval(trackWall, ai.selfSpeed())   #risk of running into trackWall
        frontRisk = riskEval(frontWall, ai.selfSpeed())   #risk of running into frontWall
        leftRisk = riskEval(leftWall, ai.selfSpeed())     #risk of running into leftWall
        rightRisk = riskEval(rightWall, ai.selfSpeed())   #risk of running into rightWall
        LFRisk = riskEval(leftFrontWall, ai.selfSpeed())  #risk of running into leftFrontWall
        RFRisk = riskEval(rightFrontWall, ai.selfSpeed()) #risk of running into rightFrontWall
        LBRisk = riskEval(leftBackWall, ai.selfSpeed())   #risk of running into leftBackWall
        RBRisk = riskEval(rightBackWall, ai.selfSpeed())  #risk of running into rightBackWall
        backRisk = riskEval(backWall, ai.selfSpeed())     #risk of running into backWall

        # Compress some wall feelers
        sTrack = self.squisher(trackWall)
        sLeft = self.squisher(leftFrontWall)
        sRight = self.squisher(rightFrontWall)
        sLeftStraight = self.squisher(leftWall)
        sRightStraight = self.squisher(rightWall)

        # output from neural network that tells how much to turn and which direction
        turn = self.trainedNeuralNetwork(sTrack, sLeft, sRight, sLeftStraight, sRightStraight)


        ###=== THRUST POWER ADJUSTMENT ===#

        # Power levels

        mfS = self.mfSpeed(ai.selfSpeed())
        mfD = self.mfDanger(ai.shotAlert(0))

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

        consequents = [55,45,55,36,36,28,24,30]
        memberships = [p1,p2,p3,p4,p5,p6,p7,p8]
        ai.setPower(self.crispify(memberships, consequents))

        if ai.enemyDistance(0) > self.lastDist and ai.enemyDistance(0) < self.enemyClose:
            ai.thrust(1)

        elif ai.selfSpeed() <= 3 and frontWall >= 200:  # if speed is slow and front wall is far away, thrust
            ai.thrust(1)
        elif trackWall < 60 and frontWall >= 200: # if the track wall is close, thrust
            ai.thrust(1)
        elif backWall < 20: # if the back wall is close, thrust
            ai.thrust(1)


        ###=== TURNING RULES ===###

        # Escape shots
        if shot > 0 and shot < 70:
            # if a shot is closeby, turn and thrust to avoid
            if self.angleDif(rightDir,ai.shotX(0)) < self.angleDif(leftDir,ai.shotX(0)) or self.angleDif(rightDir,ai.shotY(0)) < self.angleDif(leftDir,ai.shotY(0)): # if shot is coming from the right, turn away and thrust
                # print("Turning: avoiding shot")#debug
                ai.turnLeft(1)
                ai.thrust(1)
            elif self.angleDif(leftDir,ai.shotX(0)) < self.angleDif(rightDir,ai.shotX(0)) or self.angleDif(leftDir,ai.shotY(0)) < self.angleDif(rightDir,ai.shotY(0)): # if shot is coming from the left, turn away and shoot ------> change this shot is just a number
                # print("Turning: avoiding shot")#debug
                ai.turnRight(1)
                ai.thrust(1)

        # Turn towards unoccluded enemy
        elif aimer >= 0 and self.angleDif(rightDir,aimer) < self.angleDif(leftDir,aimer) and not self.enemyBehindWall(0): # if an enemy to the right, turn and shoot it
            if ai.screenEnemyX(0) >= 0:
                enemyDeg = self.angleToPointDeg((ai.selfX(), ai.selfY()),(ai.screenEnemyX(0), ai.screenEnemyY(0)))
                ai.setTurnSpeed(self.rangeMap(abs(enemyDeg),0,180,self.turnSpeedMin,turnSpeedMax))
            else:
                enemyDeg = self.angleToPointDeg((ai.selfRadarX(),ai.selfRadarY()),(ai.closestRadarX(),ai.closestRadarY()))
                ai.setTurnSpeed(self.rangeMap(abs(enemyDeg),0,180,self.turnSpeedMin,turnSpeedMax))
            # print("Turning: aiming right")#debug
            ai.turnRight(1)
        elif aimer >= 0 and self.angleDif(leftDir,aimer) < self.angleDif(rightDir,aimer) and not self.enemyBehindWall(0): # if an enemy to the left, turn and shoot it
            if ai.screenEnemyX(0) >= 0:
                enemyDeg = self.angleToPointDeg((ai.selfX(), ai.selfY()),(ai.screenEnemyX(0), ai.screenEnemyY(0)))
                ai.setTurnSpeed(self.rangeMap(abs(enemyDeg),0,180,self.turnSpeedMin,turnSpeedMax))
            else:
                enemyDeg = self.angleToPointDeg((ai.selfRadarX(),ai.selfRadarY()),(ai.closestRadarX(),ai.closestRadarY()))
                ai.setTurnSpeed(self.rangeMap(abs(enemyDeg),0,180,self.turnSpeedMin,turnSpeedMax))
            # print("Turning: aiming left")#debug
            ai.turnLeft(1)

        #fuzzy avoid walls ahead
        elif leftRisk > rightRisk and trackRisk > 0.5:# and min(feelers) < self.nearLimit: #if the left wall and track walls are close, turn right
            #if enemyX >=0 and enemyY >= 0 and ai.wallBetween(selfX, selfY, enemyX, enemyY) == -1:
            ai.turnRight(1)
            # print("Turning: fuzzy right")#debug
        elif rightRisk > leftRisk and trackRisk > 0.5:# and min(feelers) < self.nearLimit: #if the right wall and track walls are close, turn left
            # if enemyX >=0 and enemyY >= 0 and ai.wallBetween(selfX, selfY, enemyX, enemyY) == -1:
            ai.turnLeft(1)
            # print("Turning: fuzzy left")#debug

        # Turn to open space nearest the angle to the enemy
        elif self.enemyBehindWall(0) and min(feelers) > self.nearLimit:
            if angleToOpenSpace < 0:
                # print("Turning: open space left")#debug
                ai.turnLeft(1)
            elif angleToOpenSpace > 0:
                # print("Turning: open space right")#debug
                ai.turnRight(1)

        # if neural net value is not between 0.48 and 0.52 then we have to turn right or left
        elif not (turn >= 0.43 and turn <= 0.57):
            if turn < 0.43: # turn right if value is below 0.43
                # print("Turning: neural net right")#debug
                ai.turnRight(1)
            elif turn > 0.57: # turn left if value is below 0.57
                # print("Turning: neural net left")#debug
                ai.turnLeft(1)


        ###=== FIRING RULES ===###

        # Restrict firing to reasonably accurate attempts:
        # accurate range, enemy not behind wall and enemy close enough
        if self.headingDiff(heading, ai.aimdir(0)) < targetingAccuracy and not self.enemyBehindWall(0) and ai.enemyDistance(0) < self.enemyFireDist:
            ai.fireShot()
            # print("Shot Fired")#debug
        # print("Firing Dist: ", self.enemyFireDist)#debug

        self.counter += 1


        ###=== How did we die? and other Fitness Calculations ===###

        # Fitness function information
        self.totalDists += ai.enemyDistance(0)

        if ai.enemyDistance(0) > 0:
            self.currentDist = ai.enemyDistance(0)

        if self.currentDist < self.lastDist:
            self.fitness += 1
            self.lastDist = self.currentDist
        self.fitness+=1


        alive = ai.selfAlive()
        message = ai.scanGameMsg(1)
        # print(message)#debug
        if alive == 0:
            self.framesDead += 1
            # print(self.framesDead, message)#debug

            if self.framesDead == 2:
                # print("dead now")#debug
                # Ran into wall
                if message.find("Beal-Morneault") != -1 and message.find("wall") != -1:
                    print("End of match: wall collision.")#debug
                    self.fitness -= self.wallPenalty
                # Crashed into player
                elif message.find("crashed.") != -1:
                    print("End of match: player collision.")#debug
                    self.fitness -= self.crashPenalty
                # Killed by bullet
                elif message.find("Beal-Morneault was") != -1:
                    print("End of match: killed by opponent.")#debug
                    self.fitness -= self.killedPenalty
                # Killed the opponent
                elif message.find("by a shot from Beal-Morneault") != -1:
                    print("End of match: killed the opponent!")#debug
                    self.fitness += self.killerBonus

                else:
                    print("End of match: enemy died.")

                self.fitness += (ai.selfScore()-ai.enemyScoreId(0))*self.scoreDiffBonusFactor
                ai.quitAI()
        else:
            self.framesDead = 0


def main(*args):
    # print(sys.argv[2])#debug
    agent = Individual(sys.argv[2])

if __name__ == "__main__":
    main()
