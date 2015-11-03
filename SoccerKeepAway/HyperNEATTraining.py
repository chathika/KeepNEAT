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

import cPickle
import os.path

import matplotlib.pyplot as plt

params = NEAT.Parameters()
params.PopulationSize = 150

'''
params.DynamicCompatibility = True
params.AllowClones = True
params.CompatTreshold = 5.0
params.CompatTresholdModifier = 0.3
params.YoungAgeTreshold = 15
params.SpeciesMaxStagnation = 100
params.OldAgeTreshold = 35
params.MinSpecies = 3
params.MaxSpecies = 10
params.RouletteWheelSelection = True
params.RecurrentProb = 0.0
params.OverallMutationRate = 0.02
params.MutateWeightsProb = 0.90
params.WeightMutationMaxPower = 1.0
params.WeightReplacementMaxPower = 5.0
params.MutateWeightsSevereProb = 0.5
params.WeightMutationRate = 0.75
params.MaxWeight = 20
params.MutateAddNeuronProb = 0.01
params.MutateAddLinkProb = 0.02
params.MutateRemLinkProb = 0.00
params.DivisionThreshold = 0.5
params.VarianceThreshold = 0.03
params.BandThreshold = 0.3
params.InitialDepth = 3
params.MaxDepth = 4
params.IterationLevel = 1
params.Leo = False #Initially True
params.GeometrySeed = False #Initially True
params.LeoSeed = False #Initially True
params.LeoThreshold = 0.3
params.CPPN_Bias = 1.0
params.Qtree_X = 0.0
params.Qtree_Y = 0.0
params.Width = 1.
params.Height = 1.
params.Elitism = 0.1
params.CrossoverRate = 0.5
params.MutateWeightsSevereProb = 0.01
params.MutateActivationAProb = 0.0;
params.ActivationAMutationMaxPower = 0.5;
params.MinActivationA = 0.05;
params.MaxActivationA = 6.0;

params.MutateNeuronActivationTypeProb = 0.03;
'''

params.DynamicCompatibility = True;
params.CompatTreshold = 2.0;
params.YoungAgeTreshold = 15;
params.SpeciesMaxStagnation = 100;
params.OldAgeTreshold = 35;
params.MinSpecies = 5;
params.MaxSpecies = 25;
params.RouletteWheelSelection = False;

params.MutateRemLinkProb = 0.02;
params.RecurrentProb = 0;
params.OverallMutationRate = 0.15;
params.MutateAddLinkProb = 0.08;
params.MutateAddNeuronProb = 0.01;
params.MutateWeightsProb = 0.90;
params.MaxWeight = 8.0;
params.WeightMutationMaxPower = 0.2;
params.WeightReplacementMaxPower = 1.0;

params.MutateActivationAProb = 0.0;
params.ActivationAMutationMaxPower = 0.5;
params.MinActivationA = 0.05;
params.MaxActivationA = 6.0;

params.MutateNeuronActivationTypeProb = 0.03;


params.ActivationFunction_SignedSigmoid_Prob = 0.0;
params.ActivationFunction_UnsignedSigmoid_Prob = 1.0;
params.ActivationFunction_Tanh_Prob = 1.0;
params.ActivationFunction_TanhCubic_Prob = 0.0;
params.ActivationFunction_SignedStep_Prob = 1.0;
params.ActivationFunction_UnsignedStep_Prob = 0.0;
params.ActivationFunction_SignedGauss_Prob = 1.0;
params.ActivationFunction_UnsignedGauss_Prob = 0.0;
params.ActivationFunction_Abs_Prob = 1.0;
params.ActivationFunction_SignedSine_Prob = 1.0;
params.ActivationFunction_UnsignedSine_Prob = 0.0;
params.ActivationFunction_Linear_Prob = 1.0;

rng = NEAT.RNG()
rng.TimeSeed()




def evaluate(worldRef, genome, substrate, i, display = False):
	screen = pygame.display.set_mode((600, 600))
	space = pm.Space()
	clock = pygame.time.Clock()
	#print("Starting evaluation ",i)
	net = NEAT.NeuralNetwork()
	try:
		genome.BuildHyperNEATPhenotype(net, substrate)
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
			worldRef._sendBirdsEyeView()
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
				img = np.zeros((450, 450, 3), dtype=np.uint8)
				img += 10
				NEAT.DrawPhenotype(img, (0, 0, 450, 450), net ,15, 3, substrate)
				cv2.imshow("current best", img)
				cv2.waitKey(1)

				## Draw stuff
				screen.fill(THECOLORS["black"])

				### Draw stuff
				draw(screen, space)

				### Flip screen
				pygame.display.flip()
				clock.tick(10000)


			worldRef.commonFunctionality(showDisplay)
			worldRef.clock.tick(10000)

		#print("Ending Evaluation ",i)

		return worldRef.keeperScore
	
	except Exception as ex:
		print('Exception:', ex)
		return 1.0

	



