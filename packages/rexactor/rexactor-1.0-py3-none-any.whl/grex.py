from operators import *
import numpy as np

def NW(x, y, match = 1, mismatch = 1, gap = 1):
    nx = len(x)
    ny = len(y)
    digit_weight = 1
    # Optimal score at each possible pair of characters
    F = np.zeros((nx + 1, ny + 1))
    F[:,0] = np.linspace(0, -nx * gap, nx + 1)
    F[0,:] = np.linspace(0, -ny * gap, ny + 1)
    # Pointers to trace through an optimal alignment
    P = np.zeros((nx + 1, ny + 1))
    P[:,0] = 3
    P[0,:] = 4
    # Fill in the table for dynamic programming
    T = np.zeros(3)
    for i in range(nx):
        for j in range(ny):
            if x[i] == y[j]:
                T[0] = F[i,j] + match
            else:
                T[0] = F[i,j] - mismatch
            T[1] = F[i, j+1] - gap
            T[2] = F[i+1, j] - gap
            tmax = np.max(T)
            F[i+1, j+1] = tmax
            if T[0] == tmax:
                P[i+1, j+1] += 2
            if T[1] == tmax:
                P[i+1, j+1] += 3
            if T[2] == tmax:
                P[i+1, j+1] += 4

    # trace the optimal alignment
    i = nx
    j = ny
    rx = []
    ry = []
    while i > 0 or j > 0:
        if P[i,j] in [2,5,6,9]:
            rx.append(x[i-1])
            ry.append(y[j-1])
            i -= 1
            j -= 1
        elif P[i,j] in [3,5,7,9]:
            rx.append(x[i-1])
            ry.append(smallPsi)
            i -= 1
        elif P[i,j] in [4,6,7,9]:
            rx.append(smallPsi)
            ry.append(y[j-1])
            j -= 1

    # reverse the strings
    rx = ''.join(rx)[::-1]
    ry = ''.join(ry)[::-1]

    return rx, ry

# not digit
def exception1(dig):
    return not (is_not_char(dig) or is_not_ws(dig))

# not alpha
def exception2(alp):
    return not (is_not_ws(alp) or is_not_digit(alp))

# not whitespace
def exception3(ws):
    return not (is_not_char(ws) or is_not_digit(ws))

# replace matching character classes with Greek symbols
def encode(seqA, seqB):
    encoded_sequence = []
    for i in range(min(len(seqA), len(seqB))):
        typeA = char_type(seqA[i])
        typeB = char_type(seqB[i])

        if seqB[i] == smallPsi or seqA[i] == smallPsi: # NW gaps
            encoded_sequence.append(bigPhi)

        elif seqA[i] == bigPhi or seqB[i] == bigPhi:
            encoded_sequence.append(bigPhi)

        else:
            if typeA == typeB:
                if typeA == "alpha":
                    encoded_sequence.append(bigSigma)
                elif typeA == "digit":
                    encoded_sequence.append(bigPi)
                elif typeA == "space":
                    encoded_sequence.append(bigOmega)

            else:
                if (typeA != "alpha" and typeB != "alpha" and exception2(seqA[i]) and exception2(seqB[i])) or (typeA == "notChar" and typeB == "notChar"):
                    encoded_sequence.append(smallOmega) # not char
                elif (typeA != "digit" and typeB != "digit" and exception1(seqA[i]) and exception1(seqB[i])) or (typeA == "notDigit" and typeB == "notDigit"):
                    encoded_sequence.append(smallLambda) # not digit
                elif (typeA != "space" and typeB != "space" and exception3(seqA[i]) and exception3(seqB[i])) or (typeA == "notWS" and typeB == "notWS"):
                    encoded_sequence.append(smallSigma) # not whitespace
                else:
                    encoded_sequence.append(bigDelta)

    if (len(seqA) != len(seqB)):
        encoded_sequence += "".join([bigPhi * ((max(len(seqA), len(seqB))) - len(encoded_sequence))])
    return encoded_sequence

# replace symbols with regex classes
def replace(result):
    t = []
    f = []
    indexr = 0
    indext = 0
    indexf = 0

    while indexr < len(result):
        t.append(result[indexr])
        indexr += 1
        if indexr < len(result):
            f.append(t)
            t = [] # erase t
            indext = 0
            indexf += 1

    g = []
    i = 0
    while i < len(f):
        if indel(f[i][0]): #Phi
            phicount = 0
            while i < len(f) and indel(f[i][0]):
                phicount = phicount + 1
                i = i + 1
            g.append('.{0,' + str(phicount) + '}') # Single Phi
        elif mismatch(f[i][0]): # Delta
            if len(f[i]) > 1:
                g.append('.' + str(len(f[i])) + '}') # Multiple Delta
                appendlen = len(str(len(f[i])))
                a = 0
                while a < appendlen:
                    a += 1
            else:
                g.append('.') # Single Delta

        elif (f[i][0] == bigSigma): # alpha class type
            x = 0
            g.append(alphaChar(len(f[i])))
        elif (f[i][0] == bigPi): # digit class type
            g.append(digitChar(len(f[i])))
        elif(f[i][0] == bigOmega): # whitespace class type
            g.append(whitespaceChar(len(f[i])))
        elif(f[i][0] == smallOmega): # not alpha class type
            g.append(notAlphaChar(len(f[i])))
        elif(f[i][0] == smallLambda): # not digit class type
            g.append(notDigitChar(len(f[i])))
        elif(f[i][0] == smallSigma):
            g.append(notWhitespaceChar(len(f[i]))) # not whitespace class type
        elif(isSpecial(f[i][0])):
            x = 0
            spec = f[i][0]
            while x < len(f[i]):
                if spec != '.':
                    specstr = '\\' + spec
                else:
                    spectr = spec
                g.append(specstr)
                x += 1
        else:
            g.append(exactChar(f[i][0], len(f[i])))
        i += 1
    return g

# pairwise substring alignment
def align(passedList):
    result = passedList[0]
    for i in range(1, len(passedList)):
        continueAlignment = False
        for c in result:
            if c != bigPhi:
                continueAlignment = True
        if continueAlignment:
            a,b = NW(result, passedList[i])
            result = encode(a,b)
        else:
            result = [bigPhi * max(len(result), len(passedList[i]))]
    regex = replace(result)
    return regex
