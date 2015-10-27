<<<<<<< HEAD
"""
This module contains the function that will be called to train the NEAT agent

"""
import unittest
import math
import MultiNEAT as NEAT
import pygame

params = NEAT.Parameters()
params.PopulationSize = 150
params.DynamicCompatibility = True
params.WeightDiffCoeff = 4.0
params.CompatTreshold = 2.0
params.YoungAgeTreshold = 15
params.SpeciesMaxStagnation = 15
params.OldAgeTreshold = 35
params.MinSpecies = 5
params.MaxSpecies = 25
params.RouletteWheelSelection = False  #Original value = False
params.RecurrentProb = 0.0
params.OverallMutationRate = 0.8

params.MutateWeightsProb = 0.90

params.WeightMutationMaxPower = 2.5
params.WeightReplacementMaxPower = 5.0
params.MutateWeightsSevereProb = 0.5
params.WeightMutationRate = 0.25

params.MaxWeight = 8

params.MutateAddNeuronProb = 0.03
params.MutateAddLinkProb = 0.05
params.MutateRemLinkProb = 0.0

params.MinActivationA  = 4.9
params.MaxActivationA  = 4.9

params.ActivationFunction_SignedSigmoid_Prob = 0.0
params.ActivationFunction_UnsignedSigmoid_Prob = 1.0
params.ActivationFunction_Tanh_Prob = 0.0
params.ActivationFunction_SignedStep_Prob = 0.0

params.CrossoverRate = 0.75  # mutate only 0.25
params.MultipointCrossoverRate = 0.4
params.SurvivalRate = 0.2


def evaluate(worldRef, genome):
	net = NEAT.NeuralNetwork()
    genome.BuildPhenotype(net)
	worldRef.displayGraphics = False
	while worldRef.isGameOver() == False:
		for event in pygame.event.get():
		    if event.type == pygame.QUIT:
		        gameExit = True
		worldRef._sendCalcReceiveDecision()
        worldRef._sendStateVars()
        #reward = 100000

        for keeper in worldRef.keeperArray:
            
			keeper.receiveNN(net)
            keeper._decisionFlowChart()
        for taker in worldRef.takerArray:
            taker.decisionFlowChart()
        
		'''    
        newBallPoint = kUtil.addVectorToPoint(worldRef.fieldBall.trueBallPos, kUtil.scalarMultiply(worldRef.maxBallSpeed, kUtil.unitVector(worldRef.fieldBall.trueBallDirection)))
        worldRef.fieldBall.updateCoordinate(newBallPoint)
        for i in range(len(worldRef.takerArray)):
            worldRef.takerArray[i].noisyBallPos = kUtil.getNoisyVals(worldRef.fieldBall.trueBallPos, worldRef.takerArray[i].sigma)
        for i in range(len(worldRef.keeperArray)):
            worldRef.keeperArray[i].noisyBallPos = kUtil.getNoisyVals(worldRef.fieldBall.trueBallPos, worldRef.keeperArray[i].sigma)                
        worldRef.updateBallPosession()
        worldRef.updateScore()
        if(worldRef.displayGraphics == True):
            worldRef.drawWorld ()
            worldRef.displayScore()
            pygame.display.update()
        '''
        worldRef.clock.tick(10000)

	return worldRef.keeperScore

	



def train(worldRef):

	g = NEAT.Genome(0, 14, 3, 1, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)
    pop = NEAT.Population(g, params, True, 1.0, i)
    pop.RNG.Seed(i)

    generations = 0
    for generation in range(1000):
        genome_list = NEAT.GetGenomeList(pop)
        fitness_list = NEAT.EvaluateGenomeList_Serial(genome_list, evaluate, display=False)
        NEAT.ZipFitness(genome_list, fitness_list)

        best,index = max([(x.GetLeader().GetFitness(),y) for y,x in enumerate(pop.Species)])
        best_genome_ever = pop.Species[index].GetLeader()

	net = NEAT.NeuralNetwork()
    best_genome_ever.BuildPhenotype(net)

	for keeper in worldRef.keeperArray:
		keeper.receiveBest(net)
    
    return True
=======
>>>>>>> a0bb770f2892b86f036c11f56a56b4112e24ef8d
