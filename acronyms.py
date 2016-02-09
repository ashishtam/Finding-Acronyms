import numpy as np

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
    # c = np.zeros((m + 1, n + 1), dtype=np.int)
    c = [[0]* (n+1) for i in range(m+1)]

    # initialization of matrix b to trace the back pointer
    b = [[0]* (n+1) for i in range(m+1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # print i, j
            # print "Y:", Y[j-1]
            if (X[i-1] == Y[j-1]):
                c[i][j] = c[i - 1][j - 1] + 1
                # b[i][j] = (i-1,j-1)
                b[i][j] = 'D'
            elif (c[i-1][j]>= c[i][j-1]):
                c[i][j] = c[i - 1][j]
                # b[i][j] = (i-1,j)
                b[i][j] = 'U'
            else:
                c[i][j] = c[i][j - 1]
                # b[i][j] = (i,j-1)
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
    list = [0]*n

    for i,j in Stack:
        list[j-1] = i
    return list

import re

# Reading the text file in python
file = open('text.txt', 'r')
text = file.read()

#split the words from the text.
words = text.split()
# words = re.findall(r'\w+', text)

# Reading stop words from the file
fileStopwords = open('stopwords.txt', 'r')
stopwordsList = fileStopwords.read()
stopwords = stopwordsList.split()

print words

# input the acronym to be search from the user
print "Enter acronym to be searched: "
acronym = raw_input().upper()
# acronym = "DOE"
print acronym

# Finding the position of the word in the list.

# print words.index(acronym)
index = [i for i,s in enumerate(words) if acronym in s]
print index

if (index):
    indexAcronym = index[0]

# Find the pre-window
preWindowFirstIndex = indexAcronym - 2 * len(acronym)
print preWindowFirstIndex

if (preWindowFirstIndex < 0):
    preWindow = words[:indexAcronym]
else:
    preWindow = words[preWindowFirstIndex:indexAcronym]

print preWindow

#Separate hyphenated words in the list
preWindowJoin = ' '.join(preWindow)
preWindow = re.findall(r'\w+', preWindowJoin)
print "After join: ", preWindow

# Find the leaders of the pre window
leaders = [x[0].lower() for x in preWindow]
print leaders

types = []
for x in preWindow:
    flagStop = x.lower() in stopwords
    if (flagStop):
        types.append('s')
    else:
        types.append('w')

print types


#X and Y
X = acronym.lower()
Y = ''.join(leaders)

print X,Y
# build LCS matrix
c,b = buildLCSmatrix(X,Y)

print c
print b

m = len(X)
n = len(Y)
print c[m][n]
Vectors = parseLCSmatrix(b, 0, 0, m, n, c[m][n], [], [])

print Vectors

finalList = []
for i,x in enumerate(Vectors[0]):
    if (x!=0):
        finalList.append(preWindow[i])

print acronym, ' '.join(finalList)