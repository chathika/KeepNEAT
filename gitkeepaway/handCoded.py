from agent import agent
import kUtil

class handCoded(agent):
    def __init__(self, worldRef, pos, sigma, agentType, trueBallPos,maxPlayerSpeed, maxBallSpeed, posession = False):
        agent.__init__(self, worldRef, pos, sigma, agentType, trueBallPos, maxPlayerSpeed, maxBallSpeed, posession)
        #I'm using these for some stupid hand coded decisions.
        #delete these when coming up with intelligent agents
        #TODO: FILL as needed for qlearning
        self.agent_block_size = 23
        self.thresh = 100
        
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
            else:#TODO
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
                
                
                