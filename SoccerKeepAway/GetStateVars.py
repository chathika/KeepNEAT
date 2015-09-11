import agent, StateVars
import kUtil, unittest
import math


"""
Get all the state variables as a list.
input = list of keepers and takers and the center coordinate of the field.
output = list of all state variables.
"""
def getStateVarsKeepers(keepers,takers,center):
    returnList = []
    keeperActual = sorted(keepers)
    takerActual = sorted(takers)
    
    for i in range(len(keeperActual)):
        returnList.append(StateVars.distCenter(keeperActual[i], center))
        
    for i in range(len(takerActual)):
        returnList.append(StateVars.distCenter(takerActual[i], center))
    
    
    for i in range(1,len(keeperActual)):
        returnList.append(StateVars.distAgent(keeperActual[0], keeperActual[i]))
    
    for i in range(len(takerActual)):
        returnList.append(StateVars.distAgent(keeperActual[0], takerActual[i]))
    
    
    returnList.append(min(StateVars.distAgent(keeperActual[1], takerActual[0]),StateVars.distAgent(keeperActual[1], takerActual[1])))
    returnList.append(min(StateVars.distAgent(keeperActual[2], takerActual[0]),StateVars.distAgent(keeperActual[2], takerActual[1])))
    returnList.append(max(StateVars.getCosAngle(keeperActual[1], keeperActual[0], takerActual[0]),StateVars.getCosAngle(keeperActual[1], keeperActual[0], takerActual[1])))
    returnList.append(max(StateVars.getCosAngle(keeperActual[2], keeperActual[0],takerActual[0]),StateVars.getCosAngle(keeperActual[2], keeperActual[0], takerActual[1])))

    return returnList

# Unit test complete.

class testingCode(unittest.TestCase):
    
    def test_getStateVars(self):
        #self, worldRef, pos, sigma, agentType, trueBallPos, maxPlayerSpeed, maxBallSpeed, inPossession = False
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        ballPos = (0,0)
        center = (0,0)
        simulatedError = 0.01
        a1 = agent.agent(keepAwayWorld, (10,0),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a2 = agent.agent(keepAwayWorld,(0,0),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a3 = agent.agent(keepAwayWorld,(0,5),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        keepers = [a1,a2,a3]
        t1 = agent.agent(keepAwayWorld,(5,5),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        t2 = agent.agent(keepAwayWorld,(5,0),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        takers = [t1,t2]
        testOut = getStateVarsKeepers(keepers, takers, center)
        actualOut = [0,5,10,5,math.sqrt(50),5,10,5,math.sqrt(50),5,5,math.cos(math.pi / 4.0),1]
        for i in range(len(testOut)):
            self.assertAlmostEqual(testOut[i], actualOut[i], 1)
    #new test case. variables are given in order
    def test_getStateVars2(self):
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        simulatedError = 0.01
        simWidth = 550.0
        simHeight = 357.0
        ballPos = (1/3 * simWidth,1/6 * simHeight)
        c = (simWidth /2.0,simHeight/2.0)
        a1 = agent.agent(keepAwayWorld,(1/3 * simWidth,1/6 * simHeight),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a2 = agent.agent(keepAwayWorld,(2/3 * simWidth,1/7 * simHeight),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a3 = agent.agent(keepAwayWorld,(2/5 * simWidth,6/7 * simHeight),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        keepers = [a1,a2,a3]
        t1 = agent.agent(keepAwayWorld,(1/2 * simWidth,5/12 * simHeight),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        t2 = agent.agent(keepAwayWorld,(2/5 * simWidth,7/12 * simHeight),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        takers = [t1,t2]
        testOut = getStateVarsKeepers(keepers, takers, c)
        actualOut = [kUtil.getDist((550/3, 59.5), c),
                     kUtil.getDist((550/3 * 2, 51), c),
                     kUtil.getDist((220, 306), c),
                     kUtil.getDist((275, 148.75), c),
                     kUtil.getDist((220, 208.25), c),
                     kUtil.getDist((550/3,59.5), (550/3*2, 51)),
                     kUtil.getDist((550/3,59.5), (220,306)),
                     kUtil.getDist((550/3,59.5), (275, 148.75)),
                     kUtil.getDist((550/3,59.5), (220, 208.25)),
                     min( kUtil.getDist((550/3*2,51), (220, 208.25)), kUtil.getDist((550/3*2,51), (275, 148.75)) ),
                     min( kUtil.getDist((220,306), (220, 208.25)), kUtil.getDist((220,306), (275, 148.75)) ),
                     max(kUtil.cosTheta((550/3*2, 51), (550/3,59.5), (275,148.75)), 
                         kUtil.cosTheta((550/3*2, 51), (550/3,59.5), (220,208.25))),
                     max(kUtil.cosTheta((220,306), (550/3,59.5), (275,148.75)), 
                         kUtil.cosTheta((220,306), (550/3,59.5), (220,208.25))),
                     ]
        for i in range(len(testOut)):
            self.assertAlmostEqual(testOut[i], actualOut[i], 1,"Failed on index: %d" % i)
     
        
        
if __name__ == "__main__":
    print ('Unit Testing')
    unittest.main()
    
