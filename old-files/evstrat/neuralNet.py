# Jack Beal and Lydia Morneault
# COM-407 CI
# 2018-05-07 Final project
# Based on neuralnet.py by Jessy Quint and Rishma Mendhekar

from random import*
import math


def sigmoid(x):
    return (1/(1+math.exp(-1*x)))

def perceptron(thing, weights):

    summation = 0 # initialize sum
    counter = 0 # variable to assign correct weight to correct bit

    for digit in thing: # for each bit
        summation += (int(digit)*weights[counter]) # calculate weighted sum
        counter += 1
    summation += (-1 * weights[-1]) # subtract the threshold in order to shift the decision boundary

    output = sigmoid(summation) # keep output between 0 and 1
    return output

# perceptron for hidden layer to output neuron
# inputs into output neuron are float values that we do not want to round to integers
def perceptron2(thing, weights):

    summation = 0 # initialize sum
    counter = 0 # variable to assign correct weight to correct bit

    for digit in thing: # for each bit
        summation += digit*weights[counter] # calculate sum based on weights
        counter += 1
    summation += (-1 * weights[-1]) # subtract the threshold in order to shift the decision boundary

    output = sigmoid(summation)
    return output

def trainingPercepton(iterations):

    learningRate = 0.1 # Epsilon
    weightsA = [] # weights for each input for neuron A
    weightsB = [] #           ''           for neuron B
    weightsC = [] #           ''           for neuron C

    # Weights from hidden layer to output neuron and threshold
    weightFinal = [round(uniform(-0.48, 0.48), 2), round(uniform(-0.48, 0.48), 2), round(uniform(-0.48, 0.48), 2), round(uniform(-0.48, 0.48), 2)]

    # Assign random initial weights, with values between -r and +r where r = 2.4/# of inputs see p.179
    for w in range(4):
        weightsA.append(round(uniform(-0.48, 0.48), 2))
        weightsB.append(round(uniform(-0.48, 0.48), 2))
        weightsC.append(round(uniform(-0.48, 0.48), 2))
    #print(weightsA)
    #print(weightsB)

    trainingInput = [ ['000', 1],
                    ['025', 1],
                    ['050', 1],
                    ['075', 0.9],
                    ['100', 0.8],
                    ['125', 0.7],
                    ['150', 0.7],
                    ['175', 0.6],
                    ['200', 0.6],
                    ['225', 0.5],
                    ['250', 0.5],
                    ['275', 0.4],
                    ['300', 0.3],
                    ['325', 0.2],
                    ['350', 0.1],
                    ['375', 0],
                    ['400', 0],
                    ['425', 0],
                    ['450', 0],
                    ['500', 0]]

    for j in range(iterations): # Loop through the list, number of loops depends on user input
        outputList = [] # Print output list to see accuracy

        for train in trainingInput:
            outputA = perceptron(train[0],weightsA) # output for neuron A
            outputB = perceptron(train[0],weightsB) # output for neuron B
            outputC = perceptron(train[0],weightsC) # output for neuron C

            outputsABC = [outputA, outputB, outputC] # inputs for the final neuron
            finalOutput = perceptron2(outputsABC, weightFinal)

            # Error is calculated by subtracting the program output from the desired output
            error = train[1] - finalOutput

            # Calculate error gradients
            # error gradient for output layer based on formula
            errorGradient = finalOutput * (1-finalOutput) * error

            # Add the previous neuron's weight to (learning rate * input * error gradient)
            for i in range(len(weightFinal)-1):
                weightFinal[i] += (learningRate * outputsABC[i] * errorGradient)
            weightFinal[3] = weightFinal[3] + (learningRate * -1 * errorGradient) # for threshold

            # Error gradient for hidden layer
            # Don't have desired outputs for hidden layer, therefore cannot calculate error
            # Instead of error, use sumGradient = error gradient for output neuron * weight of the input
            sumGradientA = (errorGradient * weightFinal[0])
            sumGradientB = (errorGradient * weightFinal[1])
            sumGradientC = (errorGradient * weightFinal[2])

            hiddenGradientA = (outputA * (1-outputA) * sumGradientA)
            hiddenGradientB = (outputB * (1-outputB) * sumGradientB)
            hiddenGradientC = (outputC * (1-outputC) * sumGradientC)

            # Using error gradients, update the weights
            for i in range(len(weightsA)-1):
                weightsA[i] += (learningRate * int(train[0][i]) * hiddenGradientA)
                weightsB[i] += (learningRate * int(train[0][i]) * hiddenGradientB)
                weightsC[i] += (learningRate * int(train[0][i]) * hiddenGradientC)
            weightsA[3] += (learningRate * -1 * hiddenGradientA)
            weightsB[3] += (learningRate * -1 * hiddenGradientB)
            weightsC[3] += (learningRate * -1 * hiddenGradientC)

            outputList.append([])
            outputList[-1].append(train[0])
            outputList[-1].append(finalOutput)

    # for temp in outputList:
    #   print(temp[0], "->", temp[1])



