# @author Ashish Tamrakar
# @Date 2016-02-08
# Program to find the definition of acronyms from the text.
# Python v2.7.10

import numpy as np
import sys
import re
def buildLCSmatrix(X, Y):
    """
    Returns the matrix with c and back pointer b obtained from dynamic programming of Longest Common Sequence (LCS)
    :param X: string
    :param Y: string
    :return: c,b matrix,matrix
    """
    m = len(X)
    n = len(Y)

    # initialization of matrix C to count the LCS
    c = [[0]* (n+1) for i in range(m+1)]

    # initialization of matrix b to trace the back pointer
    b = [[0]* (n+1) for i in range(m+1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if (X[i-1] == Y[j-1]):
                c[i][j] = c[i - 1][j - 1] + 1
                b[i][j] = 'D'
            elif (c[i-1][j]>= c[i][j-1]):
                c[i][j] = c[i - 1][j]
                b[i][j] = 'U'
            else:
                c[i][j] = c[i][j - 1]
                b[i][j] = 'L'
    return c,b

def parseLCSmatrix(b, start_i, start_j, m, n, lcs_length, Stack, Vectorlist):
    """
    Returns the vector list containing the list of LCS on the corresponding list
    """
    for i in range(start_i, m+1):
        for j in range(start_j, n+1):
            if (b[i][j] == "D"):
                Stack.append((i,j))
                if lcs_length == 1:
                    v = buildVector(Stack, n)
                    Vectorlist.append(v)
                else:
                    parseLCSmatrix(b, i+1, j+1, m, n, lcs_length-1, Stack, Vectorlist)
                Stack.pop()
    return Vectorlist

def buildVector(Stack, n):
    """
    Building the vector list from the Stack.
    """
    list = [0]*n
    for i,j in Stack:
        list[j-1] = i
    return list

def getFirstAndLastIndex(VectorList):
    """
    Returns the first and last index of the possible acronym in Vector list
    """
    first = next((i for i, x in enumerate(VectorList) if x), None)
    reverseV = VectorList[::-1]
    last = (len(VectorList)-1) - next((i for i, x in enumerate(reverseV) if x), None)
    return first, last

def vectorValues(V, types):
    """
    Calculation of the size, distance, stopcount and misses in the vector.
    """
    dict = {}
    i = 1
    first, last = getFirstAndLastIndex(V)
    dict['size'] = last - first + 1
    dict['distance'] = (len(V)-1) - last
    dict['stopcount'] = 0
    dict['misses'] = 0
    for i in range(first, last+1):
        if (V[i] > 0 and types[i] == 's'):
            dict['stopcount'] = dict['stopcount'] + 1
        elif (V[i] == 0 and types[i] != 's' and types[i] != 'h'):
            dict['misses'] = dict['misses'] + 1
    return dict

def compareVectors(A, B, types):
    """
    Comparing two Vectors based on the number of misses, stopcount, distance and size.
    """
    resultA = vectorValues(A, types)
    resultB = vectorValues(B, types)

    if (resultA['misses'] > resultB['misses']):
        return B
    elif (resultA['misses'] < resultB['misses']):
        return A
    if (resultA['stopcount'] > resultB['stopcount']):
        return B
    elif (resultA['stopcount'] < resultB['stopcount']):
        return A
    if (resultA['distance'] > resultB['distance']):
        return B
    elif (resultA['distance'] < resultB['distance']):
        return A
    if (resultA['size'] > resultB['size']):
        return B
    elif (resultA['size'] < resultB['size']):
        return A

def findAcronym(words, acronym, stopwords):
    """
    Finding the acronym definition using the list of paragraph words and stopwords for the given acronyms
    :param words:
    :param acronym:
    :param stopwords:
    :return:
    """
    # Finding the position of the word in the list.
    index = [i for i,s in enumerate(words) if acronym in s]

    if (index):
        indexAcronym = index[0]
    else:
        return "(Acronym not found in the text.)"

    # Find the pre-window
    preWindowFirstIndex = indexAcronym - 2 * len(acronym)

    if (preWindowFirstIndex < 0):
        preWindow = words[:indexAcronym]
    else:
        preWindow = words[preWindowFirstIndex:indexAcronym]

    #Separate hyphenated words in the list
    preWindowJoin = ' '.join(preWindow)
    preWindowS = re.findall(r'\w+', preWindowJoin)
    hyphenatedWords = re.findall(r'\w+-\w+[-\w+]*',preWindowJoin)

    # Find the leaders of the pre window
    leaders = [x[0].lower() for x in preWindowS]

    types = []
    for x in preWindowS:
        flagStop = x.lower() in stopwords
        if (flagStop):
            types.append('s')
        else:
            flagHyphen = 0
            for word in hyphenatedWords:
                listHyphen = ''.join(word).split('-')
                indexHyphen = None
                if (x in listHyphen):
                    flagHyphen = 1
                    indexHyphen = listHyphen.index(x)
                    if (indexHyphen == 0):
                        types.append('H')
                    else:
                        types.append('h')
            if (not flagHyphen):
                types.append('w')

    #X and Y
    X = acronym.lower()
    Y = ''.join(leaders)

    # build LCS matrix
    c,b = buildLCSmatrix(X,Y)

    m = len(X)
    n = len(Y)
    Vectors = parseLCSmatrix(b, 0, 0, m, n, c[m][n], [], [])

    if (not Vectors):
        return  "(Acronym definition not found in the text.)"

    # Choosing of vectors from the multiple vectors based on number of misses, stopcount, distance and size
    choiceVector = Vectors[0]
    for i in range(1, len(Vectors)):
        choiceVector = compareVectors(choiceVector, Vectors[i], types)

    finalList = []
    firstIndex, lastIndex = getFirstAndLastIndex(choiceVector)

    countHyphen = 0
    textHyphen = ""
    for i,x in enumerate(choiceVector):
        if (i>=firstIndex and i<=lastIndex):
            if (types[i] == 'H' or types[i] == 'h'):
                textHyphen += preWindowS[i]
                if (i+1 < len(types) and types[i+1] == 'h'):
                    countHyphen += 1
                    textHyphen += '-'
                    continue

            #Reset the hyphen parameters
            if (countHyphen != 0):
                textJoin = textHyphen
                textHyphen = ""
                countHyphen = 0
            else:
                textJoin = preWindowS[i]
            finalList.append(textJoin)

    return ' '.join(finalList)

def main():
    # Reading the text file in python
    file = open('text3.txt', 'r')
    text = file.read()
    print text

    #split the words from the text.
    words = text.split()

    # Reading stop words from the file
    fileStopwords = open('stopwords.txt', 'r')
    stopwordsList = fileStopwords.read()
    stopwords = stopwordsList.split()

    #acronymLis
    acronymList = [x for x in words if x.isupper() and len(x) > 1]
    acronymLists= re.findall(r'\w+', ' '.join(acronymList))

    print "Acronyms and its defintions"
    for acronym in acronymLists:
        print acronym, ":", findAcronym(words, acronym, stopwords)

main()