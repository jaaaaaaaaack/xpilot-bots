# Jack Beal and Lydia Morneault
# COM-407 CI
# 2018-05-07 Final project
# Evolutionary strategy control script

import subprocess
import math
from random import *


def fitness(c):
    # Assess fitness of an individual chromosome, c
    # Returns an integer fitness value, hopefully

    # cmd = ["python3", "Individual.py", "-g", c]
    p = subprocess.call(["python3", "es-agent.py", "-g", str(c)])

    with open("fitness.txt", 'r') as inputFile:
        fitness = inputFile.readlines()[-1]
        # print("Fitness Split \t", eval(fitness.split()[0]))#debug

    return eval(fitness.split()[0])

def boltzmann_cooling(initial, beta):
    # Generator function for Boltzmann cooling
    # Returns an iterable!
    t = initial
    c = 0
    while True:
        yield t
        t = (beta**c)*t
        c += 1

def kirkpatrick_cooling(intial, alpha):
    # Generator function for Kirkpatrick cooling
    # Returns an iterable!
    t = initial
    while True:
        yield t
        t = alpha*t

def getNewChromosome(c, rangeList):
    # Expects rangelist to be a list of tuples
    # in which tuples are (min, max, stdev)
    if len(c) != len(rangeList):
        print("Chromosome and rangelist are of different lengths.")#debug
    for i in range(len(rangeList)):
        r = rangeList[i][2]
        halfr = rangeList[i][2]/2
        c[i] += (uniform(0,r)-halfr)
    return c

def acceptanceProbability(currentFitness, nextFitness, t):
    try:
        a = math.e**((nextFitness-currentFitness)/t)
    except OverflowError:
        print("acceptanceProbability calculated a huge number and overflowed!")
        print("Returning math.inf")
        return math.inf
    return a


def anneal(c, rangeList):
    print("Annealing!")#debug

    # Wipe out the bookkeeping file
    open("es-selections.txt", "w").close()

    t = 1.0          # Initial temperature
    tMin = 0.00001   # Termination point
    alpha = 0.99     # Cooling rate (should be <1)
    tries = 20       # Number of neighboring solutions to check

    print("Generating temperatures...")#debug
    print("T =", t, "\ttMin = ", tMin, "\ta =", alpha, "\ttries =", tries)#debug
    # Make an iterable! This bit is a fun trick.
    temperatures = boltzmann_cooling(t, alpha)

    bestEver = [0, []] # Hold the best ever individual
    currentFitness = fitness(c)

    while t > tMin:
        print("Temperature:", t)#debug
        i = 1

        # Check a number of neighboring solutions
        print("Attempting neighboring solutions...")#debug
        while i <= tries:
            print("Trying solution", i, "of", tries, "\t Temperature:", t)#debug

            nextc = getNewChromosome(c, rangeList)

            print("Getting fitness of chromosome", nextc)#debug
            nextFitness = fitness(nextc)

            # Remember the best ever individual
            if nextFitness > bestEver[0]:
                print("New best individual!")#debug
                bestEver = [nextFitness, nextc]

            # Check the current solution's acceptance probability
            ap = acceptanceProbability(currentFitness, nextFitness, t)
            print("Probability of acceptance:", ap)#debug

            # If it gets accepted,
            if ap > random():
                print("-> Accepted!")#debug
                print("Moving ahead with new solution\n\n")#debug

                # Make the current solution the best one
                c = nextc
                currentFitness = nextFitness

                # i = tries + 1;

            # Mark that we tried a new one
            i += 1

            with open("es-selections.txt", "a") as outFile:
                outFile.write(str((currentFitness))+"\t")
                outFile.write(str(c)+"\n")

        # Once we've tried all the things there are to try
        # Let's cool down a bit and do it again
        t = next(temperatures)

    print("Done annealing.")#debug
    print("Last individual:", currentFitness, c)#debug
    print("Best individual:", bestEver[0], bestEver[1])#debug
    return c, currentFitness


def main():

    # Pregenerated chromosomes; comment out for a random initial chromosome
    # pregenChromosome = [11.57, 0.303, 205.748, 60.564, 9.214, 200.538, 126.272]
    # pregenChromosome = [14.79126, 0.06382, 199.42344, 58.38579, -4.45596, 209.58182, 98.84216]

    numGenerations = 2
    poprecordFileName = "fitness.txt"

    # Clear out the output file
    with open(poprecordFileName, "w") as initOutput:
        initOutput.write("")

    # (min, max, stdev)
    ranges = [(4,  24,  1), # min turn speed
              (3,  8,   2), # speed limit
              (100,200, 5), # firing range
              (30, 120, 1), # feeler sweep max offset
              (2,  10,  1), # feeler sweep resolution
              (20, 250, 5), # wall near limit
              (20, 250, 5)  # enemy close flag (for thrusting)
            ]

    # Randomly generate a chromosome
    chromosome = []
    print("Generating initial chromosome...")#debug

    for t in ranges:
        chromosome.append(randint(t[0], t[1]))

    print("Chromosome:", chromosome)#debug

    anneal(chromosome, ranges)

main()
