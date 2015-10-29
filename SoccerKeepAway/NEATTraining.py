"""
This module contains the function that will be called to train the NEAT agent

"""
import unittest
import math
import MultiNEAT as NEAT
import pygame
import numpy as np
import cv2
from pygame.locals import *
from pygame.color import *

import pymunk as pm
from pymunk import Vec2d
from pymunk.pygame_util import draw, from_pygame

params = NEAT.Parameters()
params.PopulationSize = 150
params.DynamicCompatibility = True
params.AllowClones = True
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

params.Elitism = 0.1



def evaluate(worldRef, genome, i, display = False):
	screen = pygame.display.set_mode((600, 600))
	space = pm.Space()
	clock = pygame.time.Clock()
	#print("Starting evaluation ",i)
	net = NEAT.NeuralNetwork()
	genome.BuildPhenotype(net)
	worldRef.displayGraphics = True
	worldRef.resetGameForTraining()
	#print("Game reset for training")
	#counter = 0
	showDisplay = display
	while worldRef.isGameOver() == False:
		#print("Entering while game is not over for ",counter,"  time")
		#counter += 1
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
			    gameExit = True
		worldRef._sendCalcReceiveDecision()
		worldRef._sendSimpleStateVars()
		#reward = 100000

		for keeper in worldRef.keeperArray:
			keeper.receiveNN(net)
			#print(super(keeper))
			keeper.decisionFlowChart("NEAT trying to move")
		for taker in worldRef.takerArray:
			taker.decisionFlowChart("NEAT trying to move")
		
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
		if(display):
			# draw the phenotype
			img = np.zeros((250, 250, 3), dtype=np.uint8)
			img += 10
			NEAT.DrawPhenotype(img, (0, 0, 250, 250), net )
			cv2.imshow("current best", img)
			cv2.waitKey(1)

			## Draw stuff
			screen.fill(THECOLORS["black"])

			### Draw stuff
			draw(screen, space)

			### Flip screen
			pygame.display.flip()
			clock.tick(50)


		worldRef.commonFunctionality(showDisplay)
		worldRef.clock.tick(10000)

	#print("Ending Evaluation ",i)

	return worldRef.keeperScore

	



def train(worldRef):

	print("Entering training")
	i=1

	g = NEAT.Genome(0, 14, 0, 3, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)
	pop = NEAT.Population(g, params, True, 1.0,i)
	pop.RNG.Seed(i)
	generations = 0
	global_best = 0
	for generation in range(5):
		#genome_list = NEAT.GetGenomeList(pop)
		#fitness_list = NEAT.EvaluateGenomeList_Serial(genome_list, evaluate, display=False)
		#NEAT.ZipFitness(genome_list, fitness_list)

		genome_list = []
		for s in pop.Species:
			for i in s.Individuals:
				genome_list.append(i)
		
		print('All individuals:', len(genome_list))
		
		
		for i,gen in enumerate(genome_list):
			fitness = 0
			for j in range(5):
				fitness += evaluate(worldRef,gen,i)
			gen.SetFitness((fitness/5))

		best,index = max([(x.GetLeader().GetFitness(),y) for y,x in enumerate(pop.Species)])
		best_genome_this_run = pop.Species[index].GetLeader()
		if best > global_best:
			best_genome_ever = best_genome_this_run

		evaluate(worldRef,best_genome_this_run,index,True)

		pop.Epoch()

		print("Generation: ",generation)
		print("Best Fitness", best)

		generations = generation

		if best > 7000:
			break

	net = NEAT.NeuralNetwork()
	best_genome_ever.BuildPhenotype(net)

	for keeper in worldRef.keeperArray:
		keeper.receiveBest(net)

	worldRef.displayGraphics = True

	print("Ending Training")
	worldRef.resetGameForTraining()
	
	return True

