"""
This module contains the handCoded agent class. 
"""
import agent
from numpy import arccos

class handCoded(agent.agent):
    """
    This class is a child of the agent class, and therefore inherits all 
    of agent's methods. This child class will simply over ride the 
    decisionFunction, which is responsible for making the ballholder 
    decide if it should hold the ball, or pass to a team mate. And if
    passing to a team mate, which team mate to pass to. The hand coded
    agent will use a deterministic policy. 
    """
    def __init__(self, worldRef, simIndex, noisyPos, sigma, agentType, noisyBallPos,maxPlayerSpeed, maxBallSpeed, posession = False):
        agent.agent.__init__(self, worldRef, simIndex, noisyPos, sigma, agentType, noisyBallPos, maxPlayerSpeed, maxBallSpeed, posession)

    
    def _decisionFunction(self):
        """
        This is a hand coded policy for deciding on holding the ball, or which team 
        member to pass to. The logic of this decision function is based very heavily 
        on "Algorithm 1 Pass:Hand-coded", which is created and implemented by the 
        researchers who published this paper:
        
        http://www.cs.utexas.edu/users/pstone/Papers/bib2html-links/LNAI09-kalyanakrishnan-1.pdf
        """
        #THIS IS WHERE THE INTELLIGENT AGENT CODE MAKES DECISION
        #since this is the hand coded extension, I'm just going to hard code some stuff
        #q learning and Sarsa should hopefully do better
                
        #this is some other hand coded stuff that you read in stone's paper
        c1 = 64 #c1 = distance in pixels
        c2 = 2.5#c2 = something to multiply angle by
        c3 = 77 #c3 is the number of pixels you assume are in 5 meteres
        #state variable 7 is distance in pixels from K1 to T1
        if self.stateVariables[7] > c1:
            self._holdBall()
        else:
            passMax = float("-Inf")
            passMaxArg = None
            for i in range(1,3):
                var = (c2 * arccos(self.stateVariables[10+i])) + (self.stateVariables[8+i] / c3)
                """
                print("var = ", var)
                print("stateVariable[", 10 + i, "]=", self.stateVariables[10+i] )
                print("arccos of stateVariable[", 10 + i, "]=", arccos(self.stateVariables[10+i]) )
                print("stateVariable[", 8 + i, "]=", self.stateVariables[8+i] )
                """
                        
                if var > passMax:
                    passMax = var
                    passMaxArg = i
            self._passBall(passMaxArg)
        

                        

                
                