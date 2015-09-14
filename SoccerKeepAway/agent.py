import kUtil, pickle, os, math, unittest, ball
import calcReceive
import pygame

class agent():
    #initial parameters: XY position, the sigma for calculating noise, and type "keeper" or "taker"
    def __init__(self, worldRef, pos, sigma, agentType, trueBallPos, maxPlayerSpeed, maxBallSpeed, inPossession = False):
        self.sigma = sigma
        self.true_pos = pos
        self.noisy_pos = kUtil.getNoisyVals(self.true_pos, self.sigma)
        self.agentType = agentType
        self.maxPlayerSpeed = maxPlayerSpeed
        self.keeperArray = None
        self.takerArray = None
        self.agentListIndex = None
        self.stateVariables = None
        self.onReceiveDecision = None #receive variables
        self.worldRef = worldRef
        
        #BALL VARIABLES
        self.noisyBallPos = kUtil.getNoisyVals(trueBallPos, self.sigma)
        self.maxBallSpeed = maxBallSpeed
        self.fieldBall = None
        self.inPosession = False
        self.isKicking = False
        
        #go and initialize the variables used for getOpen and passBall
        portionOfBorderToStayAwayFrom = 0.15
        self.getOpenPoints = self.initializeGetOpenGrid(portionOfBorderToStayAwayFrom)
        #the playable region is bound by a top left and a bottom right coordinate.
        #    these coordinates define a rectangle that the agents will try to stay in:
        #    when an agent passes the ball, it makes sure it's team mate can get the ball
        #    at the edge of the boundary
        self.playableRegionTopLeft = (self.worldRef.display_height * portionOfBorderToStayAwayFrom/2, 
                                    self.worldRef.display_width * portionOfBorderToStayAwayFrom/2)
        self.playableRegionBottomRight = (self.worldRef.display_height - self.playableRegionTopLeft[0],
                                          self.worldRef.display_width - self.playableRegionTopLeft[1])
        
        #initialize the cosines of interest for getting rotated vectors
        self.cosinesOfInterest = []
        self.passAngleGranularity = 5
        self.terminalPassAngle = 45
        for i in list(range(5, self.terminalPassAngle, self.passAngleGranularity)):
            self.cosinesOfInterest.append(math.cos(math.pi / 180 * i))
        
        
    #used only in keepaway.py
    #used by keepaway.py go give the agent a direct reference to the ball object. 
    #agent will need this reference in order to set the ball's velocity if the agent ever gains posession
    def receiveBallReference(self, inputBall):
        self.fieldBall = inputBall
    
    #this function will only be used by keepaway.py to update some initial variables that couldn't be updated
    #in __init__
    def receiveListOfOtherPlayers(self,  keeperArray, takerArray,index):
        self.takerArray = takerArray
        self.keeperArray = keeperArray
        self.agentListIndex= index #index in either the taker list or keeper list
        
    #used only in keepaway.py
    #When the world calculates the state variables, the agent will get a noisy copy of them
    def receiveStateVariables(self, variables):
        self.stateVariables = kUtil.getNoisyVals(variables, self.sigma)
        
    #used only in keepaway.py   
    def receiveDecision(self, rDecision):
        self.onReceiveDecision = rDecision
        self.onReceiveDecision[1] = kUtil.getNoisyVals(self.onReceiveDecision[1], self.sigma)
    
    #used only in keepaway.py. Only keepaway.py is allowed to actually change positions of agents
    #agents only have the power to request movements
    def updateAgentPosition(self, truePosition):
        self.true_pos = truePosition
        self.noisy_pos = kUtil.getNoisyVals(truePosition, self.sigma)
    
    #for keepers, go to the intersection, or optimal point
    #for takers, just go to the ball
    #note: this returns a movement vector that must be implemented in keepaway
    def goToBall(self):
        
        if (self.agentType == "keeper"):
            V = kUtil.getVector(self.noisy_pos, self.onReceiveDecision[1])
            minDist = min(self.maxPlayerSpeed, kUtil.getDist(self.noisy_pos, self.onReceiveDecision[1]))
        else:
            #you have a taker. have him be stupider by going to the ball rather than the intersection point
            V = kUtil.getVector(self.noisy_pos, self.noisyBallPos)
            minDist = min(self.maxPlayerSpeed, kUtil.getDist(self.noisy_pos, self.noisyBallPos))
        
        #these 2 lines of code are for if you want keepers and takers to go to same location
        #this is the more challenging case as the taker will predict where the ball intersects
        """
        V = kUtil.getVector(self.noisy_pos, self.onReceiveDecision[1])
        minDist = min(self.maxPlayerSpeed, kUtil.getDist(self.noisy_pos, self.onReceiveDecision[1]))
        """
        
        self.worldRef.moveAttempt(self, (V, minDist))
        #return (V, self.maxPlayerSpeed)
        
    
    #given this agent's current position, check and see if a point is currently
    #inside the agent boundaries. If it is, return true. if not, return false
    #This function will be used to see if the soccer ball will end up inside the 
    #agent if the agent were to just hold his/her ground
    def agentCurrentlyInPoint(self, point):
        row1 = agent.noisy_pos[0]
        col1 = agent.noisy_pos[1]
        row2 = row1 + self.worldRef.agent_block_size
        col2 = col1 + self.worldRef.agent_block_size
        if (point[0] >= row1 and point[0] <= row2):
            if (point[1] >= col1 and point[1] <= col2):
                return True
        return False
        
    
    #just hold your ground and return        
    def holdBall(self):
        if self.fieldBall == None:
            print "ERROR: trying to hold ball without actually having  ball" 
        return
    
    #just a temporary function to draw the vectors that are being calculated for debugging purposes
    def debugPassVectors(self, startPoint, vectors):
        self.worldRef.drawWorld ()
        self.worldRef.displayScore()
        print "Starting point: ", startPoint 
        for vector in vectors:
            newVector = kUtil.addVectorToPoint(startPoint, kUtil.scalarMultiply(5, vector))
            print "printing vector: ", newVector
            self.worldRef.gameDisplay.blit(self.worldRef.debugYellowDotImage, (newVector[1], newVector[0]))
        self.worldRef.gameDisplay.blit(self.worldRef.debugRedDotImage, (startPoint[1], startPoint[0]))
        pygame.display.update()
        print "debugging"
            
    #only keeper 0 will have this option available
    def passBall(self, integerK):
        print "passing to team mate ", integerK +1
        #if you're passing to integerK = 1, then that means pass to the keeper that's closer to you
        #if you're passing ot integerK = 2, then that means pass to the keeper that's farther to you
        #0 is an invalid input
        sortedKeepers = sorted(self.keeperArray)
        if integerK == 0:
            print "Invalid input for integerK! integerK not allowed to be", integerK
            return
        if self.fieldBall == None:
            print "ERROR: trying to hold ball without actually having  ball"
            return
        
        #pass to team mate integerK. if integerK = 1, then it's the 2nd element in array
        selfToTeammateDirection = kUtil.unitVector(kUtil.getVector(self.noisyBallPos, sortedKeepers[integerK].noisy_pos))
        selfToTeammateVector = (kUtil.scalarMultiply(self.fieldBall.maxBallSpeed, selfToTeammateDirection))
        
        """
        #this code segment is for determining which angle you'd rather pass to. it's all deterministic
        ballPos = self.noisyBallPos
        passVectorsToConsider = []
        passVectorsToConsider.append(selfToTeammateDirection)
        for i in range(len(self.cosinesOfInterest)):
            passVectorsToConsider = passVectorsToConsider + self.getRotatedVectors(selfToTeammateDirection, self.cosinesOfInterest[i])
        #now sort the vectors based on how open they are:
        self.debugPassVectors(ballPos, passVectorsToConsider)
        passVectorsToConsider = sorted(passVectorsToConsider, 
                                       key = lambda vector: max ( kUtil.cosTheta(self.worldRef.takerArray[0].getNoisyMidPoint(), ballPos, kUtil.addVectorToPoint(ballPos, vector)), 
                                                                  kUtil.cosTheta(self.worldRef.takerArray[1].getNoisyMidPoint(), ballPos, kUtil.addVectorToPoint(ballPos, vector))),
                                        )
        #iterate over the sorted list until you find a pass that you can do
        for i in range(len(passVectorsToConsider)):
            if( calcReceive.calc_receive(self.worldRef, passVectorsToConsider[i]) != None): 
                selfToTeammateDirection = passVectorsToConsider[i]
                selfToTeammateVector = (kUtil.scalarMultiply(self.fieldBall.maxBallSpeed, selfToTeammateDirection))
                print "PASS USING ANGLE ACHEIVED AT i=", i
                break
        """    
                
        #at this point, you've determined the angle you wanna pass, and you pass.
        #set ball's possesion to false, and update to new point. ball class handles direction vector
        self.fieldBall.updatePosession(False)
        self.inPosession = False
        self.isKicking = True
        #kUtil.addVectorToPoint(self.fieldBall.trueBallPos, selfToTeammateVector)
        self.fieldBall.update(kUtil.getNoisyVals(selfToTeammateVector, self.sigma))
        #self.fieldBall.updatepos( kUtil.addVectorToPoint(self.fieldBall.true_pos, selfToTeammateVector ) )
        #return (selfToTeammateDirection, self.maxBallSpeed)
    
    #UNIT TESTED 
    #use the solution to a quadratic formula to get the rotated unit vectors. So if you had a vector, and
    #you wanted the 2 vectors that you get when you rotate that vector 5 degrees in either direction,
    #then use this function. The formula from this function was derived from a dot b = mag(a)*mag(b)cosTheta
    #and the contrant that bx^2 + by^2 = 1 if b is a unit vector
    def getRotatedVectors(self, vector, cos_k):
        discriminantIsZero = False
        terminalPosCosZero = kUtil.addVectorToPoint(self.noisyBallPos, vector) 
        vector = kUtil.unitVector(vector)
        ax = vector[1] #columns are x
        ay = vector[0] #rows are y
        k = cos_k
        term1 = 2*k*ax #term 1 = -b 
        discriminant = term1 * term1 - 4 * (ax*ax +ay*ay)*(-1.0*ay*ay + k * k)
        discriminant = math.sqrt(discriminant)
        if (abs(discriminant) < 0.00001):
            discriminantIsZero = True
            
        #denominator = 2 * (ax*ax + ay*ay) #should be 2 every time if A is a unit vector
        denominator = 2 #should be 2 every time if A is a unit vector
        bx1 = (term1 - discriminant) / denominator
        #print "term1: ", term1, " discriminant:", discriminant, " denominator: ", denominator
        by1 = math.sqrt(1.0 - (bx1 * bx1))
        returnUnitVectors = []
        #make it (row,col) format, so therefore it's (y,x)
        returnUnitVectors.append((by1, bx1))
        returnUnitVectors.append((-1.0 * by1, bx1))
        
        if discriminantIsZero == False:
            bx2 = (term1 + discriminant) / denominator
            by2 = math.sqrt(1.0 - (bx2 * bx2))
            returnUnitVectors.append((by2, bx2))
            returnUnitVectors.append((-1.0 * by2, bx2)) 
            #print "return vectors"
            #print returnVectors
            returnUnitVectors = sorted(returnUnitVectors, key=lambda x: kUtil.getSqrDist(terminalPosCosZero, x))
            
        return returnUnitVectors[:2]
        
    #getOpen() needs to consider a very limited amount of points. 
    #this function should be called in initialization to go and defined the 
    #list of all points that getOpen will check 
    def initializeGetOpenGrid(self, portionOfBorderToStayAwayFrom):
        #portionOfBorderToStayAwayFrom specified which percent of the boarder
        #to ignore. So it you migth end up ignoring 15% of the border
        #The rest of the area, split it into 25 points, going 5x5
        cutoffWidth = self.worldRef.display_width * portionOfBorderToStayAwayFrom
        cutoffHeight = self.worldRef.display_height * portionOfBorderToStayAwayFrom
        widthIncrement = (self.worldRef.display_width - (2 * cutoffWidth)) / 5.0
        heightIncrement = (self.worldRef.display_height - (2*cutoffHeight)) / 5.0
        returnList = []
        for i in range(5):
            #i will be the row index iterator
            for j in range(5):
                #j will be the column index iterator
                returnList.append( (cutoffHeight + heightIncrement * i, cutoffWidth + widthIncrement * j) )
        return returnList
            
    
    def getOpen(self):
        #note: safety constant is cos(18.4) degrees
        safetyConstant = 0.94887601164449654493424118056447
        curMax = float("-inf")
        argMax = None
        if self.worldRef.fieldBall.trueBallDirection == (0.0, 0.0):
            predictedBallPos = self.noisyBallPos
        else:
            predictedBallPos = self.onReceiveDecision[1]
        for point in self.getOpenPoints:
            safety = max(kUtil.cosTheta(point, predictedBallPos, self.takerArray[0].noisy_pos),
                         kUtil.cosTheta(point, predictedBallPos, self.takerArray[1].noisy_pos))
            if (safety > safetyConstant):
                #angle is too narrow, a taker can easiy steal
                continue
            
            #if you're at this point, then then point is a safe point to consider
            teamCongestion = 0.0
            oppCongestion = 0.0
            totalCongestion = 0.0
            value = 0.0
            for i in range(len(self.keeperArray)):
                if i != self.agentListIndex:
                    teamCongestion += 1.0 / (kUtil.getDist(self.keeperArray[i].noisy_pos, point))
            for i in range(len(self.takerArray)):
                oppCongestion += 1.0 / (kUtil.getDist(self.takerArray[i].noisy_pos, point))
            totalCongestion = teamCongestion + oppCongestion
            value = -1.0 * totalCongestion
            if (value > curMax):
                curMax = value
                argMax = point
        #At this point, just run towards argMax at max speed
        minDist = min(self.maxPlayerSpeed, kUtil.getDist(self.noisy_pos, argMax))
        self.worldRef.moveAttempt(self, (kUtil.getVector(self.noisy_pos, argMax), minDist) )
                    
        
    
    def blockPass(self, kIndex):
        #kIndex is ordered based on who is the closest keeper
        keeperActual = sorted(self.keeperArray)
        #use the current keeper 0 position to block pass
        midPoint = kUtil.getMidPoint(keeperActual[0].noisy_pos, keeperActual[kIndex].noisy_pos)
        #use the predicted keeper 0 position to block pass
        #midPoint = kUtil.getMidPoint(self.onReceiveDecision[1], keeperActual[kIndex].noisy_pos)
        vector = kUtil.getVector(self.noisy_pos, midPoint)
        minDist = min(self.maxPlayerSpeed, kUtil.getDist(self.noisy_pos, midPoint))
        self.worldRef.moveAttempt(self, (vector, minDist))
        
    def receive(self):
        if self.inPosession == True:
            print "you're not supposed to be receiving you idiot, you have the ball!!!!!"
            return
        if self.agentListIndex == self.onReceiveDecision[0]: #this is the agent to go to ball
            if self.worldRef.fieldBall.inPosession == False:
                self.goToBall()
            else:
                self.getOpen()
        else:
            self.getOpen() #get open with respect to this 
        
    #this function is for saving the training data
    #if you have multiple agents, make the inputAgent string
    #the name of the agent. So sarsa will be "sarsa_agent" or something
    #the name is the object name, such as "dict" or whatever
    def save_obj(self, obj, name, index , inputAgent):
        with open(inputAgent+'Obj/%d/'%index + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    
    #this function is for loading the training data
    #if you have multiple agents, make the inputAgent string
    #the name of the agent. So sarsa will be "sarsa_agent" or something
    def load_obj(self, name, index, inputAgent ):
        fileExists = os.path.isfile(inputAgent+'obj/%d/'%index + name + '.pkl') 
        if(fileExists):
            with open(inputAgent+'obj/%d/'%index + name + '.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            return None
    
    def getNoisyMidPoint(self):
        return( (self.noisy_pos[0] + self.worldRef.agent_block_size) / 2.0 , (self.noisy_pos[1] + self.worldRef.agent_block_size) / 2.0 )
    def getTrueMidPoint(self):
        return( (self.true_pos[0] + self.worldRef.agent_block_size) / 2.0 , (self.true_pos[1] + self.worldRef.agent_block_size) / 2.0 )
    def getNoisyBallMid(self):
        return ((self.noisyBallPos[0] + self.worldRef.ball_block_size)/2, (self.noisyBallPos[1] + self.worldRef.ball_block_size)/2)
    
    #use this if you're sorting the agents for the purpose
    #of getting the state variables
    def __lt__(self, other):
        if self.onReceiveDecision == None:
            return kUtil.getDist(self.noisy_pos, self.noisyBallPos) < kUtil.getDist(other.noisy_pos, other.noisyBallPos)
        else:
            return kUtil.getDist(self.noisy_pos, self.onReceiveDecision[1]) < kUtil.getDist(other.noisy_pos, other.onReceiveDecision[1])
    
    
    
    
class testingCode(unittest.TestCase):
    #test case where you're at 45 degrees, and you rotate to 40 and 50 degrees
    def test_rotated_vectors(self):
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        #intialize agent to position 25,25 with no noise/error, as a keeper, with (357/2, 550/2) as center of field,
        #and 2 as agent speed, and 3 as ball speed
        Agent = agent(keepAwayWorld,(25, 25), 0.0, "keeper", (357/2, 550/2), 2, 3)
        cos5 = math.cos(5.0 * math.pi / 180) #cosine of 3 degress. angle needs to be in radians
        #Agent.receiveListOfOtherPlayers(self.keeperArray, self.takerArray, i)
        testBall = ball.ball((25,25), 3, True)
        Agent.receiveBallReference(testBall)
        v = kUtil.getVector(Agent.true_pos, (30, 30)) #a vector whose angle is 45 degrees
        answer = Agent.getRotatedVectors(v, cos5)
        correctAnswer1 = [((math.cos(50 * math.pi / 180)), (math.sin(50 * math.pi/180))),
                          ((math.cos(40 * math.pi / 180)), (math.sin(40 * math.pi/180)))]
        """
        print "answer"
        print answer
        print "correct"
        print correctAnswer1
        """
        for i in range(len(correctAnswer1)):
            for j in range(len(correctAnswer1[i])):
                str1 = "failed at: i = %d "%i
                str2 = "j = %d" %j
                strend = str1 + str2
                self.assertAlmostEqual(answer[i][j], correctAnswer1[i][j], msg=strend)
    
    #test case where you're at 0 degrees, and you rotate to 5 degrees and - 5 degrees 
    def test_rotated_vectors2(self):
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        #intialize agent to position 25,25 with no noise/error, as a keeper, with (357/2, 550/2) as center of field,
        #and 2 as agent speed, and 3 as ball speed
        Agent = agent(keepAwayWorld,(25, 25), 0.0, "keeper", (357/2, 550/2), 2, 3)
        print "These are the cosines of interest, printed in ", self 
        print Agent.cosinesOfInterest 
        cos5 = math.cos(5.0 * math.pi / 180) #cosine of 3 degress. angle needs to be in radians
        #Agent.receiveListOfOtherPlayers(self.keeperArray, self.takerArray, i)
        testBall = ball.ball((25,25), 3, True)
        Agent.receiveBallReference(testBall)
        v = kUtil.getVector(Agent.true_pos, (25, 30)) #a vector whose angle is 0 degrees
        answer = Agent.getRotatedVectors(v, cos5)
        correctAnswer1 = [((math.sin(5 * math.pi / 180)), (math.cos(5 * math.pi/180))),
                          ((math.sin(-5 * math.pi / 180)), (math.cos(-5 * math.pi/180)))]
        for i in range(len(correctAnswer1)):
            for j in range(len(correctAnswer1[i])):
                str1 = "failed at: i = %d "%i
                str2 = "j = %d" %j
                strend = str1 + str2
                self.assertAlmostEqual(answer[i][j], correctAnswer1[i][j], msg=strend)
                
    #UNIT TESTED with display height = 357, display width = 550
    #go and test the function that initializes that get open points
    def test_get_open_initial_points(self):
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        #intialize agent to position 25,25 with no noise/error, as a keeper, with (357/2, 550/2) as center of field,
        #and 2 as agent speed, and 3 as ball speed
        testAgent = agent(keepAwayWorld,(25, 25), 0.0, "keeper", (357/2, 550/2), 2, 3)
        #print "display height: ", testAgent.worldRef.display_height
        rows = [53.55, 103.53, 153.51, 203.49, 253.47]
        cols = [82.5, 159.5, 236.5,  313.5, 390.5]
        testPoints = testAgent.getOpenPoints
        for i in range(len(rows)):
            for j in range(len(cols)):
                testPoint = testPoints[i * len(rows) + j]
                self.assertAlmostEqual(testPoint[0], rows[i])
                self.assertAlmostEqual(testPoint[1], cols[j])
    def testCosinesOfInterest(self):
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        Agent = agent(keepAwayWorld,(25, 25), 0.0, "keeper", (357/2, 550/2), 2, 3)
        anglesToTest = list(range(5, Agent.terminalPassAngle, Agent.passAngleGranularity))
        print "these are the angls to test:" 
        print anglesToTest 
        for i in range(len(Agent.cosinesOfInterest)):
            self.assertAlmostEqual(Agent.cosinesOfInterest[i], math.cos(anglesToTest[i] * math.pi / 180) )
        
        


if __name__ == "__main__":
    print  'Unit Testing' 
    unittest.main()