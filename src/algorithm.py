"""File that implements the algorithm for the binary knapsack
problem.

All of the algorithms follow a depth-first approach in the search
for an optimal solution.

However, the implementation of the branch and bound algorithm is
such that once it finds a new lower bound (stored in the variable
bestValueSoFar), it unrolls the recursion tree, to try to prune the
branches from some place nearer to the root. This is expected to
increase efficiency.

It is not possible, though, to do the same with the backtracking
paradigm, since the only thing it considers to prune a branch is its
feasibility --- no upper bounds are taken into account.

"""

from numpy import logical_or
from warnings import warn

# Global variables, to reduce overhead of recursive calls

# These four are defined in the function "algorithm"
numWeights = None
maxWeight = None
vs = None
ws = None

# bestValueSoFar is the the variable used to store the current
# global optima, both for the backtracking and the branch-and-bound
# algorithms.
bestValueSoFar = None

# This variable is used in the branch-and-bound algorithm to unroll
# the recursive stack once a new optima is found.
foundBest = None

"""If this function is not run, some problems might happen, namely
when the python virtual machine is not turn off between calls to the
main function

"""
def resetGlobalVars():
    global numWeights, maxWeight, vs, ws
    global bestValueSoFar, foundBest
    numWeights = None
    maxWeight = None
    vs = None
    ws = None
    bestValueSoFar = 0
    foundBest = False

"""Auxiliary recursive function for the backtracking algorithm

@see backtracking

"""
def btRec(leftOverIndexes, cumValue, cumWeight):
    global vs, ws, maxWeight, bestValueSoFar

    if leftOverIndexes == []:
        return 0

    # Below we will branch with and without the first weight
    resWith = 0
    resWout = 0

    firstWeight = leftOverIndexes[0]

    # Incremented (with first weight) value and weight
    incValue = cumValue + vs.iloc[firstWeight]
    incWeight = cumWeight + ws.iloc[firstWeight]

    # Prune the branch by infeasibility
    if incWeight <= maxWeight:
        # Branch **with** the weight
        # Must pass the arguments incValue and incWeight, instead of
        # cumValue and cumWeight.
        resWith = incValue + btRec(leftOverIndexes[1:], incValue,
                                   incWeight)

        if resWith > bestValueSoFar:
            bestValueSoFar = resWith    

    # Branch without the weight (no need to check for infeasibility)
    resWout = cumValue + btRec(leftOverIndexes[1:], cumValue,
                               cumWeight)

    if resWout > bestValueSoFar:
        bestValueSoFar = resWout
    
    return max(resWith, resWout) - cumValue

""" Algorithm to resolve the knapsack problem by backtracking. It
simply passes the initial variables to the recursive function above,
which in turn takes care of the rest.

@see btRec

"""
def backtracking():
    btRec(leftOverIndexes=list(vs.index),
          cumValue=0,
          cumWeight=0)

    return bestValueSoFar

""" Fetches the best possible result if we proceed with the
leftOverIndexes.

@see bbRec

"""
def getBestUb(leftOverIndexes, curValue, curWeight):
    global maxWeight

    if leftOverIndexes == []:
        return curValue
    
    bestIdx = leftOverIndexes[0]
    
    bestValue = vs.iloc[bestIdx]
    bestWeight = ws.iloc[bestIdx]
    rogProfit = (bestValue / bestWeight) * (maxWeight - curWeight)
    
    return curValue + rogProfit
    

""" Auxiliary recursive function for the branch-and-bound algorithm.

@see branchAndBound

"""
def bbRec(leftOverIndexes, cumValue, cumWeight):
    global maxWeight, vs, ws, bestValueSoFar, foundBest

    if leftOverIndexes == []:
        return 0

    # Below we will branch with and without the first weight
    resWith = 0
    resWout = 0

    firstWeight = leftOverIndexes[0]
    # Incremented (with first weight) value and weight
    incValue = cumValue + vs.iloc[firstWeight]
    incWeight = cumWeight + ws.iloc[firstWeight]

    # Prune the branch by infeasibility
    if incWeight <= maxWeight:
        # Prune the branch by limit
        hipotheticalUb = getBestUb(leftOverIndexes[1:], incValue,
                                   incWeight)

        if hipotheticalUb > bestValueSoFar:
            # Branch with the weight
            resWith = cumValue + bbRec(leftOverIndexes[1:],
                                       incValue, incWeight)
            if resWith > bestValueSoFar:
                bestValueSoFar = resWith
                foundBest = True

    # Now let us try to branch without the first weight in the list
    # No need to prune by infeasibility
    # Prune the branch by limit
    hipotheticalUb = getBestUb(leftOverIndexes[1:], cumValue,
                               cumWeight)

    if hipotheticalUb > bestValueSoFar:
        # Branch without the weight
        resWout = cumValue + bbRec(leftOverIndexes[1:],
                                   cumValue, cumWeight)
        if resWout > bestValueSoFar:
            bestValueSoFar = resWout
            foundBest = True
    
    return max(resWith, resWout) - cumValue

"""Get the descending order of the weights according to the ratio
(var / wei). This way, when we are doing branch-and-bound, we can
always know that the most profitable node is the first node in the
index list passed to the function bbRec.

@see branchAndBound

"""
def getRatioIdx():
    return list((vs / ws).sort_values(ascending=False).index)
    
""" This is the branch and bound version to solve the problem. Note
that much of the work is left to the recursive bbRec. Here, we just
add a loop to improve efficiency by trying nodes closer to the root,
whenever the algorithm finds a new optima.

@see bbRec

"""
def branchAndBound():
    global foundBest

    bbInitialList = getRatioIdx()

    i = 0
    while i < len(bbInitialList):
        curIdx = bbInitialList[i]
        bbInitialList.pop(i)
        
        foundBest = True
        while foundBest:
            foundBest = False

            bbRec(leftOverIndexes=bbInitialList,
                  cumValue=vs.iloc[curIdx],
                  cumWeight=ws.iloc[curIdx])
        
        bbInitialList.insert(i, curIdx)
        
        i += 1
        
    return bestValueSoFar



"""Interfaces to communicate with the outside world.

"""
def dropVsWsZeros(df, vs, ws):
    droppedIndexes = df[logical_or(vs == 0, ws == 0)].index

    if len(droppedIndexes) != 0:
        warn("Zero entries (either values or weights) detected.")
        df.drop(droppedIndexes, inplace=True)
    
""" Receives data from the interface and calls correct algorithm.

@see interface.interface

"""
def algorithm(data, algName):

    resetGlobalVars()
    
    global numWeights, maxWeight, vs, ws, mutableVsIndex
    
    df, numWeights, maxWeight = data
    vs = df["vs"]
    ws = df["ws"]

    # Make sure to remove zero values and weights
    dropVsWsZeros(df, vs, ws)

    if algName == "backtracking":
        return backtracking()
    elif algName == "branchAndBound":
        return branchAndBound()
    else:
        raise AttributeError("The algorithm '" + algName +
                             "' is unknown.")
