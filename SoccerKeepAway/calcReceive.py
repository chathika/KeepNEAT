#note: the whole purpose of this class is to return the tuple called
#rDecision = (keeperIndex_to_go_after_ball, intersection_coordinate)

import kUtil
#calculate the receive() for if the ball is stationary
#or moving. calcuations for stationary are done in this 
#fucntion. the function for when the ball is moving
#is done in the other function
def calc_receive(worldRef, inputDirection = None):
    #keep track of which keeper is currently the possessing keeper.
    #this way, you don't try to pass to yourself.
    posessingKeeperIndex = None
    for keeper in worldRef.keeperArray:
        if keeper.inPosession == True:
            posessingKeeperIndex = keeper.agentListIndex
            break
        
    #you're either calculating a hypothetical pass, or the actual pass
    if inputDirection == None:
        print "calc recieve for ball. "
        if(worldRef.fieldBall.trueBallDirection == (0.0, 0.0)):
            print "ball is stationary" 
        else:
            print "ball is moving" 
        inputDirection = worldRef.fieldBall.trueBallDirection
    
    if(inputDirection == (0.0, 0.0))== False:
        rDecision = calc_receive_ball_moving(worldRef, inputDirection, posessingKeeperIndex)
    else:
        mimimum = 99999.0
        argmin = None
        for i in range(len(worldRef.keeperArray)):
            temp = kUtil.getDist(worldRef.fieldBall.trueBallPos, worldRef.keeperArray[i].true_pos)
            if (temp < mimimum and i != posessingKeeperIndex):
                mimimum = temp
                argmin = i
        rDecision = [argmin, worldRef.fieldBall.trueBallPos]
    return rDecision
            
#go and calulcate the receive() information and send it over to the agents
#This function is automatically called by the wrapper function 
#calc_receive. The wrapper calls calc_receive_ball_moving if the ball is
#moving, because that computation is pretty complicated
def calc_receive_ball_moving(worldRef, inputDirection, posessingKeeperIndex):
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
        TC = worldRef.keeperArray[i].true_pos
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
                if (pt < minTime and i !=  posessingKeeperIndex):
                    minTime = pt
                    argmin = i
                    bestPerpIntersect = perpIntersect
    #at this point, if a keeper can get to the ball, 
    #the fastest and it's intercept are saved
    if (argmin != None):
        rDecision = [argmin, calcOptimal(worldRef, worldRef.keeperArray, argmin, bestPerpIntersect)]
        return rDecision
    else:
        print "no argmin found. game about to crash for sure"
        return None
            
#once an agent is determined to be the one in best position to get to the ball, then 
#the next step is to try intercepting it. Calc optimal will check to see if the 
#perpendicular intercept is out of play region. If so, it will iteratively change
#the intersection point until the agent can get to the ball within the play region
def calcOptimal(worldRef, agentList, i, intersect):
    #if the intersect is in bounds, just go to it. no calculations needed
    if isPointOutOfPlayRegion(worldRef, intersect, agentList, i) == False:
        print "point in bounds, return intersect" 
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
        """
        currPd = kUtil.getDist(optimalPoint,agentList[i].true_pos)
        currBd = kUtil.getDist(self.fieldBall.trueBallPos, optimalPoint)
        currPt = currPd / self.maxPlayerSpeed
        currBt = currBd / self.maxBallSpeed
        if currPt < currBt:
            #found the optimal, so return it
            return optimalPoint
        """
        if isPointOutOfPlayRegion(worldRef, optimalPoint, agentList, i) == False:
            print "Optimal found, returning optimal point:", optimalPoint 
            return optimalPoint
    #if you get here, then no closer optimal was found
    print "no optimal found, returning intersect", intersect 
    return intersect
    
#simple function to check if a point is outside of the playable region defined by the player
def isPointOutOfPlayRegion(worldRef, pointOfInterest, agentList, agentIndex):
    topLeft = agentList[agentIndex].playableRegionTopLeft
    bottomRight = agentList[agentIndex].playableRegionBottomRight
    rowPixel1 = pointOfInterest[0]
    colPixel1 = pointOfInterest[1]
    rowPixel2 = rowPixel1 + worldRef.agent_block_size
    colPixel2 = colPixel1 + worldRef.agent_block_size
    #print "rowPixel1:", rowPixel1, " colPixel1: ", colPixel1, " rowPixel2:", rowPixel2, " colPixel2:",colPixel2 
    #check to see if you go outside the boundaries of the game    
    if rowPixel1 < topLeft[0] or colPixel1 < topLeft[1] or rowPixel2 > bottomRight[0] -1 or colPixel2 > bottomRight[1] - 1:  
        return True
    else:
        return False
    