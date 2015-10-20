"""
This module contains the hyperNEAT agent class. 
"""
import agent

class NEAT(agent.agent):
    """
    This class is a child of the agent class, and therefore inherits all 
    of agent's methods. This child class will simply over ride the 
    decisionFunction, which is responsible for making the ballholder 
    decide if it should hold the ball, or pass to a team mate. And if
    passing to a team mate, which team mate to pass to. The hyperNEAT 
    agent will use the same simple state variables as the hand coded agent.
    """
    def __init__(self, worldRef, simIndex, noisyPos, sigma, agentType, noisyBallPos,maxPlayerSpeed, maxBallSpeed, posession = False):
        agent.agent.__init__(self, worldRef, simIndex, noisyPos, sigma, agentType, noisyBallPos, maxPlayerSpeed, maxBallSpeed, posession)

    
    def _decisionFunction(self):
        """
        This is where Magic Happens
        """
        return
        

                        

                
                