"""
This module contains the hyperNEAT agent class. 
"""
import agent
import numpy as np
import MultiNEAT as NEAT

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
		self.NN = None
		#self.bestNN = None


	def receiveNN(self, NN):
		self.NN = NN

	def _decisionFunction(self):
		"""
		This is where Magic Happens
		"""
		#print("Entering decision function")
		self.NN.Flush()
		self.NN.Input(np.array(self.stateVariables+(1,))) # can input numpy arrays, too
														# for some reason only np.float64 is supported
		for _ in range(2):
			self.NN.Activate()
		o = self.NN.Output()

		#print(len(o))
	
		out,i = max([(x,y) for y,x in enumerate(o)])
	
		if i==0:
			self._holdBall()
		elif i==1:
			self._passBall(1)
		else:
			self._passBall(2)

		#print("The decision is: ",i)

		return
	

	def receiveBest(self, NN):
		self.NN = NN

