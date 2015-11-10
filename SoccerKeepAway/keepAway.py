"""
This module contains keepAway, which is the simulator class. 
"""
import kUtil, agent, ball, getSimpleStateVars, handCoded, calcReceive, birdsEyeView, NEAT, hyperNEAT, NEATTraining, HyperNEATTraining
import pygame, sys, math
from statistics import mode



class keepAway():
	"""
	This is the simulator class. It is triggered by the runme module, and will 
	control most of the execution of the simulation. It is responsible for holding
	all of the true values of positions. It sends noisy information to all the 
	agents, and also allows agents to interact with it. Agents have no control
	whatsoever of variables and functions within keepAway. 
	"""

	def __init__(self, inputAgentSigmaNoise = .1, alreadyTrained = True, bevCustomTileSize = None):
		pygame.init()
		#RGB color
		self.__white = (255,255,255) 
		self.__black = (0,0,0)
		self.__red = (255,0,0)
		self.__green = (0,155,0)
		self.__blue = (0,0,255)
		
		#give the game a title
		pygame.display.set_caption('Keepaway')
		self.keeperScore = 0
		
		#these are more or less global variables..
		#I'm not sure if this is bad or not. 
		self.__worldImage = pygame.image.load('images/soccer_field.png')
		self.__ballImage = pygame.image.load('images/ball.png')
		self.__keeperImage = pygame.image.load('images/keeper.png')
		self.__keeperGoldImage = pygame.image.load('images/keeperGold.png')
		self.__takerImage = pygame.image.load('images/taker.png')
		self.__predictedImage = pygame.image.load('images/x.png')
		self.__debugYellowDotImage = pygame.image.load('images/yellow_dot.png')
		self.__debugRedDotImage = pygame.image.load('images/red_dot.png')
		self.__debugBlackDotImage = pygame.image.load('images/black_dot.png')
		self.__debugWhiteDotImage = pygame.image.load('images/white_dot.png')
		self.__debugBlueDotImage = pygame.image.load('images/blue_dot.png')
		self.__debugTakerPathTile = pygame.image.load('images/takerPathSquare.png')
		self.__debugKeeperPathTile = pygame.image.load('images/keeperPathSquare.png')
		self.__debugKeeperTile = pygame.image.load('images/keeperSquare.png')
		self.__debugTakerTile = pygame.image.load('images/takerSquare.png')
		self.__debugEmptyTile = pygame.image.load('images/emptySquare.png')
		self.__debugTakerPathTileTwo = pygame.image.load('images/takerPathSquare2.png')
		self.__debugKeeperPathTileTwo = pygame.image.load('images/keeperPathSquare2.png')
		#block sizes are used for collision detection
		#only 1 size per element because all blocks are squares. block size = side length
		self.__agent_block_size = 23
		self.__ball_block_size = 12

		self.maxBallSpeed= 4
		self.maxPlayerSpeed = 2
		#self.rDecision = None

		
		#dimensions of the game are the same as the soccer field image
		self.__display_width = 550
		self.__display_height = 357
		self.displayGraphics = True
		self.__field_center = (self.__display_width / 2 , self.__display_height / 2)
		#gameDisplay is a pygame.surface object. it's your screen
		self.gameDisplay = pygame.display.set_mode((self.__display_width,self.__display_height))
		self.test_fps = 60
		self.train_fps = 10000
		self.clock = pygame.time.Clock()
		
		
		#start the ball kinda close to the keeper in the upper left corner
		self.fieldBall = ball.ball( (self.__field_center[0]/4, self.__field_center[1]/4), self.maxBallSpeed)
		
		#the simple state variables for agents like NEAT, novelty search, and maybe sarsa
		self.simpleStateVars = None
		
		self.alreadyTrained = alreadyTrained  #False if you want agent to learn and True if you want to demo
		
		#setup all the initial keepers and takers. They are all starting at different field positions, which is why
		#you can't have a for loop just iterate and declare all of them
		types = ["keeper", "taker"]
		self.agentSigmaError = inputAgentSigmaNoise
		self.keeperArray = []
		self.keeperTruePosArray = []
		self.keeperTruePosArray.append((12.5, 12.5))
		self.keeperTruePosArray.append((25,  self.__display_width - 37.5))
		self.keeperTruePosArray.append((self.__display_height - 37.5,  self.__display_width - 37.5))
		self.keeperArray.append(agent.agent(self, 0, kUtil.getNoisyVals( self.keeperTruePosArray[0], self.agentSigmaError), self.agentSigmaError, types[0], kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.agentSigmaError), self.maxPlayerSpeed, self.maxBallSpeed))
		self.keeperArray.append(agent.agent(self, 1, kUtil.getNoisyVals( self.keeperTruePosArray[1], self.agentSigmaError), self.agentSigmaError, types[0], kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.agentSigmaError), self.maxPlayerSpeed, self.maxBallSpeed))
		self.keeperArray.append(agent.agent(self, 2, kUtil.getNoisyVals( self.keeperTruePosArray[2], self.agentSigmaError), self.agentSigmaError, types[0], kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.agentSigmaError), self.maxPlayerSpeed, self.maxBallSpeed))
		
		self.takerArray = []
		self.takerTruePosArray = []
		self.takerTruePosArray.append((self.__display_height - 25,  25))
		self.takerTruePosArray.append((self.__display_height - 37.5,  50))
		self.takerArray.append(agent.agent(self, 0, self.takerTruePosArray[0], self.agentSigmaError, types[1], kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.agentSigmaError), self.maxPlayerSpeed, self.maxBallSpeed))
		self.takerArray.append(agent.agent(self, 1, self.takerTruePosArray[1], self.agentSigmaError, types[1], kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.agentSigmaError), self.maxPlayerSpeed, self.maxBallSpeed))
		
		#3 different font sizes 
		self.smallfont = pygame.font.SysFont("comicsansms",25) #25 is font sizes
		self.medfont = pygame.font.SysFont("comicsansms",50) 
		self.largefont = pygame.font.SysFont("comicsansms",80) 
		self.verysmallfont = pygame.font.SysFont("comicsansms", 12)
		
		#birdsEyeView generator for agents like hyperNEAT:
		if bevCustomTileSize == None:
			bevCustomTileSize = self.__agent_block_size
		self.bev = birdsEyeView.birdsEyeView(self.__display_width, self.__display_height, bevCustomTileSize, self.__ball_block_size )
		self.bev_grid_as_grid = self.bev.getBirdsEyeView(self.keeperArray, self.takerArray);
		self.bev_grid_as_list = self.bev.getBirdsEyeViewAsList(self.keeperArray, self.takerArray);
		self.bev_substrate = self.bev.getSubstrate(self.keeperArray, self.takerArray);
		self.bev_keeper_sub_index = self.bev.getBallHolderTile(self.keeperArray)
	"""
	BASIC REQUIRED FUNCTIONS 
	functions: exit, message to screen, pause, finish execution, draw world, and update score
	"""
		
	def __exitSim(self):
		"""
		This function will quit the simulation
		
		:returns: no return
		"""
		pygame.quit()
		sys.exit(0)
		
		#important function: print message to user
	def __message_to_screen(self, msg, color, y_displace = 0, size = "small"):
		"""
		This function will print a message to the screen
		
		:param msg: the message that you want to print to screen
		:param color: the color you want the message to be
		:param y_displae: the higher this value, the lower the text will be displayed. A
		    value of 0 indicates that this message should be at the very top
		:param size: the size you want the text to be. default value is "small"
		
		:type msg: string
		:type color: tuple of 3 integers. This is RGB, where each dimension 
		    ranges from 0 to 255
		:type y_displae: integer
		:type size: string
		
		:returns: no return
		"""
		textSurface,textRect = self.__text_objects(msg,color, size)
		textRect.center = (self.__display_width/2), (self.__display_height/2) + y_displace
		self.gameDisplay.blit(textSurface, textRect)
		
	def __text_objects(self, text,color, size):
		"""
		This function will generate a text object to be printed 
		to the screen
		
		:param text: the message that you're generating a text object for
		:param color: the color you want the message to be
		:param size: the size you want the text to be.
		
		:type text: string
		:type color: tuple of 3 integers. This is RGB, where each dimension 
		    ranges from 0 to 255
		:type size: string
		
		:returns: no return
		"""
		if size == "small":
			textSurface = self.smallfont.render(text, True, color)
		elif size == "medium":
			textSurface = self.medfont.render(text, True, color)
		elif size == "large":
			textSurface = self.largefont.render(text, True, color)
		elif size == "verysmall":
			textSurface = self.verysmallfont.render(text,True,color)
		return textSurface, textSurface.get_rect()
		
	def __displayScore(self):
		"""
		This function will display the keeper score on the top left corner of 
		the screen
		
		:returns: no return
		"""
		text= self.verysmallfont.render("Keeper Reward: "+ str(self.keeperScore), True, self.__black)
		
		self.gameDisplay.blit(text, [0,0]) 

	def pause(self, message):
		"""
		This function will pause the simulation and display a message to the
		screen
		
		:param message: the message that you want to display to the screen
		
		:type message: String
		
		:returns: no return
		"""
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
		
	def __finish(self):
		"""
		This function will notify the user that the simulation has ended, display 
		the final score, and prompt the user to press Q to quit. 
		
		:returns: no return
		"""
		
		paused = True
		self.__message_to_screen("Game Over, Final Score %d" %self.keeperScore, self.__red, 0, "small")
		self.__message_to_screen("Press Q to quit.",
		                  self.__red,
		                  50)
		pygame.display.update()
		while paused:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.__exitSim()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						self.__exitSim()
			#gameDisplay.fill(white)
			self.clock.tick(10)


	def __drawWorld (self, mode, gridList = None, substrate = None):
		"""
		This function will go and update the screen to display the next frame of 
		animation. This function should be called only after all the movement
		of agents and the ball has been calculated. If the self.displayGraphics
		flag is set to false, no graphics will be displayed. This is so that training
		potentially thousands of games will be quick.
		
		:returns: no return
		"""   
		if (self.displayGraphics == False):
			return                 
		#note: for blit function, give it column, row instead of row, column
		self.gameDisplay.blit(self.__worldImage, (0,0))
		
		for i in range(len(self.keeperArray)):
			self.gameDisplay.blit(self.__keeperImage, (self.keeperTruePosArray[i][1], self.keeperTruePosArray[i][0]))
			"""
			#this is for debugging. comment this out later
			if (self.rDecision != None):
			    if (i == self.rDecision[0]):
			        self.gameDisplay.blit(self.__keeperGoldImage, (self.keeperTruePosArray[i][1], self.keeperTruePosArray[i][0]))
			"""
		for i in range(len(self.takerArray)):
			self.gameDisplay.blit(self.__takerImage, (self.takerTruePosArray[i][1], self.takerTruePosArray[i][0]))
		self.gameDisplay.blit(self.__ballImage, (self.fieldBall.trueBallPos[1], self.fieldBall.trueBallPos[0]))
		#this is to display the predicted intersection point of a ball
		#you may want to comment this code out after debugging is done
		if (self.keeperArray[0].onReceiveDecision != None):
			self.gameDisplay.blit(self.__predictedImage, (self.keeperArray[0].onReceiveDecision[1][1] , self.keeperArray[0].onReceiveDecision[1][0]) )  
				
		if (gridList != None and substrate != None):
			self.__drawBirdsEyeView(mode, gridList, substrate)

	def __drawBirdsEyeView(self, mode, gridList, substrate):
		for z in range(len(gridList)):
			i = substrate[z][0]
			j = substrate[z][1]
			if gridList[z] == 0.0:
				self.gameDisplay.blit(self.__debugWhiteDotImage, (j,i))
			if gridList[z] == -1.0:
				self.gameDisplay.blit(self.__debugRedDotImage, (j,i))
			if gridList[z] == 1.0:
				self.gameDisplay.blit(self.__debugBlueDotImage, (j,i))
			if gridList[z] == 0.3:
				self.gameDisplay.blit(self.__debugBlueDotImage, (j,i)) 
			if gridList[z] == -0.3:
				self.gameDisplay.blit(self.__debugRedDotImage, (j,i)) 
			if gridList[z] == -0.6:
				self.gameDisplay.blit(self.__debugRedDotImage, (j,i)) 
			if gridList[z] == 0.6:
				self.gameDisplay.blit(self.__debugBlueDotImage, (j,i)) 
		kZeroIndex = self.bev.getBallHolderTile(self.keeperArray)
		self.gameDisplay.blit(self.__debugBlackDotImage, (substrate[kZeroIndex][1], substrate[kZeroIndex][0]))
		if(mode == "hyperNEAT"):
			o = self.keeperArray[0].getNNoutput();
			if(o != None):
				self.__DrawHyperNEATOut(o, self.bev.getBlockSize(), substrate)
					
	def __DrawHyperNEATOut(self, output, blockSize, substrate):
		diff = blockSize / 2
		for i in range(len(substrate)):
			text= self.verysmallfont.render(str(round(output[i], 2)), True, (0, 0, int(255*output[i])) )
			self.gameDisplay.blit(text, [substrate[i][1] - diff,substrate[i][0] - diff]) 
					
			
							
	def __updateScore(self):
		"""
		This function simply increments the keeper's score for each tick that the
		keepers manage to hold the ball without a taker taking it.
		
		:returns: no return
		"""
		if self.fieldBall.inPosession:
			self.keeperScore += 1
		
	def debugPassVectors(self, startPoint, vectors):
		"""
		This function is meant to display yellow dots to help the programmer figure
		out if the getRotatedVectors function works correctly. The getRotatedVectors
		function ended up being discarded, but code for it is still kept incase
		the developers decide they want to use it later on
		
		:param vectors: 2 vectors that were calculated by getRotatedVectors
		:param startPoint: the vertex/starting point of the vector that you're trying
		    to rotate. You rotate about the vertex. 
		    
		:type vectors: a list of 2 vectors, each vector being a tuple of floats
		:type startPoint: a tuple or list of floats
		
		:returns: no return
		"""
		self.worldRef.__drawWorld ()
		self.worldRef.__displayScore()
		print("Starting point: ", startPoint) 
		for vector in vectors:
			newVector = kUtil.addVectorToPoint(startPoint, kUtil.scalarMultiply(5, vector))
			print("printing vector: ", newVector)
			self.worldRef.gameDisplay.blit(self.worldRef.__debugYellowDotImage, (newVector[1], newVector[0]))
		self.worldRef.gameDisplay.blit(self.worldRef.__debugRedDotImage, (startPoint[1], startPoint[0]))
		pygame.display.update()
		print("debugging")
	"""
	END OF BASIC REQUIRED FUNCTIONS
	"""  



	"""
	CODE FOR MOVEMENT OF AGENTS
	When it comes to movement, there are 4 different quadrants defined:
	2 3
	1 0
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
	#this is the function the agent will call to try and move somewhere
	def moveAttempt(self, inputAgent, reversedPolarCoord ):
		"""
		This function is used by the agent in order to attempt movement on the 
		field. If the move is legal, the agent's position is updated. If the 
		move is illegal, then nothing happens. A move is illegal if the agent 
		tries to go outside the boundaries of the field. 
		
		:param inputAgent: a reference to the agent that is attempting to move
		:param reversedPolarCoord: the movement that the agent is trying to do. 
		    the movement is represented as a tuple where the first element is a
		    unit vector representing the direction the agent is trying to move, 
		    and the 2nd element is the distance the agent is trying to move.
		    
		:type inputAgent: agent
		:type reversedPolarCoord: tuple where first element is a tuple of floats, 
		    and the 2nd element is a float or integer
		
		:returns: true if move was successful, false if not
		:rtype: boolean
		"""
		noiseFreeDirectionVector = reversedPolarCoord[0]
		distance = reversedPolarCoord[1]
		
		#for the purposes of finding legal moves, just assume that they player is trying
		#to cover the most amount of distance. Also, right now, it's not important if
		#noiseFreeDirectionVector is a unit vector or not
		quad = self.__getQuadAttemptingToMoveTo(inputAgent, noiseFreeDirectionVector)
		setOfLegalQuads = self.__getLegalQuadrants(inputAgent)
		#print setOfLegalQuads 
		#print "quad:", quad
		if quad in setOfLegalQuads:
			#move is legal, do it
			self.__moveAgent(inputAgent, kUtil.scalarMultiply ( distance, kUtil.unitVector(noiseFreeDirectionVector)))
		else:
			#move is illegal. Simply return without calling or updating anything
			#print "Illegal move: ", reversedPolarCoord 
			return False
		if kUtil.magnitude(noiseFreeDirectionVector) == 0.0:
			return False
		else:
			return True
	#if a move is determined to be legal, this function will move the agnet
	def __moveAgent(self, inputAgent, movementVector):
		"""
		This is a private function that is called by the moveAttempt function.
		this function is only called if a move is determined to be legal. Once
		the move is determined to be legal, this function will go and update the
		position of the agent on the field.
		
		:param inputAgent: a reference to the agent that is is being moved.
		:param movementVector: the vector that will be added to the inputAgent's
		    current position. The sum of the current position and the movementVector
		    will be the new position of the inputAgent.
		    
		:type inputAgent: agent
		:type movementVector: a tuple of floats
		
		:returns: no return
		
		.. note::
		    This is a private function that the user shouldn't worry about calling.
		    Only the move_attempt() function should be called.  
		"""
		if inputAgent.getAgentType() == "keeper":
			newNoiseFreePos = kUtil.addVectorToPoint(self.keeperTruePosArray[inputAgent.getSimIndex()], movementVector)
			self.keeperTruePosArray[inputAgent.getSimIndex()] = newNoiseFreePos
		elif inputAgent.getAgentType() == "taker":
			newNoiseFreePos = kUtil.addVectorToPoint(self.takerTruePosArray[inputAgent.getSimIndex()], movementVector)
			self.takerTruePosArray[inputAgent.getSimIndex()] = newNoiseFreePos

		inputAgent.updateAgentPosition(kUtil.getNoisyVals(newNoiseFreePos, self.agentSigmaError))    
	#internal function. determine which quadrant the agent is trying to move to
	def __getQuadAttemptingToMoveTo(self, agent, noiseFreeDirectionVector):
		"""
		This is a private function that is called by the moveAttempt function.
		this function is used to determine which quadrant the agent is attempting
		to move to. 
		
		:param agent: a reference to the agent that is is being moved.
		:param noiseFreeDirectionVector: a vector that represented the displacement
		    that the agent is trying to achieve. 
		    
		:type agent: agent
		:type noiseFreeDirectionVector: a tuple of floats
		
		:returns: the quadrant the agent is trying to move to, indexed 0 - 3
		
		.. note::
		    This is a private function that the user shouldn't worry about calling.
		    Only the move_attempt() function should be called.  
		"""
		#noise free direction vector of the form (row, col), and row's graph axis is reversed in pygame. so multiply 
		#the row direction vector by -1.0
		y = noiseFreeDirectionVector[0]
		x = noiseFreeDirectionVector[1] 
		angleInRadians = math.atan2(y,x)
		#print "angleInRadians:", angleInRadians, " for y = ", y, "and x = ", x 
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
	def __getLegalQuadrants(self, inputAgent):
		"""
		When it comes to movement, there are 4 different quadrants defined:
		2 3
		1 0
		quadrant 0 is from directions 0 degrees to 90 degrees
		quadrant 1 is from directions 90 degrees to 180 degrees
		quadrant 2 is from directions 180 degrees to 270 degrees
		quadrant 3 is from directions 270 degrees to 360 degrees
		
		This function returns the set of quadrants that an agent is allowed 
		to move to
		
		:param inputAgent: a reference to the agent whose set of legal quadrants 
		    is being calculated for
		    
		:type inputAgent: agent
		
		:returns: set of quadrants the agent can move to
		:rtype: set of integers
		
		.. note::
		    This is a private function that the user shouldn't worry about calling.
		    Only the move_attempt() function should be called. 
		"""
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
			if not self.__isDirectionLegal(inputAgent, directions[i]):
				# this will execute if a move is ILLEGAL
				returnSet.difference_update(bannedQuadrants[i])
		return returnSet

	#a function that is internal to __getLegalQuadrants
	def __isDirectionLegal(self, inputAgent, direction):
		"""
		This is a private function used exclusively by __getLegalQuadrants in
		order to determine if an agent is legally allowed to move in a given
		direction
		
		:param inputAgent: a reference to the agent, which is being checked to 
		    see if it can move in a given direction
		:param direction: the direction the agent is trying to go. It's going
		    to be either up,down,left, or right
		    
		:type inputAgent: agent
		:type direction: string
		
		:returns: true if the agent is allowed to move in that direction, otherwise false
		:rtype: boolean
		"""
		rowPixel1 = self.keeperTruePosArray[inputAgent.getSimIndex()][0]
		colPixel1 = self.keeperTruePosArray[inputAgent.getSimIndex()][1]
		
		
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
		rowPixel2 = rowPixel1 + self.__agent_block_size
		colPixel2 = colPixel1 + self.__agent_block_size 
		
		#check to see if you go outside the boundaries of the game    
		if rowPixel1 < 0 or colPixel1 < 0 or rowPixel2 > self.__display_height or colPixel2 > self.__display_width :
			#print "upper left coordinates: ", (rowPixel1, colPixel1) 
			return False
		#if you're not outside boundaries, then it's a totally legal direction. It just might not be optimal
		else:
			return True
		
		
	"""
	End the code that defines movement for agents
	""" 

	"""THIS CODE IS FOR GAMEOVER, GAME RESET FOR TRAINING, AND AGENT REPLACEMENT"""
	#reset the game for another training episode
	def resetGameForTraining(self):
		"""
		This is a public function that is meant for resetting the simulator when in 
		training mode. Training mode will be used by the intelligent agents such as
		SARSA, NEAT, hyperNEAT, etc.
		
		All it does is reset the ball position, the agent positions, and also sets the
		individual agents "inPosession", and "isKicking" flags to false, to indicate 
		that there are no agents that have posession of the ball, nor are there
		any agents kicking the ball. 
		
		:returns: no return 
		"""
		#reset the ball variables
		#row = random.randint(0, int(self.__display_height/2))
		#col = random.randint(int(self.__display_width/4), int (self.__display_width/4 * 3))
		self.fieldBall.updateCoordinate((self.__field_center[0]/4, self.__field_center[1]/4))
		self.fieldBall.updateDirection((0.0,0.0))
		
		#reset the score
		self.keeperScore = 0
		
		#now reset the agent positions:
		self.keeperTruePosArray[0] = (12.5, 12.5)
		self.keeperTruePosArray[1] = (25,  self.__display_width - 37.5)
		self.keeperTruePosArray[2] = (self.__display_height - 37.5,  self.__display_width - 37.5)
		self.takerTruePosArray[0] = (self.__display_height - 25,  25)
		self.takerTruePosArray[1] = (self.__display_height - 37.5,  50)
		
		for i in range(len(self.keeperArray)):
			self.keeperArray[i].updateAgentPosition(kUtil.getNoisyVals(self.keeperTruePosArray[i], self.agentSigmaError)) 
			self.keeperArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos,self.keeperArray[i].getSigma())
			self.keeperArray[i].inPosession = False
			self.keeperArray[i].isKicking = False

		for i in range(len(self.takerArray)):
			self.takerArray[i].updateAgentPosition(kUtil.getNoisyVals(self.takerTruePosArray[i], self.agentSigmaError)) 
			self.takerArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.takerArray[i].getSigma())
			self.takerArray[i].inPosession = False
			self.takerArray[i].isKicking = False
	#detect if game is over by checking if ball is out of bounds, or 
	#if a taker has gained posession of the ball
	def isGameOver(self):
		"""
		This function simply checks whether or not the ball is out of bounds, or 
		intercepted by a taker. if so, then the game is over.
		
		:returns: true if ball out of bounds or intercepted by taker. otherwise false
		:rtype: boolean
		"""
		#game is over when a taker obtains the ball
		#game is also over when the ball is kicked out of bounds
		for i in range(len(self.takerArray)):
			if self.takerArray[i].inPosession == True:
				return True
		#now check if ball is out of bounds:
		rowPixel1 = self.fieldBall.trueBallPos[0]
		colPixel1 = self.fieldBall.trueBallPos[1]
		
		#lower right coordinate of ball boundary
		rowPixel2 = rowPixel1 + self.__ball_block_size
		colPixel2 = colPixel1 + self.__ball_block_size    
		
		#check to see if you go outside the boundaries of the game    
		if rowPixel1 < 0 or colPixel1 < 0 or rowPixel2 > self.__display_height - 1 or colPixel2 > self.__display_width - 1:  
			return True
		#If you made it here, then that means the game is still going
		return False

	#At the title, the user will decide which agent should take control
	#This function will replace the default agent.py class with whatever
	#the user decides to pick
	def __replaceAgents(self, inputClass):
		"""
		During the game introduction, the user can select which agent should be run.
		After the user selects the agent, this function will go and 
		override the default agents with the agents the user has selected
		
		:param inputClass: this is the class that the user has selected to 
		    go and replace the default agents.
		
		:type inputClass: agent.class
		
		:returns: no return 
		"""
		#replace the standard agents with the intelligent or hand coded agents
		for i in range(len(self.keeperArray)):
			tempKeeper = self.keeperArray[i]
			self.keeperArray[i] = inputClass(tempKeeper.worldRef, tempKeeper.getSimIndex(), tempKeeper.get_noisy_pos(), tempKeeper.getSigma(), tempKeeper.getAgentType(), self.fieldBall.trueBallPos, self.maxPlayerSpeed, self.maxBallSpeed) 
		for i in range(len(self.takerArray)):
			tempTaker = self.takerArray[i]
			self.takerArray[i] = inputClass(tempTaker.worldRef, tempTaker.getSimIndex(), tempTaker.get_noisy_pos(), tempTaker.getSigma(), tempTaker.getAgentType(), self.fieldBall.trueBallPos, self.maxPlayerSpeed, self.maxBallSpeed)    
		
		#once the other arrays are initialized, send references to all keepers and takers
		#you don't need to worry about other references. This function will only be called during initialization
		#also go and send over references to the ball                 
		for i in range(len(self.keeperArray)):
			self.keeperArray[i].receiveListOfOtherPlayers(self.keeperArray, self.takerArray, i)
			self.keeperArray[i].receiveBallReference(self.fieldBall)
		for i in range(len(self.takerArray)):
			self.takerArray[i].receiveListOfOtherPlayers(self.keeperArray, self.takerArray, i)
			self.takerArray[i].receiveBallReference(self.fieldBall)

	"""END OF GAME OVER, RESET, AND AGENT REPLACEMENT CODE"""

	"""THIS CODE DEALS WITH UPDATING POSESSION VARIABLES AND BALL/AGENT COLLISION DETECTION"""
	#This function checks for ball intersections, and then updates posession variables for agents and bal
	def __updateBallPosession(self): 
		"""
		This private function checks to see if a keeper or taker has intercepted the ball. If so,
		Then update the ball's possession variable to indicate that the ball is currently in 
		possession, and also set the ball's velocity/direction to 0. 
		
		
		:returns: no return 
		"""     
		#check takers first. If they get the ball, GG, so return
		for i in range(len(self.takerArray)):
			if self.__agentBallIntersection(self.takerArray[i], "taker"):
				self.takerArray[i].inPosession = True
				self.fieldBall.updatePosession(True)
				#print "taker ", i, "has ball at taker true coordinate:", self.takerArray[i].true_pos
				#print "ball true corner coord range: ", self.fieldBall.trueBallPos, "to", (self.fieldBall.trueBallPos[0]+ self.ball_block_size, self.fieldBall.trueBallPos[1]+ self.ball_block_size)
				return
			else:
				self.takerArray[i].inPosession = False

		
		for i in range(len(self.keeperArray)):
		#for i in range(1):
			if self.keeperArray[i].isKicking == False:
				if self.__agentBallIntersection(self.keeperArray[i], "keeper"):
					#case where keeper is NOT kicking, and ball and agent intersect
					self.keeperArray[i].inPosession = True
					self.fieldBall.updatePosession(True)
					return
				#print "keeper ", i, "has ball at keeper true coordinate:", self.keeperArray[i].true_pos, " to ", (self.keeperArray[i].true_pos[0] + self.agent_block_size, self.keeperArray[i].true_pos[1] + self.agent_block_size)
				#print "ball true corner coord range: ", self.fieldBall.trueBallPos, "to", (self.fieldBall.trueBallPos[0]+ self.ball_block_size, self.fieldBall.trueBallPos[1]+ self.ball_block_size)
			else:
				#this is the case where the agent IS kicking
				#check to see if the agent is intersecting the ball
				#if they are, leave keeper.isKicking = true
				#otherwise, you can now update it to False
				if self.__agentBallIntersection(self.keeperArray[i], "keeper") == False:
					self.keeperArray[i].isKicking = False
				self.keeperArray[i].inPosession = False

		#if you reached here, then it means that no one has the ball, so update accordingly
		#self.fieldBall.updatePosession(False, self.fieldBall.trueBallPos)
		self.fieldBall.updatePosession(False)


	#this is more or less a private function of self.__updateBallPosession()
	#check for the intersection of an agent and a ball
	def __agentBallIntersection(self, inputAgent, agentType):
		"""
		This private function will take an input agent, and 
		check to see if that agent intersects with the ball or not.
		If so, return true. otherwise return false.
		
		:param inputAgent: the agent that you're checking to see
		    if it intersects with the ball or not. 
		:param agentType: "keeper" or "taker"
		
		:type inputAgent: agent
		:type agentType: string
		
		:returns: true if the agent intersects with the ball, false otherwise
		:rtype: boolean 
		"""  
		#print
		if agentType == "keeper":
			agentTruePosition = self.keeperTruePosArray[inputAgent.getSimIndex()]
		else:
			#agent must be a taker
			agentTruePosition = self.takerTruePosArray[inputAgent.getSimIndex()]

		agentRadius = self.__agent_block_size / 2
		ballRadius = self.__ball_block_size / 2
		cutoff = agentRadius+ ballRadius
		agentMidPoint = kUtil.addVectorToPoint(agentTruePosition, (self.__agent_block_size/2, self.__agent_block_size/2))
		ballMidPoint = kUtil.addVectorToPoint(self.fieldBall.trueBallPos, (self.__ball_block_size/2, self.__ball_block_size/2))
		#print "agent actual:", inputAgent.true_pos, "agentMid:", agentMidPoint
		#print "agentMid:", agentMidPoint, " ballMid:", ballMidPoint
		distBetweenMidPoints = kUtil.getDist(agentMidPoint, ballMidPoint)
		#print "Cutoff: ", cutoff, " actual Distance: ", distBetweenMidPoints
		if (distBetweenMidPoints <= cutoff):
			return True
		else:
			return False
	"""END OF AGENT POSSESSION UPDATE AND BALL/AGENT COLLISION DETECTION"""


	"""THIS CODE IS FOR PRE-CALCULATING RECEIVE(), STATE VARIABLES, AND SENDING THEM"""

	#send all the state variables to the keepers and takers
	def _sendSimpleStateVars(self):
		"""
		This public function will send all keepers the simple state variables.
		This function should be called for intelligent agents such as NEAT, 
		or Sarsa. This function will NOT be called for hyperNEAT, which 
		will instead, get a birds eye view of the entire field

		:returns: no return
		"""  
		#get the state variables
		self.simpleStateVars = getSimpleStateVars.getStateVarsKeepers(self.keeperArray, self.takerArray, self.__field_center)
		#send the state variables to each keeper and taker
		for i in range(len(self.keeperArray)):
			noisyCurrVars = kUtil.getNoisyVals(self.simpleStateVars, self.agentSigmaError)
			noisyCurrVars = self.__boundSimpleVars(noisyCurrVars)
			self.keeperArray[i].receiveSimpleStateVariables(noisyCurrVars)
		for i in range(len(self.takerArray)):
			noisyCurrVars = kUtil.getNoisyVals(self.simpleStateVars, self.agentSigmaError)
			noisyCurrVars = self.__boundSimpleVars(noisyCurrVars)
			self.takerArray[i].receiveSimpleStateVariables(noisyCurrVars)

	def __boundSimpleVars(self, noisySimpleStateVars):
		"""
		For the sake of simulating sensor error, some noise is added to the state variables
		that are calculated. However, the last 2 state variables are cosine values. Cosine values
		are bounded [-1.0, 1.0], so this function was made to ensure that the last 2 state variables are 
		bounded by [-1.0, 1.0] after noise is added to it. This is important because the arccos
		of these 2 state variables is calculated sometimes, and if the value input into arccos
		just so happens to be out of this range,the program will crash. 
		
		:param noisySimpleStateVars: The noisy version of the simple state variables. This should
		    be calculated in the sendSimpleStateVars function of keepaway.py. 
		
		:type noisySimpleStateVars: tuple or list of floats
		
		:returns: the noisySimpleStateVars, but with the last 2 parameters bounded by [-1.0, 1.0]
		
		:rtype: tuple or list of floats
		"""
		varIndex11 = noisySimpleStateVars[11]
		varIndex12 = noisySimpleStateVars[12]
		while (varIndex11 > 1.0 or varIndex11 <  -1.0):
			varIndex11 = kUtil.getNoisyVals(noisySimpleStateVars[11], self.agentSigmaError)
		while (varIndex12 > 1.0 or varIndex12 <  -1.0):
			varIndex12 = kUtil.getNoisyVals(noisySimpleStateVars[12], self.agentSigmaError)
		if varIndex11 > 1.0 or varIndex11 < -1.0 or varIndex12 > 1.0 or varIndex12 < -1.0:
			print("Values still out of range: varIndex11 = ", varIndex11, ", varIndex12 = ", varIndex12)
		return noisySimpleStateVars[:11] + (varIndex11, varIndex12)

	def _sendBirdsEyeView(self):
		#get the state variables
		self.bev_grid_as_grid = self.bev.getBirdsEyeView(self.keeperArray, self.takerArray);
		self.bev_grid_as_list = self.bev.getBirdsEyeViewAsList(self.keeperArray, self.takerArray);
		self.bev_substrate = self.bev.getSubstrate(self.keeperArray, self.takerArray);
		self.bev_keeper_sub_index = self.bev.getBallHolderTile(self.keeperArray)
		#send the state variables to each keeper
		for i in range(len(self.keeperArray)):
			self.keeperArray[i].receiveBirdsEyeView(self.bev_grid_as_grid, self.bev_grid_as_list, self.bev_substrate, self.bev_keeper_sub_index)

	def _sendNEATTraining(self):
		NEATTraining.train(self)
		return True

	def _sendHyperNEATTraining(self):
		HyperNEATTraining.train(self)
		return True


	def _sendCalcReceiveDecision(self):
		"""
		This public function will send all keepers the receive decision. For more information
		on what the receive decision is, refer to the documentation of the module "calcReceive"

		:returns: no return
		"""  
		#note: rDecision is only global so that it can be debugged. Once debugging is done, make it local again
		rDecision = calcReceive.calc_receive(self)
		#print("rDecision decided upon:")
		#print(rDecision)
		for i in range(len(self.keeperArray)):
			rNoisyDecision= (rDecision[0], kUtil.getNoisyVals(rDecision[1], self.agentSigmaError))
			self.keeperArray[i].receiveDecision(rNoisyDecision)
		for i in range(len(self.takerArray)):
			rNoisyDecision= (rDecision[0], kUtil.getNoisyVals(rDecision[1], self.agentSigmaError))
			self.takerArray[i].receiveDecision(rNoisyDecision)

	"""END OF CODE FOR CALCULATING RECEIVE() AND SENDING TO AGENTS"""


	"""THIS CODE IS THE INTRO AND GAME LOOPS"""
	def commonFunctionality(self, mode, showDisplay = True, turnOnGrid = False):
		#this is common code that will occur regardless of what agent you picked
		#if (self.fieldBall.inPosession == False):
		newBallPoint = kUtil.addVectorToPoint(self.fieldBall.trueBallPos, kUtil.scalarMultiply(self.maxBallSpeed, kUtil.unitVector(self.fieldBall.trueBallDirection)))
		self.fieldBall.updateCoordinate(newBallPoint)
		for i in range(len(self.takerArray)):
			self.takerArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.takerArray[i].getSigma())
		for i in range(len(self.keeperArray)):
			self.keeperArray[i].noisyBallPos = kUtil.getNoisyVals(self.fieldBall.trueBallPos, self.keeperArray[i].getSigma())                
		self.__updateBallPosession()
		self.__updateScore()
		#remove this line if you don't want the grid to be drawn
		if showDisplay:
			if (turnOnGrid):
				gridList = self.bev.getBirdsEyeViewAsList(self.keeperArray, self.takerArray)
				substrate = self.bev.getSubstrate(self.keeperArray, self.takerArray)
				self.__drawWorld (mode, gridList, substrate)
			else:
				self.__drawWorld(mode)
			self.__displayScore()
			pygame.display.update()

	def game_intro(self):
		"""
		This is the introduction screen. It will prompt the user to select the 
		agent that should play keepaway. After selection of the agent, this loop will
		terminate and begin the main game loop.
		
		:returns: no return
		"""  
		intro = True
		#display intro title to user
		if intro:
			self.gameDisplay.fill(self.__white)
			self.__message_to_screen("Welcome to Keep Away",
			                  self.__green,
			                  -100,
			                  "medium")      
			self.__message_to_screen("N for NEAT, ",
			                  self.__black,
			                  40)   
			self.__message_to_screen("S for HyperNEAT, ",
			                  self.__black,
			                  80)           
			self.__message_to_screen("H for hand coded agent, or E to exit.",
			                  self.__black,
			                  120) 
			pygame.display.update()
		#while in the intro, check for user input on what type of model they wanna use
		while intro:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.__exitSim()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_s:
						mode = "hyperNEAT"
						self.__replaceAgents(hyperNEAT.hyperNEAT)
						intro = False
						return mode
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_n:
						mode = "NEAT"
						self.__replaceAgents(NEAT.NEAT)
						intro = False
						return mode
					if event.key == pygame.K_h:
						mode = "hand_coded"
						self.__replaceAgents(handCoded.handCoded)
						intro = False
						return mode
					if event.key == pygame.K_m:
						mode = "manual"
						intro = False
						return mode
					if event.key == pygame.K_e:
						self.__exitSim()
			self.clock.tick(5)

	def gameLoop(self, mode, turnOnGrid = False):
		"""
		This is the main game loop. Each iteration of this counts as a tick. 
		With each tick, an agent can move keepAway.maxPlayerSpeed units, and the
		ball can move keepAway.maxBallSpeed units. At the end of each tick, the
		pygame screen is updated to the next frame. 

		:returns: no return
		"""  
		self.__drawWorld (mode)
		gameExit = False
		pygame.display.update()
		experimentAgent = self.keeperArray[0]
		#each occurance of this loop is treated as one simulation cycle
		while not gameExit:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					gameExit = True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						self.pause("PAUSED. Press Space to continue")
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
				self._sendCalcReceiveDecision()
				self._sendBirdsEyeView()
				self._sendSimpleStateVars()
				for keeper in self.keeperArray:
					keeper.decisionFlowChart()
				for taker in self.takerArray:
					taker.decisionFlowChart()
			elif(mode == "NEAT"):
				self._sendCalcReceiveDecision()
				self._sendSimpleStateVars()
				if (self.alreadyTrained == False):
					self.alreadyTrained = self._sendNEATTraining()
				for keeper in self.keeperArray:
					keeper.decisionFlowChart()
				for taker in self.takerArray:
					taker.decisionFlowChart()
			elif(mode == "hyperNEAT"):
				self._sendCalcReceiveDecision()
				self._sendBirdsEyeView()
				if (self.alreadyTrained == False):
					self.alreadyTrained = self._sendHyperNEATTraining()
				for keeper in self.keeperArray:
					keeper.decisionFlowChart()
				for taker in self.takerArray:
					taker.decisionFlowChart()
			self.commonFunctionality(mode, True,turnOnGrid)
	
			if self.isGameOver() == True:
				gameExit = True
				print("final score: ", self.keeperScore) 
			#this specifies frames per second
			self.clock.tick(self.test_fps)
		self.__finish()
		#self.pause("Game Over: Final Score %d" % self.keeperScore)
		self.__exitSim()

	"""END OF INTRO AND GAME LOOPS"""
		
	"""Getter functions"""
	def get_ball_block_size(self):
		"""
		this simply gets and returns the simulators agent_block_size, which 
		is the width and height of the agent in pixels. 
		
		:returns: agent block size
		:rtype: integer
		"""
		return self.__ball_block_size	
	
	def get_agent_block_size(self):
		"""
		this simply gets and returns the simulators agent_block_size, which 
		is the width and height of the agent in pixels. 
		
		:returns: agent block size
		:rtype: integer
		"""
		return self.__agent_block_size

	def get_display_width(self):
		"""
		this simply gets and returns the simulators display width. 
		
		:returns: simulator screen width
		:rtype: integer
		"""
		return self.__display_width

	def get_display_height(self):
		"""
		this simply gets and returns the simulators display height. 
		
		:returns: simulator screen height
		:rtype: integer
		"""
		return self.__display_height

	def get_field_center(self):
		"""
		this simply gets and returns center coordinate of the field 
		
		:returns: center of field coordinate
		:rtype: tuple of floats
		"""
		return self.__field_center

