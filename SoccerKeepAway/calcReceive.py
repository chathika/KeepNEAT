"""
This is a module of static functions whose sole purpose is simply 
to calculate and return
a tuple (Index_of_keeper_to_go_after_ball, intersection_coordinate).
Index_of_keeper_to_go_after_ball will allow the keepers to decide which keeper
is in the best position to intercept the ball. That keeper will run to the
projected intersection point, the intersection_coordinate. 

All other keepers will try to position themselves to be open to receive
a pass from the keeper going for the ball. 
 
"""
#note: the whole purpose of this class is to return the tuple called
#rDecision = (keeperIndex_to_go_after_ball, intersection_coordinate)

import kUtil
#calculate the receive() for if the ball is stationary
#or moving. calcuations for stationary are done in this 
#fucntion. the function for when the ball is moving
#is done in the other function
def calc_receive(worldRef, inputDirection = None):
    """
    This function is the only public function of this module. It will go and 
    calculate the receive decision, which is a tuple that simply contains the 
    index of the keeper that should run towards the ball, and the coordinate 
    that the keeper should run to. If the ball is stationary, the coordinate
    the selected keeper should run to is simply the coordinates of the ball. 
    If the ball is moving, then calc_receieve will find an intersection point
    along the balls projected path that the selected keeper can run to. 
    The intercept point is selected such that the 
    selected keeper will run a short distance, be far away from the takers, 
    and also be far away from out of bounds.  
    
    .. note::
        Only the simulator class should call the calc_receive method. This method
        will therefore return the noise-free interception point. The simulator
        must then add random noise to the noise-free interception point before
        passing the receive decision to a keeper. A different amount of noise value
        be added for each keeper. 
    
    :param worldRef: a reference to the simulator class which is calling this function
    :param inputDirection: the current direction the ball is moving. This parameter must 
        be specified if the ball is moving. If the ball is not moving, then leave this 
        parameter blank. 
        
    :type worldRef: keepAway
    :type inputDirection: tuple of floats
    
    :returns: tuple, where first element is the index of the keeper picked to run towards
        the ball. The simulator will use this index to look up the index of the keeper 
        in its self.keeperArray. The 2nd element is the intersection coordinate
    :rtype: tuple where first element is integer, second element is tuple. 2nd element
        tuple contains integers

    """
    #keep track of which keeper is currently the possessing keeper.
    #this way, you don't try to pass to yourself.
    posessingKeeperIndex = None
    for keeper in worldRef.keeperArray:
        if keeper.inPosession == True:
            posessingKeeperIndex = keeper.agentListIndex
            break
        
    #you're either calculating a hypothetical pass, or the actual pass
    """
    if inputDirection == None:
        print("calc recieve for ball. ")
        if(worldRef.fieldBall.trueBallDirection == (0.0, 0.0)):
            print("ball is stationary") 
        else:
            print("ball is moving") 
        inputDirection = worldRef.fieldBall.trueBallDirection
    """
    if inputDirection == None:
        inputDirection = worldRef.fieldBall.trueBallDirection
    
    
    if(inputDirection == (0.0, 0.0))== False:
        rDecision = __calc_receive_ball_moving(worldRef, inputDirection, posessingKeeperIndex)
    else:
        mimimum = 99999.0
        argmin = None
        for i in range(len(worldRef.keeperArray)):
            temp = kUtil.getDist(worldRef.fieldBall.trueBallPos, worldRef.keeperTruePosArray[i])
            if (temp < mimimum and i != posessingKeeperIndex):
                mimimum = temp
                argmin = i
        rDecision = [argmin, worldRef.fieldBall.trueBallPos]
    return rDecision
            
