# Jack Beal and Lydia Morneault
# COM-407 CI
# 2018-04-21
# Gen alg control script

from random import *
import subprocess
from Individual import *


def fitness(c):
    # Assess fitness of an individual chromosome, c
    # Returns an integer fitness value, hopefully
    p = subprocess.call(["python3", "genalg-agent.py", "-g", c])
    with open("fitness.txt", 'r') as inputFile:
        fitness = int(inputFile.readlines()[-1])
    return fitness

def selectRoulette(chromosomes, fitnesses):
    # Picks a chromosome from the list of chromosomes and its parallel list of fitnesses
    # Returns (chromosome, fitness)
    stop = uniform(0,sum(fitnesses))
    curr = 0
    for i in range(len(chromosomes)):
        curr += fitnesses[i]
        if curr > stop:
            return (chromosomes[i], fitnesses[i])


def main():

    fileMode = False # Flip this to initialize from a text file
    popFileName = "population.txt"
    lastGenerationFileName = "gaoutput.txt"

    # Clear out the output file
    with open(lastGenerationFileName, "w") as initOutput:
        initOutput.write("")

    # NB: fileMode expects format "<chromosome>\n" throughout entire file!
    #     Also that all chromosomes are same length as the first in file.

    lenChromosome = 47
    populationSize = 15
    probMutation = 0.007
    numGenerations = 50
    interval = 5 # Interval at which best individual is reported
    bestIndividualEver = (-1,-1,-1) # This gets used later


    # Initialize population from a file of chromosomes
    if fileMode == True:
        print("Executing in FILE MODE")#pretty

        chromFile = open(popFileName, "r")
        population = [l.strip() for l in chromFile.readlines()]
        chromFile.close()

        lenChromosome = len(population[0])
        populationSize = len(population)

    # Randomly generate a population of chromosomes
    else:
        print("Executing in RANDOM MODE")#pretty.

        population = []
        for i in range(populationSize):
            c = ""
            for j in range(lenChromosome):
                c += str(randint(0,1))
            population.append(c)


    # print(population)#debug

    # Do a genetic algorithm!
    for gen in range(numGenerations):

        nextPopulation = []
        fitnesses = []

        # Calculate fitnesses for all chromosomes
        for individual in population:
            fitnesses.append(fitness(individual))

            with open("masteroutput.txt", "a") as masteroutputFile:
                print(gen, individual, fitnesses[-1], file=masteroutputFile)

        sortedPop = [x for _, x in sorted(zip(fitnesses,population), key=lambda pair: pair[0], reverse=True)]

        if fitness(sortedPop[0]) >= bestIndividualEver[1]:
            bestIndividualEver = (sortedPop[0], fitness(sortedPop[0]), gen)

        # Update the user
        if gen % interval == 0 or gen == numGenerations:
            print("Gen", gen, "\tbest:", sortedPop[0], "\tf =", fitness(sortedPop[0]), "\tavg =", (sum(fitnesses)/len(fitnesses)))#pretty


        # We're done, time to save the population from extinction
        outfile = open(lastGenerationFileName, "a")
        for i in range(len(population)):
            print(gen, population[i], fitnesses[i], file=outfile)
        outfile.close()

        # Reproduce
        while len(nextPopulation) < len(population):
            # Select a pair of chromosomes for reproduction
            p1 = selectRoulette(population, fitnesses)[0]
            p2 = selectRoulette(population, fitnesses)[0]

            # Crossover
            crossPoint = randint(0, lenChromosome)
            c1 = p1[:crossPoint]+p2[crossPoint:]
            c2 = p2[:crossPoint]+p1[crossPoint:]

            # Mutation
            for j in range(lenChromosome):
                # This part is ugly, watch out
                if random() < probMutation:
                    if j == lenChromosome:
                        c1 = c1[:j] + str(-int(c1[j])+1)
                    else:
                        c1 = c1[:j] + str(-int(c1[j])+1) + c1[j+1:]
                if random() < probMutation:
                    if j == lenChromosome:
                        c2 = c2[:j] + str(-int(c2[j])+1)
                    else:
                        c2 = c2[:j] + str(-int(c2[j])+1) + c2[j+1:]

            # Place offspring into next population
            nextPopulation.append(c1)
            nextPopulation.append(c2)

        population = nextPopulation

    print("Best individual ever was:")#pretty
    print("Gen", bestIndividualEver[2], "\tchrm:", bestIndividualEver[0], "\tf =", bestIndividualEver[1])#pretty

    print("Last generation saved to", lastGenerationFileName, "\n\n")#pretty

main()