def train(worldRef):

	print("Entering training")
	best_fitness_per_generation = []
	species_per_generation = []
	nodes_per_generation = []
	links_per_generation = []
	
	i=1
	'''
	fileExists = os.path.isfile('NEAT_Population/population')
	if fileExists:
		print("There is a previous stored population, loading it")
		with open('NEAT_Population/population', 'rb') as f:
			pop = cPickle.load(f)
		print("Printing loaded popuation")
		for s in pop.Species:
			for i in s.Individuals:
				print("Fitness: ",i.GetFitness())
	else:
	'''
	substrate = NEAT.Substrate(worldRef.bev_substrate,
                           [],
                           worldRef.bev_substrate)
	#substrate.m_with_distance = True;

	print("Printing the substrate")
	print(worldRef.bev_substrate)

	substrate.m_allow_input_hidden_links = False
	substrate.m_allow_input_output_links = False
	substrate.m_allow_hidden_hidden_links = False
	substrate.m_allow_hidden_output_links = False
	substrate.m_allow_output_hidden_links = False
	substrate.m_allow_output_output_links = False
	substrate.m_allow_looped_hidden_links = False
	substrate.m_allow_looped_output_links = False

	# let's set the activation functions
	substrate.m_hidden_nodes_activation = NEAT.ActivationFunction.SIGNED_SIGMOID
	substrate.m_output_nodes_activation = NEAT.ActivationFunction.TANH

	# when to output a link and max weight
	substrate.m_link_threshold = 0.2
	substrate.m_max_weight_and_bias = 8.0
	
	fileExists = False
	#fileExists = os.path.isfile('HyperNEAT_Population/population.txt')
	#fileExists = os.path.isfile('HyperNEAT_Population/genome.txt')
	if fileExists:
		print("There is a previous stored population, loading it")
		#f = open('HyperNEAT_Population/population.txt', 'r')
		#print (f)
		#pop = NEAT.Population('HyperNEAT_Population/population.txt')
		#g = NEAT.Genome('HyperNEAT_Population/genome.txt')
		'''		
		print("Printing loaded popuation")
		for s in pop.Species:
			for i in s.Individuals:
				print("Fitness: ",i.GetFitness())
		'''
	else:
		g = NEAT.Genome(0,
                    substrate.GetMinCPPNInputs(),
                    0,
                    substrate.GetMinCPPNOutputs(),
                    False,
                    NEAT.ActivationFunction.TANH,
                    NEAT.ActivationFunction.TANH,
                    0,
                    params)

		pop = NEAT.Population(g, params, True, 1.0,i)
		pop.RNG.Seed(i)
	generations = 0
	global_best = 0
	for generation in range(10):
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
				fitness += evaluate(worldRef,gen,substrate,i,True)
			gen.SetFitness((fitness/5))

		best,index = max([(x.GetLeader().GetFitness(),y) for y,x in enumerate(pop.Species)])
		best_genome_this_run = pop.Species[index].GetLeader()
		if best > global_best:
			best_genome_ever = best_genome_this_run
			global_best = best

		evaluate(worldRef,best_genome_this_run,substrate,index,True)
		best_fitness_per_generation.append(best)
		species_per_generation.append(len(pop.Species))
		nodes_per_generation.append(best_genome_this_run.NumNeurons())
		links_per_generation.append(best_genome_this_run.NumLinks())
		#print("The best genome is: ",best_genome_this_run)
		#print("The best genome type is: ",type(best_genome_this_run))
		locationToSave = "HyperNEAT_Test/Generation_"+str(generation)+".txt"
		best_genome_this_run.Save(locationToSave)
		pop.Epoch()

		print("Generation: ",generation)
		print("Best Fitness", best)

		generations = generation

		if best > 7000:
			break

	net = NEAT.NeuralNetwork()
	best_genome_ever.BuildHyperNEATPhenotype(net,substrate)

	for keeper in worldRef.keeperArray:
		keeper.receiveBest(net)

	worldRef.displayGraphics = True

	print("Ending Training")
	'''
	print("About to store pickle object")
	print("Printing population before storing:")
	for s in pop.Species:
		for i in s.Individuals:
			print("Fitness: ",i.GetFitness())
	with open('NEAT_Population/population', 'wb') as f:
            cPickle.dump(pop, f)
	'''
	best_genome_ever.Save('HyperNEAT_Population/genome.txt')

	worldRef.resetGameForTraining()
	plt.plot(best_fitness_per_generation)
	plt.xlabel("Generation")
	plt.ylabel("Maximum Fitness per Genetation")
	plt.title("Maximum Fitness per Generation for NEAT Agent")
	plt.show()
	plt.hold()


	plt.plot(species_per_generation)
	plt.xlabel("Generation")
	plt.ylabel("Number of Species per Genetation")
	plt.title("Number of Species per Generation for NEAT Agent")
	plt.show()
	plt.hold()


	plt.plot(nodes_per_generation)
	plt.xlabel("Generation")
	plt.ylabel("Number of Nodes in Genome of Fittest Individual per Genetation")
	plt.title("Number of Nodes in Genome of Fittest Individual per Generation for NEAT Agent")
	plt.show()
	plt.hold()


	plt.plot(links_per_generation)
	plt.xlabel("Generation")
	plt.ylabel("Number of Links in Genome of Fittest Individual per Genetation")
	plt.title("Number of Links in Genome of Fittest Individual per Generation for NEAT Agent")
	plt.show()

	
	return True


