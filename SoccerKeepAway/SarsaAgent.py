import collections
import random
from keepAway import keepAway
import pygame
from agent import agent
import kUtil

class SarsaAgent(agent):
    def __init__(self, worldRef, pos, sigma, agentType, trueBallPos,maxPlayerSpeed, maxBallSpeed, epsilon=0.8,alpha=0.2,discount=0.9, posession = False):
        agent.__init__(self, worldRef, pos, sigma, agentType, trueBallPos, maxPlayerSpeed, maxBallSpeed, posession)
        #I'm using these for some stupid hand coded decisions.
        #delete these when coming up with intelligent agents
        self.agent_block_size = 23
        self.thresh = 100
 
        self.q_values = collections.defaultdict(int)
        self.epsilon = float(epsilon) #(exploration prob)
        self.alpha = float(alpha) #(learning rate)
        self.discount = float(discount) #(discount rate)
        self.start = (self.startx, self.starty)
        self.end = (self.goalx, self.goaly)
        self.isStochastic = True
        
    def setEpsilon(self, epsilon):
        self.epsilon = epsilon

    def setLearningRate(self, alpha):
        self.alpha = alpha

    def setDiscount(self, discount):
        self.discount = discount               

    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        #return dictionary
        return self.q_values[(state,action)]
    
    def getAllQvalues(self):
        returnList= []
        for i in range(self.numRows):
            temp = []
            returnList.append(temp)
            for j in range(self.numCols):
                temp2 = []
                returnList[i].append(temp2)
                returnList[i][j].append(self.getQValue((i,j), "up"))
                returnList[i][j].append(self.getQValue((i,j), "down"))
                returnList[i][j].append(self.getQValue((i,j), "left"))
                returnList[i][j].append(self.getQValue((i,j), "right"))
        return returnList

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        actions=self.getLegalActions()
        if len(actions)==0:
            return 0.0
        else:
            value=-9999
            for action in actions:
                temp=self.getQValue(state,action)
                if temp>value:
                    value=temp
        return value
    
    def computeRandomQvalue(self,state):
        """
          Returns action Q(state,action)  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        actions=self.getLegalActions()
        if len(actions)==0:
            return 0.0
        else:
            if random.random() <= self.epsilon:
                action = random.choice(actions)
                value = self.getQValue(state,action)
            else:
                value = self.computeValueFromQValues(state)
        return value

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        actions=self.getLegalActions()
        if len(actions)==0:
            return 0.0
        else:
            value=-9999
            for action in actions:
                temp=self.getQValue(state,action)
                if temp>value:
                    value=temp
                    a=action
        return a

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

        """
        # Pick Action
        legalActions = self.getLegalActions()
        action = None
        if len(legalActions)!=0:
            if random.random() <= self.epsilon:
                action=random.choice(legalActions)
            else:
                action=self.computeActionFromQValues(state)

        return action

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          """
        self.q_values[(state,action)]=((1-self.alpha)*(self.q_values[(state,action)]))+((self.alpha)*(reward+(self.discount*self.computeRandomQValues(nextState))))
        return self.q_values[(state,action)]

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)
    
    def isRandPosInBlock(self):
        row = int(self.agentx /self.block_size)
        col = int(self.agenty /self.block_size)
        if self.worldDescription[row][col] == 0:
            return False
        elif self.worldDescription[row][col]== 1:
            return True
        else:
            print("error in isRandPosInBlock function")
            return True

    def training(self):
        state = self.start
        numTraining = 800
        count = 0
        while count <= numTraining:
            print("Current episode: ", count)
            iterations = 0
            """"
            if count%16 == 0:
                self.agentx = self.startx * self.block_size
                self.agenty = self.starty * self.block_size
            """
            randPosInBlock = True
            while randPosInBlock == True:
                self.agentx = random.randint(0, self.numRows - 1) * self.block_size
                self.agenty = random.randint(0, self.numCols - 1) * self.block_size
                randPosInBlock = self.isRandPosInBlock()
        
            while self.isGoal()== False:
                action = self.getAction(state)
                for i in range(int(self.block_size / self.stepSize)):
                    self.agentx, self.agenty = self.moveAttempt(action, self.agentx, self.agenty, self.pointsHistory)
                nextState = self.getState()
                reward = self.getReward(nextState)
                self.update(state,action,nextState,reward)
                state = nextState
                iterations +=1
                if iterations % 100 == 0:
                    self.printQVals(self.getAllQvalues(), False)
            #self.setLearningRate(self.alpha + 0.001)
            #self.setEpsilon(self.epsilon - 0.004)
            self.printQVals(self.getAllQvalues(), False)
            count += 1
            #print(self.getQValue((7,5), "down"))
            

    def testing(self):
        self.setEpsilon(0.0)
        state = self.start
        self.agentx = self.startx * self.block_size
        self.agenty = self.starty * self.block_size
        self.pointsHistory = []
        self.pointsHistory.append((self.agentx, self.agenty))
        while self.isGoal()== False:
            action = self.getAction(state)
            self.agentx, self.agenty = self.moveAttempt(action, self.agentx, self.agenty, self.pointsHistory)
            self.printQVals(self.getAllQvalues(), True)
            """
            print()
            print("Comparision")
            print(state, ", " , self.getQValue(state, "up"))
            print(len(self.getAllQvalues()))
            print(len(self.getAllQvalues()[0] ))
            print(len(self.getAllQvalues()[0][0] ))
            print(state, ", ", self.getAllQvalues()[ state[0] ][ state[1] ][0])
            """
            state = self.getState()
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exitSim()
            #self.clock.tick(self.fps)
        
        #self.finish()
        
    def decisionFlowChart (self):
        if (self.agentType == "taker"):
            #taker closest to ball will go to ball.
            #state variables 7 and 8 contain the distances from T1 to K1 and T2 to K2 respectively
            if (self.stateVariables[7] < self.stateVariables[8] ):
                #taker 1 is closer
                closerTaker = 0
            else:
                closerTaker = 1
            takerActual = sorted(self.takerArray)
            if (self.agentListIndex == takerActual[closerTaker].agentListIndex):
                #you're the closer taker so go for the ball
                self.goToBall()
            else:
                #you're the farther taker, so go and block pass to the closer keeper
                keeperActual = sorted(self.keeperArray)
                cos2 = kUtil.cosTheta(self.noisy_pos, keeperActual[0].noisy_pos, keeperActual[1].noisy_pos)
                cos3 = kUtil.cosTheta(self.noisy_pos, keeperActual[0].noisy_pos, keeperActual[2].noisy_pos)
                if cos2 > cos3:
                    #block keeper 2
                    self.blockPass(1)
                else:
                    self.blockPass(2)

        else:
            #the agent is a keeper
            if(self.inPosession == False):
                #deterministic stuff happens here
                self.receive()
            else:
                #THIS IS WHERE THE INTELLIGENT AGENT CODE MAKES DECISION
                #since this is the hand coded extension, I'm just going to hard code some stuff
                #q learning and Sarsa should hopefully do better
                agentMidPoint = kUtil.addVectorToPoint(self.noisy_pos, (self.agent_block_size/2, self.agent_block_size/2))
                taker1Midpoint = kUtil.addVectorToPoint(self.takerArray[0].noisy_pos, (self.agent_block_size/2, self.agent_block_size/2))
                taker2Midpoint = kUtil.addVectorToPoint(self.takerArray[1].noisy_pos, (self.agent_block_size/2, self.agent_block_size/2))
                taker1Dist = kUtil.getDist(agentMidPoint, taker1Midpoint)
                taker2Dist = kUtil.getDist(agentMidPoint, taker2Midpoint)
                if (taker1Dist > self.thresh) and taker2Dist > self.thresh:
                    self.holdBall()
                else:
                    #passBall
                    keeperActual = sorted(self.keeperArray)
                    #pick the keeper with minimum cos value
                    if (self.stateVariables[11] < self.stateVariables[12]):
                        #k2 is a better option
                        print("pass to keeper 2")
                        self.passBall(1)
                    else:
                        print("pass to keeper 3")
                        self.passBall(2)


        
            
