from itertools import combinations
from collections import Counter

''' HELPERS '''

def sort_dictionary(dictInput: dict):
    # sorts dictionary by keys
    return {key: val for key, val in sorted(dictInput.items(), key = lambda ele: ele[0])}

def generate_no_sups(lk: dict):
    # returns keys of dictionary in a list
    return [itemSet for itemSet in lk] 

def filter_data(aprioriResult, minimumSupport):
    tempRes = {}
    for x in aprioriResult:
        miniTempRes = {}
        for y in aprioriResult[x]:
            if aprioriResult[x][y] >= minimumSupport:
                miniTempRes[y] = aprioriResult[x][y]
        
        tempRes[x] = miniTempRes
    
    return tempRes

def item_set_counter(aprioriResult):
    itemSetCount = {}
    for kItemSet in aprioriResult:
        itemSetCount[kItemSet] = len(aprioriResult[kItemSet])
    return itemSetCount

'''
APRIORI ALGORITHM & HELPERS
'''

def above_support(dictInput, minSupport):
    return {key: val for key, val in dictInput.items() if val >= minSupport}

def generate_k_candidate_set(prevLk):
    #input of prevLk is a dictionary of key/value pairs where each key is a sorted itemset in the form of tuple

    prevLkNoSups = generate_no_sups(prevLk)
    ck = {}

    upIdx = 0
    bottomIdx = 1

    while(1):

        if (bottomIdx == len(prevLkNoSups)):
            upIdx += 1
            bottomIdx = upIdx + 1
            continue

        if upIdx >= len(prevLkNoSups)-1 and bottomIdx >= len(prevLkNoSups)-1:
            break
        
        if prevLkNoSups[upIdx][0:-1] == prevLkNoSups[bottomIdx][0:-1]:
            ck[prevLkNoSups[upIdx] + (prevLkNoSups[bottomIdx][-1],)] = 0
            # print(upIdx, ' ' , bottomIdx)
        else:
            # print('----change----')
            upIdx += 1
            bottomIdx = upIdx + 1
            continue
        bottomIdx += 1
    return ck

def prune(ck, prevLk, k):
    prunedCk = {}
    for itemSet in ck:
        if all(subset in prevLk for subset in combinations(itemSet, k-1)):
            prunedCk[itemSet] = 0

    return prunedCk

def count_support(trans, ck, k):
    for transaction in trans:
        if len(transaction) >= k:
            for comb in combinations(transaction,k):
                if comb in ck:
                    ck[comb] = ck[comb] + 1
    return ck

def apriori(trans: list, minSupport: float):
    """ 
    
    @param trans: a list of transactions, each transaction is also a list 
    @param minSupport: minimum support for apriori algorithm
   
    @return: dictionary of frequent itemsets along with support
    
    """
    
    masterCandidates = {1:{}}

    c1 = Counter() 
    for x in trans:
        # gets the data of on one-itemset candidates
        c1.update(x)

    c1 = sort_dictionary(dict(c1)) 

    l1 = above_support(c1, minSupport) #get above support
    masterCandidates[1] = l1 #add 1-itemset to masterCandidate

    c2 = {}
    for comb in combinations(l1,2): #generate 2-itemset candidates
        c2[comb] = 0

    c2 = count_support(trans, c2, 2)

    l2 = above_support(c2, minSupport)

    lk = l2

    k = 3

    while(lk):
  
        masterCandidates[k-1] = lk #add k-itemset to masterCandidate
        
        ck = generate_k_candidate_set(lk)

        ck = prune(ck, lk, k)

        ck = count_support(trans, ck, k)

        lk = above_support(ck, minSupport)

        k = k+1
    
    return masterCandidates

''' 

The challenge was given a txt file where each line represents a transaction of transaction ids, 
report the number of frequent patterns, as well as the number of size-k frequent patterns for each size k 
with at least one frequent pattern, under each setting of minFreq

a trick for running the challenge above is instead of running the apriori function for each given minimum frequency, 
we run the apriori algorithm once with minimum frequency with the lowest value and filter accordingly with the other frequencies.


'''

with open('trans.txt') as f:
    lines = [line.replace('\t', ' ').strip() for line in f]

trans = [sorted(list(map(int, line.split()))) for line in lines]

minFreqs = [0.0005,0.0004,0.0003,0.0002,0.0001] # the given mininum frequencies
minFreqs.sort() 
minSupports = [x*len(trans) for x in minFreqs] # support = num of transactions * frequency
minSupports

ap1 = apriori(trans, minSupports[0]) #running apriori algorithm for minimum frequency of 0.0001

masterData = {}
masterData[minFreqs[0]] = ap1



for i,x in enumerate(minSupports[1:]):
    tempData = filter_data(ap1, x)
    masterData[minFreqs[i+1]] = tempData

for x in masterData:
    print(f'Minimum Frequency: {x}')
    print(f'-----------------------------')
    currentItemSetCount = item_set_counter(masterData[x])
    for y in currentItemSetCount:
        print(f'{y}-itemset: {currentItemSetCount[y]}')
    total = sum(currentItemSetCount.values())
    print(f'Total: {total}')
    print("")
    