#go and calulcate the receive() information and send it over to the agents
#This function is automatically called by the wrapper function 
#calc_receive. The wrapper calls __calc_receive_ball_moving if the ball is
#moving, because that computation is pretty complicated
def __calc_receive_ball_moving(worldRef, inputDirection, possessingKeeperIndex):
    """
    This function is a private function meant to assist calc_receive. This function 
    will go and calculate the receive decision for the special case where the 
    ball is moving. The receive decision is a tuple that simply contains the 
    index of the keeper that should run towards the ball, and the coordinate 
    that the keeper should run to. 
    If the ball is moving, then calc_receieve will find an intersection point
    along the balls projected path that the selected keeper can run to. 
    The intercept point is selected such that the 
    selected keeper will run a short distance, be far away from the takers, 
    and also be far away from out of bounds.  
    
    .. note::
        This is a private function that the user shouldn't worry about calling.
        Only the calc_receieve function of this method will use this function.
        And only the simulator class should call the calc_receive function. 
    
    :param worldRef: a reference to the simulator class which is calling this function
    :param inputDirection: the current direction the ball is moving.
    :param possessingKeeperIndex: the index of the keeper who currently has possession
        
    :type worldRef: keepAway
    :type inputDirection: tuple of floats
    :type possessingKeeperIndex: integer
    
    :returns: tuple, where first element is the index of the keeper picked to run towards
        the ball. The simulator will use this index to look up the index of the keeper 
        in its self.keeperArray. The 2nd element is the intersection coordinate
    :rtype: tuple where first element is integer, second element is tuple. 2nd element
        tuple contains integers

    """
    #TA is a point that the ball is heading to in the next time step      
    TA = kUtil.addVectorToPoint(worldRef.fieldBall.trueBallPos, inputDirection)
    #TB is the current ball position, and for angle calculations, it will be the vertex
    TB = worldRef.fieldBall.trueBallPos
    minTime = float("inf")
    argmin = None
    bestPerpIntersect = None
    #the purpose of this for loop is to find which keeper should go to the ball. 
    for i in range(len(worldRef.keeperArray)):
        #TC is the position of the keeper who's figuring out if he should goToBall(), or getOpen()
        TC = worldRef.keeperTruePosArray[i]
        if (kUtil.cosTheta(TA, TB, TC)) < 0:
            #print "Keeper " , i, " can't get to ball: the cosTheta is negetive."
            #it's impossible for this keeper to get the ball
            continue 
        else:
            pd = kUtil.getPerpDist(TA, TB, TC)
            pt = pd/worldRef.maxPlayerSpeed
            normalVector = kUtil.getNormalVector(TA, TB, TC)
            perpIntersect = kUtil.addVectorToPoint(TC, normalVector)
            bd = kUtil.getDist(TB, perpIntersect)
            bt = bd/worldRef.maxBallSpeed
            if pt > bt:
                #keeper wont' be able be able to get to ball in time
                #print "player ", i+1, "can't reach ball as pt:",pt," and bt: ",bt 
                continue
            else:
                #keeper CAN get to ball. can it get there soonest though?
                #save the fastest keeper
                if (pt < minTime and i !=  possessingKeeperIndex):
                    minTime = pt
                    argmin = i
                    bestPerpIntersect = perpIntersect
    #at this point, if a keeper can get to the ball, 
    #the fastest and it's intercept are saved
    if (argmin != None):
        rDecision = [argmin, __calcOptimal(worldRef, worldRef.keeperArray, argmin, bestPerpIntersect)]
        return rDecision
    else:
		rDecision = [1 , worldRef.get_field_center()]
		#print("no argmin found. game about to end for sure.")
		return rDecision
    
