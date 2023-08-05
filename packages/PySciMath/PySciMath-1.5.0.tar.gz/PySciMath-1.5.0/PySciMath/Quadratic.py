# PySciMath - Quadratic

''' This is the "Quadratic" sub-module. '''

# Imports
import Arithmetic

# Function 1 - Find Discriminant
def findDiscriminant(a, b, c):
    newA = float(a)
    newB = float(b)
    newC = float(c)

    return (b**2) - (4*a*c)

# Function 2 - Find Roots
def findRoots(a, b, c):
    newA = float(a)
    newB = float(b)
    newC = float(c)

    discriminant = findDiscriminant(a, b, c)

    alpha = (-newB + Arithmetic.squareRoot(discriminant)) / (2*newA)
    beta = (-newB - Arithmetic.squareRoot(discriminant)) / (2*newA)

    return (alpha, beta)