# PySciMath - Arithmetic

''' This is the "Arithmetic" sub-module. '''

# Imports
import cmath

# Constants
iota = "Iota, which is also referred to as 'i'. It's value is √-1."

# Functions - Simple Arithmetic Operations
def add(num1, num2): return num1 + num2
def subtract(num1, num2): return num1 - num2
def multiply(num1, num2): return num1 * num2
def divide(num1, num2): return num1 / num2
def modulus(num1, num2): return num1 % num2
def floorDivision(num1, num2): return num1 // num2
def power(base, exponent): return base ** exponent

# Functions - Complex Numbers
def modulusComplex(z): return abs(z)
def conjugateComplex(z): return z.conjugate()
def multiplicativeInverseComplex(z): return conjugateComplex(z) / power(modulusComplex(z), 2)
def polarComplex(z): return cmath.polar(z)

# Functions - Squares and Cubes
def square(number): return power(number, 2)
def cube(number): return power(number, 3)
def squareRoot(number): return number ** 0.5
def cubeRoot(number): return number ** (1/3)

# Functions - Odd and Even
def isOdd(number): return number % 2 == 1
def isEven(number): return number % 2 == 0

# Function 1 - Factorial
def factorial(number):
    f = 1

    for i in range(1, number + 1):
        f = f * i

    return f

# Function 2 - HCF
def hcf(num1, num2):
    hcf = 1

    for i in range(1, min(num1, num2)):
        if num1 % i == 0 and num2 % i == 0:
            hcf = i

    return hcf

# Function 3 - LCM
def lcm(num1, num2):
    if (num1 > num2):
        greater = num1
    else:
        greater = num2

    while True:
        if ((greater % num1 == 0) and (greater % num2 == 0)):
            lcm = greater
            break
        greater += 1

    return lcm

# Function 4 - Prime
def isPrime(number):
    isPrime = False

    if (number < 1):
        isPrime = False
    else:
        for i in range(2, int(number/2) + 1):
            if (number % i == 0):
                isPrime = False
                break
        else:
            isPrime = True

    return isPrime