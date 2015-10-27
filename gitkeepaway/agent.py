import kUtil, pickle
import os.path

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
        
    #used only in keepaway.py
    def receiveBallReference(self, inputBall):
        self.fieldBall = inputBall
    
    #this function will only be used by keepaway.py to update some initial variables that couldn't be updated
    #in __init__
    def receiveListOfOtherPlayers(self,  keeperArray, takerArray,index):
        self.takerArray = takerArray
        self.keeperArray = keeperArray
        self.agentListIndex= index #index in either the taker list or keeper list
    #used only in keepaway.py
    def receiveStateVariables(self, variables):
        self.stateVariables = variables
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
        else:
            #you have a taker
            V = kUtil.getVector(self.noisy_pos, self.noisyBallPos)
        self.worldRef.moveAttempt(self, (V, self.maxPlayerSpeed))
        #return (V, self.maxPlayerSpeed)
        
    
    #just hold your ground and return        
    def holdBall(self):
        if self.fieldBall == None:
            print("ERROR: trying to hold ball without actually having  ball")
        return
    
    #only keeper 0 will have this option available
    def passBall(self, integerK):
        #if you're passing to integerK = 1, then that means pass to the keeper that's closer to you
        #if you're passing ot integerK = 2, then that means pass to the keeper that's farther to you
        #0 is an invalid input
        sortedKeepers = sorted(self.keeperArray)
        if integerK == 0:
            print("Invalid input for integerK! integerK not allowed to be", integerK)
            return
        if self.fieldBall == None:
            print("ERROR: trying to hold ball without actually having  ball")
            return
        
        #pass to team mate integerK. if integerK = 1, then it's the 2nd element in array
        selfToTeammateDirection = kUtil.unitVector(kUtil.getVector(self.noisyBallPos, sortedKeepers[integerK].noisy_pos))
        selfToTeammateVector = (kUtil.scalarMultiply(self.fieldBall.maxBallSpeed, selfToTeammateDirection))
        #set ball's possesion to false, and update to new point. ball class handles direction vector
        self.fieldBall.updatePosession(False)
        self.inPosession = False
        self.isKicking = True
        #kUtil.addVectorToPoint(self.fieldBall.trueBallPos, selfToTeammateVector)
        self.fieldBall.update(selfToTeammateVector)
        #self.fieldBall.updatepos( kUtil.addVectorToPoint(self.fieldBall.true_pos, selfToTeammateVector ) )
        return (selfToTeammateDirection, self.maxBallSpeed)
        

            
    
    #respective position = the position you're trying to get open to
    #the keeper is the keeper is the keeper who's trying to find the best position
    #output: return a vector in the direction that's best, going from keeper true position, to optimal point
    #def getOpen(self,keeper, respectivePos):
    def getOpen(self, respectivePos):
        keeper = self
        stepIncrease = 5
        maximum = -9999
        #the threshold is compared to cosTheta. so 0 means the windows has to be at least 90 degrees. 
        #1.0 is most flexible value as it's saying the angle has to be at least 0
        threshold = 0.9
        maxPoint = None
        tempmaximum = -9999
        tempmaxPoint = None
        playersToIterate = []
        for isKeeper in self.keeperArray:
            if isKeeper != self:
                playersToIterate.append(isKeeper)
        for taker in self.takerArray:
            playersToIterate.append(taker)
                
        pointsToIterate = [(self.true_pos[0],self.true_pos[1]+stepIncrease),
                            (self.true_pos[0]+stepIncrease,self.true_pos[1]),
                            (self.true_pos[0]+stepIncrease,self.true_pos[1]+stepIncrease),
                            (self.true_pos[0]-stepIncrease,self.true_pos[1]-stepIncrease),
                            (self.true_pos[0]-stepIncrease,self.true_pos[1]),
                            (self.true_pos[0],self.true_pos[1]-stepIncrease),
                            (self.true_pos[0]-stepIncrease,self.true_pos[1]+stepIncrease),
                            (self.true_pos[0]+stepIncrease,self.true_pos[1]-stepIncrease),]
            
        for point in pointsToIterate:
            if kUtil.cosTheta(point, respectivePos, self.takerArray[0].true_pos)>threshold and kUtil.cosTheta(point, respectivePos, self.takerArray[1].true_pos)>threshold:
                spar = 0
                for player in playersToIterate:
                    spar += kUtil.getDist(player.true_pos, point)
                    
                if spar>tempmaximum:
                    tempmaximum = spar
                    tempmaxPoint = point
                continue
            else:
                spar = 0
                for player in playersToIterate:
                    spar += kUtil.getDist(player.true_pos, point)
                    
                if spar>maximum:
                    maximum = spar
                    maxPoint = point
            
        if maxPoint == None:
            #print("no open position available for agent #", self.agentListIndex + 1)
            maxPoint = tempmaxPoint
                
        #return (kUtil.getVector(keeper.true_pos, maxPoint),stepIncrease)
        self.worldRef.moveAttempt(self, (kUtil.getVector(keeper.true_pos, maxPoint), self.maxPlayerSpeed))
    
    def blockPass(self, kIndex):
        #kIndex is ordered based on who is the closest keeper
        keeperActual = sorted(self.keeperArray)
        midPoint = kUtil.getMidPoint(keeperActual[0].noisy_pos, keeperActual[kIndex].noisy_pos)
        vector = kUtil.getVector(self.noisy_pos, midPoint)
        self.worldRef.moveAttempt(self, (vector, self.maxPlayerSpeed))
        
    def receive(self):
        if self.inPosession == True:
            print("you're not supposed to be receiving you idiot, you have the ball!!!!!")
            return
        if self.agentListIndex == self.onReceiveDecision[0]: #this is the agent to go to ball
            self.goToBall()
        else:
            self.getOpen(self.onReceiveDecision[1]) #get open with respect to this 
        
    def save_obj(self, obj, name, index , inputAgent):
        with open(inputAgent+'Obj/%d/'%index + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, name, index, inputAgent ):
        fileExists = os.path.isfile(inputAgent+'obj/%d/'%index + name + '.pkl') 
        if(fileExists):
            with open(inputAgent+'obj/%d/'%index + name + '.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            return None
    #use this if you're sorting the agents for the purpose
    #of getting the state variables
    def __lt__(self, other):
        return kUtil.getDist(self.noisy_pos, self.noisyBallPos) < kUtil.getDist(other.noisy_pos, other.noisyBallPos)