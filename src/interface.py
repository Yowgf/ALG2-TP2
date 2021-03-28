"""Interface between the outside world and the knapsack algorithm"""

from pandas import read_csv

from .algorithm import algorithm

def readTable(inFile):
    # The format is as 
    #
    # File name: kp_n_wmax
    #
    # n: number of available items to choose from
    #
    # wmax: knapsack capacity
    #
    # n wmax
    #
    # v1 w1
    # v2 w2
    # : :
    # vi wi
    # : :
    # vn wn
    #
    # vi: profit from item i
    #
    # wi: weight of item i
    inTable = read_csv(inFile, sep=" ")
    
    # Extract values
    inCols = inTable.columns
    numWeights = int(inCols[0])
    maxWeight  = int(inCols[1])
    
    # Rename terrible column names into something usable
    # vs stands for the 'values' column
    # ws stands for the 'weights' column
    inTable.rename(columns={inCols[0]: "vs", inCols[1]: "ws"},
                   inplace=True)

    return inTable, numWeights, maxWeight

def interface(inFile, algName):
    algData = readTable(inFile)

    return algorithm(algData, algName)
