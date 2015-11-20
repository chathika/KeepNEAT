"""
This module contains the hyperNEAT agent class. 
"""
import agent, kUtil
import numpy as np
import MultiNEAT as MNEAT
import os.path

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
		fileExists = os.path.isfile('HyperNEAT_Population/genome.txt')
		if fileExists:
			substrate = MNEAT.Substrate(worldRef.bev_substrate,
                           [],
                           worldRef.bev_substrate)
			substrate.m_allow_input_hidden_links = False
			substrate.m_allow_input_output_links = True
			substrate.m_allow_hidden_hidden_links = False
			substrate.m_allow_hidden_output_links = False
			substrate.m_allow_output_hidden_links = False
			substrate.m_allow_output_output_links = False
			substrate.m_allow_looped_hidden_links = False
			substrate.m_allow_looped_output_links = False

			substrate.m_link_threshold = 0.2
			substrate.m_max_weight_and_bias = 8.0

			substrate.m_with_distance = True;

			g = MNEAT.Genome('HyperNEAT_Population/genome.txt')
			self.NN = MNEAT.NeuralNetwork()
			g.BuildHyperNEATPhenotype(self.NN, substrate)
		else:
			self.NN = None
		#self.bestNN = None


	def receiveNN(self, NN):
		self.NN = NN
	
	#hyperNEAT has it's own passball function which will override the default
	def _passBall(self, pointToPassTo):
		'''
		If a keeper currently has the ball, then it has the option to hold the ball,
		or pass it. Call this function to pass the ball. pointToPassTo is the coordinate that
		the keeper can pass to. these are pixel values 

		:param pointToPassTo: the tile that the agent is passing to. It is an XY coordinate defined to be the top left 
			corner of the tile you're trying to pass to

		:type pointToPassTo: typle of int

		:returns: no return 
		'''
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

	def getNNoutput(self):
		if (self.NN != None):
			self.NN.Flush()
			self.NN.Input(self.bevList) 
			self.NN.Activate()
			return self.NN.Output()
		else:
			return None;
	
	def _decisionFunction(self):
		"""
		This is where Magic Happens
		"""
		#print("Entering decision function")
		self.NN.Flush()
		self.NN.Input(self.bevList) # can input numpy arrays, too
			                          # for some reason only np.float64 is supported
		#print("Printing input of NN")		
		#print(self.bevList)
		#for _ in range(10000):
		self.NN.Activate()
		o = self.NN.Output()
		
		'''
		print("Printing output of NN")
		for i in range(len(o)):
			print o[i],' ',
		print()
		'''
		#print("Printing Connections")
		#print(len(self.NN.m_connections))
		#print(len(o))
		holdDecision = self.ballHolderSubIndex
		passList = [0,0]
		for j in range(len(self.bevList)):
			if self.bevList[j] == 1 and j!=holdDecision:
				passList.append(j)
				

		keeperIndex = [0,0]
		try:
			if self.bevSubstrate[holdDecision]:
				#print("Value for holding is:   ",o[holdDecision])
				a=0
		except Exception as ex:
			print("Exception with hold ball. Value: ",holdDecision)
		try:
			if self.bevSubstrate[passList[0]]:
				#print("Value for passing 0 is: ",o[passList[0]])
				a=0
		except Exception as ex:
			print("Exception with pass 0. Value: ",passList[0])
		try:
			if self.bevSubstrate[passList[1]]:
				#print("Value for passing 1 is: ",o[passList[1]])
				a=0
		except Exception as ex:
			print("Exception with pass 1. Value: ",passList[1])

		if (kUtil.getSqrDist(self.bevSubstrate[holdDecision],self.bevSubstrate[passList[0]])) <= (kUtil.getSqrDist(self.bevSubstrate[holdDecision],self.bevSubstrate[passList[1]])):
			keeperIndex[0] = 1
			keeperIndex[1] = 2
		else:
			keeperIndex[0] = 2
			keeperIndex[1] = 1
			
		out,i = max([(x,y) for y,x in enumerate(o)])
		'''
		if (o[holdDecision] >= o[passList[0]]) and (o[holdDecision] >= o[passList[1]]):
			#print("Holding ball")
			self._holdBall()
		else:
			if o[passList[0]] >= o[passList[1]]:
				#print("Pass 0")
				self._passBall(keeperIndex[0])
			else:
				#print("Pass 1")
				self._passBall(keeperIndex[1])

		#print("The decision is: ",i)
		'''
		if i==holdDecision:
			self._holdBall()
		else:
			self._passBall(self.bevSubstrate[i])
		
		return


	def receiveBest(self, NN):
		self.NN = NN


