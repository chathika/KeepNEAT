import kUtil, agent, ball, GetStateVars, handCoded, QlearningAgent, SarsaAgent
import pygame, sys, math, random
import unittest
from _pickle import load
pygame.init()




class keepAway():
    
    def __init__(self):
        mode = None #will be set to either monte carlo, q learning, sarsa, or manual control in the intro
        #RGB color
        self.white = (255,255,255) 
        self.black = (0,0,0)
        self.red = (255,0,0)
        self.green = (0,155,0)
        self.blue = (0,0,255)
            
        #give the game a title
        pygame.display.set_caption('Keepaway')
        self.keeperScore = 0
        self.displayGraphics = True
        
        #these are more or less global variables..
        #I'm not sure if this is bad or not. 
        self.worldImage = pygame.image.load('images/soccer_field.png')
        self.ballImage = pygame.image.load('images/ball.png')
        self.keeperImage = pygame.image.load('images/keeper.png')
        self.takerImage = pygame.image.load('images/taker.png')
        #block sizes are used for collision detection
        #only 1 size per element because all blocks are squares. block size = side length
        self.agent_block_size = 23
        self.ball_block_size = 12

        self.maxBallSpeed= 3
        self.maxPlayerSpeed = 2

        
        #dimensions of the game are the same as the soccer field image
        self.display_width = 550
        self.display_height = 357
        self.field_center = (self.display_width / 2 , self.display_height / 2)
        #gameDisplay is a pygame.surface object. it's your screen
        self.gameDisplay = pygame.display.set_mode((self.display_width,self.display_height))
        self.fps = 60 
        self.clock = pygame.time.Clock()
        
        types = ["keeper", "taker"]
        agentSigmaError = .01
        
        #start the ball kinda close to the keeper in the upper left corner
        self.fieldBall = ball.ball( (self.field_center[0]/4, self.field_center[1]/4), self.maxBallSpeed)
        
        #setup all the initial keepers and takers. They are all starting at different field positions, which is why
        #you can't have a for loop just iterate and declare all of them
        self.keeperArray = []
        self.keeperArray.append(agent.agent(self, (12.5, 12.5), agentSigmaError, types[0], self.field_center, self.maxPlayerSpeed, self.maxBallSpeed))
        self.keeperArray.append(agent.agent(self, (25,  self.display_width - 37.5), agentSigmaError, types[0], self.field_center, self.maxPlayerSpeed, self.maxBallSpeed))
        self.keeperArray.append(agent.agent(self, (self.display_height - 37.5,  self.display_width - 37.5), agentSigmaError, types[0], self.field_center, self.maxPlayerSpeed, self.maxBallSpeed))
        self.takerArray = []
        self.takerArray.append(agent.agent(self, (self.display_height - 25,  25), agentSigmaError, types[1], self.field_center, self.maxPlayerSpeed, self.maxBallSpeed))
        self.takerArray.append(agent.agent(self, (self.display_height - 37.5,  50), agentSigmaError, types[1], self.field_center, self.maxPlayerSpeed, self.maxBallSpeed))
        
        #3 different font sizes 
        self.smallfont = pygame.font.SysFont("comicsansms",25) #25 is font sizes
        self.medfont = pygame.font.SysFont("comicsansms",50) 
        self.largefont = pygame.font.SysFont("comicsansms",80) 
        self.verysmallfont = pygame.font.SysFont("comicsansms", 12)
        
    def displayScore(self):
        text= self.verysmallfont.render("Keeper Reward: "+ str(self.keeperScore), True, self.black)
        
        self.gameDisplay.blit(text, [0,0])        
    def pause(self, message):
        paused = True
        print(message)
        print("Press space to continue. Press E to exit")
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = False
                    elif event.key == pygame.K_e:
                        pygame.quit()
                        sys.exit(0)
            #gameDisplay.fill(white)
            self.clock.tick(10) 
        
    def isGameOver(self):
        #game is over when a taker obtains the ball
        #game is also over when the ball is kicked out of bounds
        for i in range(len(self.takerArray)):
            if self.takerArray[i].inPosession == True:
                return True
        #now check if ball is out of bounds:
        rowPixel1 = self.fieldBall.trueBallPos[0]
        colPixel1 = self.fieldBall.trueBallPos[1]
        
        #lower right coordinate of ball boundary
        rowPixel2 = rowPixel1 + self.ball_block_size
        colPixel2 = colPixel1 + self.ball_block_size    
        
        #check to see if you go outside the boundaries of the game    
        if rowPixel1 < 0 or colPixel1 < 0 or rowPixel2 > self.display_height or colPixel2 > self.display_width :  
            return True
        #If you made it here, then that means the game is still going
        return False
    
    #reset the game for another training episode
    def resetGameForTraining(self):
        #reset the ball variables
        row = random.randint(0, int(self.display_height/2))
        col = random.randint(int(self.display_width/4), int (self.display_width/4 * 3))
        self.fieldBall.updateCoordinate((row,col))
        self.fieldBall.update((0.0,0.0))
        
        #reset the score
        self.keeperScore = 0
        
        #now reset the agent variables:
        self.keeperArray[0].true_pos = (12.5, 12.5)
        self.keeperArray[1].true_pos = (25,  self.display_width - 37.5)
        self.keeperArray[2].true_pos = (self.display_height - 37.5,  self.display_width - 37.5)
        self.takerArray[0].true_pos = (self.display_height - 25,  25)
        self.takerArray[1].true_pos = (self.display_height - 37.5,  50)
        
        for i in range(len(self.keeperArray)):
            self.keeperArray[i].noisy_pos = kUtil.getNoisyVals(self.keeperArray[i].true_pos, self.keeperArray[i].sigma)
            self.keeperArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos,self.keeperArray[i].sigma)
            self.keeperArray[i].inPosession = False
            self.keeperArray[i].isKicking = False
            
        for i in range(len(self.takerArray)):
            self.takerArray[i].noisy_pos = kUtil.getNoisyVals(self.takerArray[i].true_pos, self.takerArray[i].sigma)
            self.takerArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.takerArray[i].sigma)
            self.takerArray[i].inPosession = False
            self.takerArray[i].isKicking = False
       
        
    
    """
    ***************The following is code for movement of the agents****************
    When it comes to movement, there are 4 different quadrants defined:
    1 0
    2 3
    quadrant 0 is from directions 0 degrees to 90 degrees
    quadrant 1 is from directions 90 degrees to 180 degrees
    quadrant 2 is from directions 180 degrees to 270 degrees
    quadrant 3 is from directions 270 degrees to 360 degrees
    The following code will determine if the move is legal, and
        will then let the agent move a step in that direction 
        if it is. The only time a move is illegal is if you step
        out of bounds
    If agent moves, the agents position will be updated everywhere
    """
    #the reversedPolarCoord = tuple of the form (noiseFreeDirectionVector, distance)
    def moveAttempt(self, inputAgent, reversedPolarCoord ):
        
        noiseFreeDirectionVector = reversedPolarCoord[0]
        distance = reversedPolarCoord[1]
        
        #for the purposes of finding legal moves, just assume that they player is trying
        #to cover the most amount of distance. Also, right now, it's not important if
        #noiseFreeDirectionVector is a unit vector or not
        quad = self.getQuadAttemptingToMoveTo(inputAgent, noiseFreeDirectionVector)
        setOfLegalQuads = self.getLegalQuadrants(inputAgent)
        #print(setOfLegalQuads)
        #print("quad:", quad)
        if quad in setOfLegalQuads:
            #move is legal, do it
            self.moveAgent(inputAgent, kUtil.scalarMultiply ( distance, kUtil.unitVector(noiseFreeDirectionVector)))
        else:
            #move is illegal. Simply return without calling or updating anything
            #print("Illegal move: ", reversedPolarCoord)
            return

    def moveAgent(self, inputAgent, movementVector):
        newNoiseFreePos = kUtil.addVectorToPoint(inputAgent.true_pos, movementVector)
        inputAgent.updateAgentPosition(newNoiseFreePos)    
        return inputAgent.true_pos

    def getQuadAttemptingToMoveTo(self, agent, noiseFreeDirectionVector):
        #noise free direction vector of the form (row, col), and row's graph axis is reversed in pygame. so multiply 
        #the row direction vector by -1.0
        y = noiseFreeDirectionVector[0]
        x = noiseFreeDirectionVector[1] 
        angleInRadians = math.atan2(y,x)
        #print("angleInRadians:", angleInRadians, " for y = ", y, "and x = ", x)
        quadrantToMoveTo = None
        if angleInRadians >= 0.0 and angleInRadians <= math.pi / 2.0:
            #this is quadrant 0
            quadrantToMoveTo = 0
        elif angleInRadians >= math.pi / 2.0 and angleInRadians <= math.pi :
            #this is quadrant 1
            quadrantToMoveTo = 1
        elif angleInRadians <= 0.0 and angleInRadians >= -1.0 * math.pi / 2.0 :
            #this is quadrant 3
            quadrantToMoveTo = 3
        elif angleInRadians <= -1.0 * math.pi / 2.0 and angleInRadians >= -1.0 * math.pi:
            #this is quadrant 2
            quadrantToMoveTo = 2
        return quadrantToMoveTo
        

    #a movement in any direction is legal except for when you're trying to go 
    #out of bounds. 
    def getLegalQuadrants(self, inputAgent):
        #the orthogonal directions that determine the validity of all other directions
        directions = ["up", "down", "left", "right"]
        #The quadrants that are illegal if the corresponding orthogonal direction is illegal
        bannedQuadrants = [set([2,3]), set([1,0]),set([1,2]), set([0,3])]
        
        #trivial case where the game is over and you return nothing
        if self.isGameOver():
            return None
        
        #initialize the return set
        returnSet = set()
        for i in range(len(directions)):
            returnSet.add(i)

        for i in range(len(directions)):
            if not self.isDirectionLegal(inputAgent, directions[i]):
                # this will execute if a move is ILLEGAL
                returnSet.difference_update(bannedQuadrants[i])
        return returnSet
    
    #this is a utility class for the getLegalDirections class
    def isDirectionLegal(self, inputAgent, direction):
        rowPixel1 = inputAgent.true_pos[0]
        colPixel1 = inputAgent.true_pos[1]
        #note, y axis is reversed in pygame: decrease Y axis to move UP, and vice versa
        if direction == "up":
            rowPixel1 -= self.maxPlayerSpeed
        elif direction == "down":
            rowPixel1 += self.maxPlayerSpeed
        elif direction == "right":
            colPixel1 += self.maxPlayerSpeed
        elif direction == "left":
            colPixel1 -= self.maxPlayerSpeed
        
        #lower right coordinate of robot boundary
        rowPixel2 = rowPixel1 + self.agent_block_size
        colPixel2 = colPixel1 + self.agent_block_size    
        
        #check to see if you go outside the boundaries of the game    
        if rowPixel1 < 0 or colPixel1 < 0 or rowPixel2 > self.display_height or colPixel2 > self.display_width :
            #print("upper left coordinates: ", (rowPixel1, colPixel1))  
            return False
        #if you're not outside boundaries, then it's a totally legal direction. It just might not be optimal
        else:
            return True
        
        
    """
    End the code that defines movement for agents
    """
    
    def exitSim(self):
        pygame.quit()
        sys.exit(0)
        
        #important function: print message to user
    def message_to_screen(self, msg, color, y_displace = 0, size = "small"):
        textSurface,textRect = self.text_objects(msg,color, size)
        textRect.center = (self.display_width/2), (self.display_height/2) + y_displace
        self.gameDisplay.blit(textSurface, textRect)
        
    def text_objects(self, text,color, size):
        if size == "small":
            textSurface = self.smallfont.render(text, True, color)
        elif size == "medium":
            textSurface = self.medfont.render(text, True, color)
        elif size == "large":
            textSurface = self.largefont.render(text, True, color)
        elif size == "verysmall":
            textSurface = self.verysmallfont.render(text,True,color)
        return textSurface, textSurface.get_rect()
    
  
        
    def finish(self):
        paused = True
        self.message_to_screen("Game Over, Final Score %d" %self.keeperScore, self.red, 0, "small")
        self.message_to_screen("Press Q to quit.",
                          self.red,
                          50)
        pygame.display.update()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exitSim()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.exitSim()
            #gameDisplay.fill(white)
            self.clock.tick(10)
                        
    
    def drawWorld (self):
        #note: for blit function, give it column, row instead of row, column
        self.gameDisplay.blit(self.worldImage, (0,0))
        for i in range(len(self.keeperArray)):
            self.gameDisplay.blit(self.keeperImage, (self.keeperArray[i].true_pos[1], self.keeperArray[i].true_pos[0]))
        for i in range(len(self.takerArray)):
            self.gameDisplay.blit(self.takerImage, (self.takerArray[i].true_pos[1], self.takerArray[i].true_pos[0]))
        self.gameDisplay.blit(self.ballImage, (self.fieldBall.trueBallPos[1], self.fieldBall.trueBallPos[0]))   
    

            
            
    def getState(self):
        rowPixelCenter = self.agentx + self.block_size / 2
        colPixelCenter = self.agenty + self.block_size/ 2
        row = rowPixelCenter / self.block_size
        col = colPixelCenter / self.block_size
        return (int(row), int(col))
    
    def updateScore(self):
        #for keeper in self.keeperArray:
            #if keeper.inPosession:
        self.keeperScore += 1
        return
    #This function checks for ball intersections, and then updates posession variables for agents and bal
    def updateBallPosession(self):      
        #check takers first. If they get the ball, GG, so return
        for i in range(len(self.takerArray)):
            if self.agentBallIntersection(self.takerArray[i]):
                self.takerArray[i].inPosession = True
                self.fieldBall.updatePosession(True)
                #print("taker ", i, "has ball at taker true coordinate:", self.takerArray[i].true_pos)
                #print("ball true corner coord range: ", self.fieldBall.trueBallPos, "to", (self.fieldBall.trueBallPos[0]+ self.ball_block_size, self.fieldBall.trueBallPos[1]+ self.ball_block_size))
                return
            else:
                self.takerArray[i].inPosession = False

        
        for i in range(len(self.keeperArray)):
        #for i in range(1):
            if self.keeperArray[i].isKicking == False:
                if self.agentBallIntersection(self.keeperArray[i]):
                    #case where keeper is NOT kicking, and ball and agent intersect
                    self.keeperArray[i].inPosession = True
                    self.fieldBall.updatePosession(True)
                    return
                #print("keeper ", i, "has ball at keeper true coordinate:", self.keeperArray[i].true_pos, " to ", (self.keeperArray[i].true_pos[0] + self.agent_block_size, self.keeperArray[i].true_pos[1] + self.agent_block_size) )
                #print("ball true corner coord range: ", self.fieldBall.trueBallPos, "to", (self.fieldBall.trueBallPos[0]+ self.ball_block_size, self.fieldBall.trueBallPos[1]+ self.ball_block_size))
            else:
                #this is the case where the agent IS kicking
                #check to see if the agent is intersecting the ball
                #if they are, leave keeper.isKicking = true
                #otherwise, you can now update it to False
                if self.agentBallIntersection(self.keeperArray[i]) == False:
                    self.keeperArray[i].isKicking = False
                self.keeperArray[i].inPosession = False
            
        #if you reached here, then it means that no one has the ball, so update accordingly
        #self.fieldBall.updatePosession(False, self.fieldBall.trueBallPos)
        self.fieldBall.updatePosession(False)
                
    #this is more or less a private fucntion of self.updateBallPosession()
    #check for the intersection of an agent and a ball
    def agentBallIntersection(self, inputAgent):
        #print()
        agentRadius = self.agent_block_size / 2
        ballRadius = self.ball_block_size / 2
        cutoff = agentRadius+ ballRadius
        agentMidPoint = kUtil.addVectorToPoint(inputAgent.true_pos, (self.agent_block_size/2, self.agent_block_size/2))
        ballMidPoint = kUtil.addVectorToPoint(self.fieldBall.trueBallPos, (self.ball_block_size/2, self.ball_block_size/2))
        #print("agent actual:", inputAgent.true_pos, "agentMid:", agentMidPoint)
        #print("agentMid:", agentMidPoint, " ballMid:", ballMidPoint)
        distBetweenMidPoints = kUtil.getDist(agentMidPoint, ballMidPoint)
        #print("Cutoff: ", cutoff, " actual Distance: ", distBetweenMidPoints)
        if (distBetweenMidPoints <= cutoff):
            return True
        else:
            return False

    def replaceAgents(self, inputClass):
        #replace the standard agents with the intelligent or hand coded agents
        for i in range(len(self.keeperArray)):
            tempKeeper = self.keeperArray[i]
            self.keeperArray[i] = inputClass(tempKeeper.worldRef, tempKeeper.true_pos, tempKeeper.sigma, tempKeeper.agentType, self.fieldBall.trueBallPos, self.maxPlayerSpeed, self.maxBallSpeed) 
        for i in range(len(self.takerArray)):
            tempTaker = self.takerArray[i]
            self.takerArray[i] = inputClass(tempKeeper.worldRef, tempTaker.true_pos, tempTaker.sigma, tempTaker.agentType, self.fieldBall.trueBallPos, self.maxPlayerSpeed, self.maxBallSpeed)    
        
        #once the other arrays are initialized, send references to all keepers and takers
        #you don't need to worry about other references. This function will only be called during initialization
        #also go and send over references to the ball                 
        for i in range(len(self.keeperArray)):
            self.keeperArray[i].receiveListOfOtherPlayers(self.keeperArray, self.takerArray, i)
            self.keeperArray[i].receiveBallReference(self.fieldBall)
        for i in range(len(self.takerArray)):
            self.takerArray[i].receiveListOfOtherPlayers(self.keeperArray, self.takerArray, i)
            self.takerArray[i].receiveBallReference(self.fieldBall)
    
    #send all the state variables to the keepers and takers
    def sendStateVars(self):
        #get the state variables
        currVars = GetStateVars.getStateVarsKeepers(self.keeperArray, self.takerArray, self.field_center)
        #send the state variables to each keeper and taker
        for i in range(len(self.keeperArray)):
            self.keeperArray[i].receiveStateVariables(currVars)
        for i in range(len(self.takerArray)):
            self.takerArray[i].receiveStateVariables(currVars)
    
    def calc_receive(self):
        if(self.fieldBall.trueBallDirection == (0.0, 0.0))== False:
            self.calc_receive_ball_moving()
        else:
            mimimum = 99999.0
            argmin = None
            for i in range(len(self.keeperArray)):
                temp = kUtil.getDist(self.fieldBall.trueBallPos, self.keeperArray[i].true_pos)
                if (temp < mimimum):
                    mimimum = temp
                    argmin = i
            rDecision = [argmin, self.fieldBall.trueBallPos]
            for i in range(len(self.keeperArray)):
                self.keeperArray[i].receiveDecision(rDecision)
            for i in range(len(self.takerArray)):
                self.takerArray[i].receiveDecision(rDecision)
            
    #go and calulcate the receive() information and send it over to the agents
    #you're only supposed to call this particular function if no one is in posession
    def calc_receive_ball_moving(self):
        #make sure that you're only doing this if
        for i in range(len(self.keeperArray)):
            if self.keeperArray[i].inPosession == True:
                rDecision = (i, self.keeperArray[i].true_pos)
                return
        for i in range(len(self.takerArray)):
            if self.takerArray[i].inPosession == True:
                return
            
        TA = kUtil.addVectorToPoint(self.fieldBall.trueBallPos, self.fieldBall.trueBallDirection)
        TB = self.fieldBall.trueBallPos
        minTime = 99999.0
        argmin = None
        bestPerpIntersect = None
        for i in range(len(self.keeperArray)):
            TC = self.keeperArray[i].true_pos
            if (kUtil.cosTheta(TA, TB, TC)) < 0:
                #print("Keeper " , i, " can't get to ball: the cosTheta is negetive.")
                #it's impossible for this keeper to get the ball
                continue
            else:
                pd = kUtil.getPerpDist(TA, TB, TC)
                pt = pd/self.maxPlayerSpeed
                normalVector = kUtil.getNormalVector(TA, TB, TC)
                perpIntersect = kUtil.addVectorToPoint(TC, normalVector)
                bd = kUtil.getDist(TB, perpIntersect)
                bt = bd/self.maxBallSpeed
                if pt > bt:
                    #keeper wont' be able be able to get to ball in time
                    #print("player ", i+1, "can't reach ball as pt:",pt," and bt: ",bt)
                    continue
                else:
                    #keeper CAN get to ball. can it get there soonest though?
                    #save the fastest keeper
                    if (pt < minTime):
                        minTime = pt
                        argmin = i
                        bestPerpIntersect = perpIntersect
        #at this point, if a keeper can get to the ball, the fastest and it's intercept are saved
        if (argmin != None):
            rDecision = [argmin, self.calcOptimal(self.keeperArray, argmin, bestPerpIntersect)]
            for i in range(len(self.keeperArray)):
                self.keeperArray[i].receiveDecision(rDecision)
            for i in range(len(self.takerArray)):
                self.takerArray[i].receiveDecision(rDecision)
        else:
            print("no argmin found. game about to crash for sure")
    def calcOptimal(self, agentList, i, intersect):
        V = kUtil.getVector(self.fieldBall.trueBallPos, intersect)
        UV = kUtil.unitVector(V)
        stepVector = kUtil.scalarMultiply(self.maxBallSpeed, UV)
        #keep adding the step vector to the optimal point
        optimalPoint = self.fieldBall.trueBallPos
        maxNumSteps = int(kUtil.getDist(self.fieldBall.trueBallPos, intersect)/ self.maxBallSpeed)
        stepCount = 0
        for k in range(maxNumSteps):
            optimalPoint = kUtil.addVectorToPoint(optimalPoint, stepVector)
            stepCount += 1
            currPd = kUtil.getDist(optimalPoint,agentList[i].true_pos)
            currBd = kUtil.getDist(self.fieldBall.trueBallPos, optimalPoint)
            currPt = currPd / self.maxPlayerSpeed
            currBt = currBd / self.maxBallSpeed
            if currPt < currBt:
                #found the optimal, so return it
                return optimalPoint
        #if you get here, then no closer optimal was found, so just return the intersect
        return intersect
    
    def QTraining(self,totalTraining):
        for training in range(totalTraining):
            print("Training number :",training)
            if training%100 == 0:
                self.displayGraphics = True
            else:
                self.displayGraphics = False
            self.resetGameForTraining()
            while self.isGameOver() == False:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameExit = True
                self.sendStateVars()
                reward = 100000
                for keeper in self.keeperArray:
                    keeper.updateReward(reward) 
                self.calc_receive()
                for keeper in self.keeperArray:
                    keeper.isInTraining = True
                    keeper.decisionFlowChart()
                for taker in self.takerArray:
                    taker.decisionFlowChart()
                    
                newBallPoint = kUtil.addVectorToPoint(self.fieldBall.trueBallPos, kUtil.scalarMultiply(self.maxBallSpeed, kUtil.unitVector(self.fieldBall.trueBallDirection)))
                self.fieldBall.updateCoordinate(newBallPoint)
                for i in range(len(self.takerArray)):
                    self.takerArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.takerArray[i].sigma)
                for i in range(len(self.keeperArray)):
                    self.keeperArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.keeperArray[i].sigma)                
                self.updateBallPosession()
                self.updateScore()
                if(self.displayGraphics == True):
                    self.drawWorld ()
                    self.displayScore()
                    pygame.display.update()
                if self.isGameOver():
                    reward = -100
                    self.sendStateVars()
                    for keeper in self.keeperArray:
                        keeper.updateFinalReward(reward)
                self.clock.tick(10000)
    
    
    def Qtesting(self):
        self.resetGameForTraining()
        while self.isGameOver() == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
            self.sendStateVars()
            self.calc_receive()
            for keeper in self.keeperArray:
                keeper.isInTraining = False
                keeper.decisionFlowChart()
            for taker in self.takerArray:
                taker.decisionFlowChart()
            
            newBallPoint = kUtil.addVectorToPoint(self.fieldBall.trueBallPos, kUtil.scalarMultiply(self.maxBallSpeed, kUtil.unitVector(self.fieldBall.trueBallDirection)))
            self.fieldBall.updateCoordinate(newBallPoint)
            for i in range(len(self.takerArray)):
                self.takerArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.takerArray[i].sigma)
            for i in range(len(self.keeperArray)):
                self.keeperArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.keeperArray[i].sigma)                
            self.updateBallPosession()
            self.updateScore()
            self.drawWorld ()
            self.displayScore()
            pygame.display.update()
            #this specifies frames per second
            self.clock.tick(self.fps)
    
        if self.isGameOver() == True:
            gameExit = True
        print("final score: ", self.keeperScore)

        self.finish()
        #self.pause("Game Over: Final Score %d" % self.keeperScore)
        self.exitSim()
    
    def game_intro(self):
        intro = True
        #display intro title to user
        if intro:
            self.gameDisplay.fill(self.white)
            self.message_to_screen("Welcome to Keep Away",
                              self.green,
                              -100,
                              "medium")  
            self.message_to_screen("Q for Q learning, ",
                              self.black,
                              80)        
            self.message_to_screen("S for SARSA, ",
                              self.black,
                              120)            
            self.message_to_screen("H for hand coded agent, or E to exit.",
                              self.black,
                              160) 
                              
            pygame.display.update()
        #while in the intro, check for user input on what type of model they wanna use
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exitSim()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        mode = "q_learning"
                        self.replaceAgents(QlearningAgent.QlearningAgent)
                        intro = False
                        return mode
                    if event.key == pygame.K_s:
                        mode = "sarsa"
                        self.replaceAgents(SarsaAgent.SarsaAgent)
                        intro = False
                        return mode
                    if event.key == pygame.K_h:
                        mode = "hand_coded"
                        self.replaceAgents(handCoded.handCoded)
                        intro = False
                        return mode
                    if event.key == pygame.K_m:
                        mode = "manual"
                        intro = False
                        return mode
                    if event.key == pygame.K_e:
                        self.exitSim()
                        
            self.clock.tick(5)
    
    def gameLoop(self, mode):
        self.drawWorld ()
        gameExit = False
        if(self.displayGraphics == True):
            pygame.display.update()
        experimentAgent = self.takerArray[0]
        #each occurance of this loop is treated as one simulation cycle
        while not gameExit:
            if(mode == "manual"):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameExit = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.moveAttempt(experimentAgent, ((0,-1), self.maxPlayerSpeed))
                        elif event.key == pygame.K_RIGHT:
                            self.moveAttempt(experimentAgent, ((0,1), self.maxPlayerSpeed))
                        elif event.key == pygame.K_UP:
                            self.moveAttempt(experimentAgent, ((-1,0), self.maxPlayerSpeed))
                        elif event.key == pygame.K_DOWN:
                            self.moveAttempt(experimentAgent, ((1,0), self.maxPlayerSpeed))
                        elif event.key == pygame.K_1:
                            self.moveAttempt(experimentAgent, ((-1,-1), self.maxPlayerSpeed))
                        elif event.key == pygame.K_2:
                            self.moveAttempt(experimentAgent, ((-1,1), self.maxPlayerSpeed))
                        elif event.key == pygame.K_3:
                            self.moveAttempt(experimentAgent, ((1,-1), self.maxPlayerSpeed))
                        elif event.key == pygame.K_4:
                            self.moveAttempt(experimentAgent, ((1,1), self.maxPlayerSpeed))
            elif (mode == "hand_coded"):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameExit = True
                self.sendStateVars()
                self.calc_receive()
                for keeper in self.keeperArray:
                    keeper.decisionFlowChart()
                for taker in self.takerArray:
                    taker.decisionFlowChart()
            elif(mode == "q_learning"):
                totalTraining = 5
                flag = False
                for index in range(len(self.keeperArray)):
                    if self.keeperArray[index].load_obj("dict",index, mode) == None:
                        flag = True
                if flag:
                    print("no files exist")
                    self.QTraining(totalTraining)
                
                    for index in range(len(self.keeperArray)):
                        self.keeperArray[index].save_obj(self.keeperArray[index].q_values,"dict",index, mode)
                        #for key in list(self.keeperArray[index].q_values.keys())[:10]:
                            #print("QValues of ",index," agent is: key=",key," value=",self.keeperArray[index].q_values[key])
                    
                    self.Qtesting()
                
                else:
                    print("files exist, continue training")
                    totalTraining = 0
                    for index in range(len(self.keeperArray)):
                        self.keeperArray[index].q_values = self.keeperArray[index].load_obj("dict",index, mode)
                        #for key in list(self.keeperArray[index].q_values.keys())[:10]:
                            #print("QValues of ",index," agent is: key=",key," value=",self.keeperArray[index].q_values[key])
                    
                    
                    
                    self.QTraining(totalTraining)
                    
                    for index in range(len(self.keeperArray)):
                        self.keeperArray[index].save_obj(self.keeperArray[index].q_values,"dict",index, mode)
                        
                    self.Qtesting()
                    
                                        
            elif(mode == "sarsa"):
                totalTraining = 5
                flag = False
                for index in range(len(self.keeperArray)):
                    if self.keeperArray[index].load_obj("dict",index, mode) == None:
                        flag = True
                if flag:
                    print("no files exist")
                    self.QTraining(totalTraining)
                
                    for index in range(len(self.keeperArray)):
                        self.keeperArray[index].save_obj(self.keeperArray[index].q_values,"dict",index, mode)
                        #for key in list(self.keeperArray[index].q_values.keys())[:10]:
                            #print("QValues of ",index," agent is: key=",key," value=",self.keeperArray[index].q_values[key])
                    
                    self.Qtesting()
                
                else:
                    print("files exist, continue training")
                    totalTraining = 0
                    for index in range(len(self.keeperArray)):
                        self.keeperArray[index].q_values = self.keeperArray[index].load_obj("dict",index, mode)
                        #for key in list(self.keeperArray[index].q_values.keys())[:10]:
                            #print("QValues of ",index," agent is: key=",key," value=",self.keeperArray[index].q_values[key])
                    
                    
                    
                    self.QTraining(totalTraining)
                    
                    for index in range(len(self.keeperArray)):
                        self.keeperArray[index].save_obj(self.keeperArray[index].q_values,"dict",index, mode)
                        
                    self.Qtesting()
                    
                                        
                
            #this is common code that will occur regardless of what agent you picked
            #if (self.fieldBall.inPosession == False):
            newBallPoint = kUtil.addVectorToPoint(self.fieldBall.trueBallPos, kUtil.scalarMultiply(self.maxBallSpeed, kUtil.unitVector(self.fieldBall.trueBallDirection)))
            self.fieldBall.updateCoordinate(newBallPoint)
            for i in range(len(self.takerArray)):
                self.takerArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.takerArray[i].sigma)
            for i in range(len(self.keeperArray)):
                self.keeperArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.keeperArray[i].sigma)                
            self.updateBallPosession()
            self.updateScore()
            self.drawWorld ()
            self.displayScore()
            pygame.display.update()
            
            if self.isGameOver() == True:
                gameExit = True
                print("final score: ", self.keeperScore)
            #this specifies frames per second
            self.clock.tick(self.fps)
        self.finish()
        #self.pause("Game Over: Final Score %d" % self.keeperScore)
        self.exitSim()

         
class testingCode(unittest.TestCase):
    
    def testInit(self):
        keepaway = keepAway()
        self.assertEqual(keepaway.fieldBall.trueBallPos, (275.0/4, 178.5/4))


if __name__ == "__main__":
    print ('Unit Testing')
    unittest.main()