#once an agent is determined to be the one in best position to get to the ball, then 
#the next step is to try intercepting it. Calc optimal will check to see if the 
#perpendicular intercept is out of play region. If so, it will iteratively change
#the intersection point until the agent can get to the ball within the play region
def __calcOptimal(worldRef, agentList, i, intersect):
    """
    This function is a private function meant to assist another private function called
    __calc_receive_ball_moving. 
    
    once __calc_receive_ball_moving has calculated the intersection point, there's 
    one last step: to make sure that the intersection point isn't too close to 
    the out of bounds area. If the intersection point too close to out of bounds, 
    then return an intersection point along the path that the ball is traveling, but
    is just still safely away from the out of bounds areas. 
    
    
    .. note::
        This is a private function that the user shouldn't worry about calling.
        Only the calc_receive function should be called.  
    
    :param worldRef: a reference to the simulator class which is calling this function
    :param agentList: a list provided by the simulator of all agents
    :param i: the index of the agent running to the ball for the list agentList
    :param intersect: the intersection point that has been calculated, and might be too
        close to out of bounds

        
    :type worldRef: keepAway class
    :type agentList: a list where each element is an agent class
    :type i: integer
    :type intersect: a tuple of floats
    
    :returns: the intersection coordinate which is safely within bounds, or the original
        intersection point if no such point is found
    :rtype: tuple of floats

    """
    #if the intersect is in bounds, just go to it. no calculations needed
    if __isPointOutOfPlayRegion(worldRef, intersect, agentList, i) == False:
        #print("point in bounds, return intersect") 
        return intersect
        
    #V = vector from agent's perpendicular intercept to the ball
    V = kUtil.getVector(intersect, worldRef.fieldBall.trueBallPos)
    #turn V into a unit vector and multipy it by the speed of the ball to get velocity vector
    UV = kUtil.unitVector(V)
    stepVector = kUtil.scalarMultiply(worldRef.maxBallSpeed, UV)
        
    #the optimal point is intialized to the intersect, and 
    #the intersect is currently out of bounds.
    #keep adding the step vector to the optimal point until
    #the intersect is no longer out of bounds
    optimalPoint = intersect
    maxNumSteps = int(kUtil.getDist(worldRef.fieldBall.trueBallPos, intersect)/ worldRef.maxBallSpeed)
    stepCount = 0
    #if you can't get to the ball in maxNumSteps, then it's hopeless. simply
    #return the intersection point. Your agent will fail and the ball will
    #go out of bounds, but there's nothing that can be done
    for k in range(maxNumSteps):
        optimalPoint = kUtil.addVectorToPoint(optimalPoint, stepVector)
        stepCount += 1
        if __isPointOutOfPlayRegion(worldRef, optimalPoint, agentList, i) == False:
            #print("Optimal found, returning optimal point:", optimalPoint) 
            return optimalPoint
    #if you get here, then no closer optimal was found
    #print("no optimal found, returning intersect", intersect) 
    return intersect
    
#simple function to check if a point is outside of the playable region defined by the player
def __isPointOutOfPlayRegion(worldRef, pointOfInterest, agentList, agentIndex):
    """
    This function is a private function meant to assist another private function called
    __calcOptimal. 
    
    This function will simply check to see if a point is too close to the out of bounds
    region. Returns true if out of safe region, false otherwise.
    
    
    .. note::
        This is a private function that the user shouldn't worry about calling.
        Only the calc_receive function should be called.  
    
    :param worldRef: a reference to the simulator class which is calling this function
    :param pointOfInterest: the point that is being checked to see if it is too
        close to the out of bounds region
    :param agentList: a list of all agents
    :param agentIndex: the index of the agent running to the ball for the list agentList
    

        
    :param worldRef: keepAway class
    :param pointOfInterest: tuple of floats
    :param agentList: a list where each element is of type agent class
    :param agentIndex: integer
    
    
    :returns: true if the point is too close to out of bounds, false otherwise
    :rtype: boolean

    """
    topLeft = agentList[agentIndex].playableRegionTopLeft
    bottomRight = agentList[agentIndex].playableRegionBottomRight
    rowPixel1 = pointOfInterest[0]
    colPixel1 = pointOfInterest[1]
    rowPixel2 = rowPixel1 + worldRef.get_agent_block_size()
    colPixel2 = colPixel1 + worldRef.get_agent_block_size()
    #print "rowPixel1:", rowPixel1, " colPixel1: ", colPixel1, " rowPixel2:", rowPixel2, " colPixel2:",colPixel2 
    #check to see if you go outside the boundaries of the game    
    if rowPixel1 < topLeft[0] or colPixel1 < topLeft[1] or rowPixel2 > bottomRight[0] -1 or colPixel2 > bottomRight[1] - 1:  
        return True
    else:
        return False
    
