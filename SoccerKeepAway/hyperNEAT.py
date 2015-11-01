"""
This module contains the hyperNEAT agent class. 
"""
import agent, kUtil
import numpy as np
import MultiNEAT as NEAT

class hyperNEAT(agent.agent):
	"""
	This class is a child of the agent class, and therefore inherits all 
	of agent's methods. This child class will simply over ride the 
	decisionFunction, which is responsible for making the ballholder 
	decide if it should hold the ball, or pass to a team mate. And if
	passing to a team mate, which team mate to pass to. The hyperNEAT 
	agent will use the agent's self.birdsEyeView as the feature input
	"""
	def __init__(self, worldRef, simIndex, noisyPos, sigma, agentType, noisyBallPos,maxPlayerSpeed, maxBallSpeed, posession = False):
		agent.agent.__init__(self, worldRef, simIndex, noisyPos, sigma, agentType, noisyBallPos, maxPlayerSpeed, maxBallSpeed, posession)
		self.NN = None


	def receiveNN(self, NN):
		self.NN = NN
		
	#hyperNEAT has it's own passball function which will override the default
	def _passBall(self, pointToPassTo):
		"""
		If a keeper currently has the ball, then it has the option to hold the ball,
		or pass it. Call this function to pass the ball. pointToPassTo is the coordinate that
		the keeper can pass to. these are pixel values 
		
		:param pointToPassTo: the tile that the agent is passing to. It is an XY coordinate defined to be the top left 
			corner of the tile you're trying to pass to
		
		:type pointToPassTo: typle of int
		
		:returns: no return 
		"""
		if self.fieldBall == None:
			print("ERROR: trying to hold ball without actually having  ball")
			return
		
		#pass to team mate integerK. if integerK = 1, then it's the 2nd element in array
		selfToTargetDirection = kUtil.unitVector(kUtil.getVector(self.__getBallCenter(self.noisyBallPos), pointToPassTo))
		selfToTargetVector = (kUtil.scalarMultiply(self.fieldBall.maxBallSpeed, selfToTargetDirection))

				
		#at this point, you've determined the angle you wanna pass, and you pass.
		#set ball's possesion to false, and update to new point. ball class handles direction vector
		self.fieldBall.updatePosession(False)
		self.inPosession = False
		self.isKicking = True
		#kUtil.addVectorToPoint(self.fieldBall.trueBallPos, selfToTeammateVector)
		self.fieldBall.updateDirection(kUtil.getNoisyVals(selfToTargetVector, self.getSigma()))
		
	def __getBallCenter(self, ballTopLeft):
		return ( ballTopLeft[0] + (self.worldRef.get_ball_block_size()/2) , ballTopLeft[1] + (self.worldRef.get_ball_block_size()/2))

	def _decisionFunction(self):
		"""
		This is where Magic Happens
		"""
		#print("Entering decision function")
		self.NN.Flush()
		self.NN.Input(np.array(self.bevList)) # can input numpy arrays, too
			                          # for some reason only np.float64 is supported
		#for _ in range(2):
		self.NN.Activate()
		o = self.NN.Output()

		#print(len(o))

		out,i = max([(x,y) for y,x in enumerate(o)])

		if i==0:
			self._holdBall()
		elif i==1:
			self._passBall( (self.worldRef.get_display_height() / 2 , self.worldRef.get_display_width() / 2) )
		else:
			self._passBall((self.worldRef.get_display_height() / 2 , self.worldRef.get_display_width() / 2))

		#print("The decision is: ",i)

		return


	def receiveBest(self, NN):
		self.NN = NN


