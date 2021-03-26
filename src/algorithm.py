"""File that implements the algorithm"""

# Global variables, to reduce overhead of recursive calls
# They are defined in the function "algorithm"
numWeights = None
maxWeight = None
vs = None
ws = None

"""
Auxiliary recursive function for the backtracking algorithm
"""
def btRec(saccus, saccusWeight):
    branchList = []
    # Branch in each of the weights
    for i in range(numWeights):
        # Proposed addition of the weight at position i
        rogWeight = saccusWeight + ws[i]
        
        # This is the only place where the branch is pruned. When we
        # see that if we put the weight it'll not work
        if rogWeight <= maxWeight:
            rogatum = saccus + [vs[i]]
            branchList.append(btRec(rogatum, rogWeight))

    if branchList == []: # This means we are at a leaf
        return sum(saccus)
    else:
        return max(branchList)

"""
Algorithm to resolve the knapsack problem by a branch and bound
approach.

First, will be implemented simply a backtracking version, that
prunes the branches as we find it is impossible to continue, but
applies no further heuristics.

Then, I must discover new conditions under which we might prove that
continuing branching will be unfruitful. These shall be considered
in the branch and bound version.
"""
def backtracking():
    return btRec([], 0)

"""
This is the branch and bound version to solve the problem.
"""    
def branchAndBound():
    pass
    
"""
Receives data from the interface and calls correct algorithm
"""
def algorithm(data, algName):
    # numWeights, maxWeight, vs, and ws are all global vars
    global numWeights, maxWeight, vs, ws
    
    df, numWeights, maxWeight = data
    
    vs = df["vs"]
    ws = df["ws"]

    if algName == "backtracking":
        return backtracking()
    elif algName == "branchAndBound":
        return branchAndBound()
