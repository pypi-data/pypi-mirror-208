"""
pymathematics
=============

Provides
  1. fast and accurate calculations
  2. work with vectors, matrices and sets
  3. statistics, basic mathematics calculation

  >>> from pymathematics import *
  >>> about.version
  ... 2023.5.13.1
  >>> about.homepage
  ... "https://github.com/Sahil-Rajwar-2004/pymathematics"
  >>> sqrt(4)
  ... 2.0
  >>> constants.inf
  ... inf
  >>> constants.pi
  ... 3.1415926535897932384626433832795
  >>> constants.e
  ... 2.7182818284590452353602874713527
  >>> mean([1,2,3,4,5])
  ... 5.5
"""

import sympy
from .info import (
    author,version,homepage
)

class about:
    author = author
    version = version
    homepage = homepage

class constants:
    pi = 3.1415926535897932384626433832795
    e = 2.7182818284590452353602874713527
    inf = float("inf")
    nan = float("nan")

class absolute_zero_temperature:
    kelvin = 0
    celsius = -273.15
    fahrenheit = -459.67

class temperature:
    def c2k(celsius):
        if celsius < absolute_zero_temperature.celsius:
            raise ValueError("below absolute zero temperature doesn't exist")
        return celsius+273.15

    def c2f(celsius):
        if celsius < absolute_zero_temperature.celsius:
            raise ValueError("below absolute zero temperature doesn't exist")
        return celsius*1.8+32

    def k2c(kelvin):
        if kelvin < absolute_zero_temperature.kelvin:
            raise ValueError("below absolute zero temperature doesn't exist")
        return kelvin-273.15

    def k2f(kelvin):
        if kelvin < absolute_zero_temperature.kelvin:
            raise ValueError("below absolute zero temperature doesn't exist")
        return temperature.k2c(kelvin)*1.8+32

    def f2c(fahrenheit):
        if fahrenheit < absolute_zero_temperature.fahrenheit:
            raise ValueError("below absolute zero temperature doesn't exist")
        return (fahrenheit-32)*0.5556

    def f2k(fahrenheit):
        if fahrenheit < absolute_zero_temperature.fahrenheit:
            raise ValueError("below absolute zero temperature doesn't exist")
        return temperature.f2c(fahrenheit)+273.15

class vector:
    def cross_product(vector1:list,vector2:list) -> int|float:
        if len(vector1) != 3 or len(vector2) != 3:
            raise ValueError("vector should have 3 directions")
        return [vector1[1]*vector2[2]-vector2[1]*vector1[2],-(vector1[0]*vector2[2]-vector2[0]*vector1[2]),vector1[0]*vector2[1]-vector2[0]*vector1[1]]

    def dot_product(vector1:list,vector2:list) -> int|float:
        if len(vector1) != 3 or len(vector2) != 3:
            raise ValueError("vector should have 3 directions")
        return vector1[0]*vector2[0]+vector1[1]*vector2[1]+vector1[2]*vector2[2]

    def magnitude(vector) -> int|float:
        if len(vector) != 3:
            raise ValueError("vector should have 3 directions")
        return sqrt(vector[0]**2+vector[1]**2+vector[2]**2)

    def projection(vector1:list,vector2:list) -> int|float:
        """
        `projection of vector1 to vector2`
        """
        if len(vector1) != 3 or len(vector2) != 3:
            raise ValueError("vector should have 3 directions")
        return vector.dot_product(vector1,vector2)/vector.magnitude(vector2)

    def angle_of_projection(vector1:list,vector2:list) -> float:
        return f"arccos({vector.dot_product(vector1,vector2)}/{(vector.magnitude(vector1)*vector.magnitude(vector2))})"

class matrix:
    def ismatrix(matrix_) -> bool:
        if not isinstance(matrix_, list):
            return False
        if not all(isinstance(row, list) for row in matrix_):
            return False
        row_lengths = [len(row) for row in matrix_]
        if not all(length == row_lengths[0] for length in row_lengths):
            return False
        return True

    def ifsquare(matrix_) -> bool:
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        if len(matrix_) == len(matrix_[0]):
            return True
        return False
    
    def shape(matrix_):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        return len(matrix_),len(matrix_[0])
    
    def size(matrix_):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        return len(matrix_)*len(matrix_[0])

    def determinant(matrix_):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        if not matrix.ifsquare(matrix_):
            raise ValueError("determinant of a matrix is only defined for square matrices")
        if len(matrix_) == 1:
            return matrix_[0][0]
        elif len(matrix_) == 2:
            return matrix_[0][0]*matrix_[1][1]-matrix_[0][1]*matrix_[1][0]
        det = 0
        for x in range(len(matrix_)):
            minor = []
            for y in range(1,len(matrix_)):
                row = []
                for z in range(len(matrix_)):
                    if z != x:
                        row.append(matrix_[y][z])
                minor.append(row)
            det += (-1)**x*matrix_[0][x]*matrix.determinant(minor)
        return det
    
    def inverse(matrix_):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        if not matrix.ifsquare(matrix_):
            raise ValueError("inverse of a matrix is only defined for square matrices")
        identity = [[0 if x != y else 1 for y in range(len(matrix_))] for x in range(len(matrix_))]
        for x in range(len(matrix_)):
            pivot = matrix_[x][x]
            for y in range(len(matrix_)):
                matrix_[x][y] /= pivot
                identity[x][y] /= pivot
            for y in range(len(matrix_)):
                if x != y:
                    factor = matrix_[y][x]
                    for k in range(len(matrix_)):
                        matrix_[y][k] -= factor * matrix_[x][k]
                        identity[y][k] -= factor * identity[x][k]
        return identity
    
    def cofactor(matrix_,row,col):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        return [row[:col] + row[col+1:] for row in (matrix_[:row] + matrix_[row+1:])]

    def adjoint(matrix_):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        adj = []
        for i in range(len(matrix_)):
            adjRow = []
            for j in range(len(matrix_)):
                sign = (-1)**(i+j)
                cofactor = matrix.determinant(matrix.cofactor(matrix_,i,j))
                adjRow.append(sign*cofactor)
            adj.append(adjRow)
        return adj

    def trace(matrix_) -> int|float:
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        if not matrix.ifsquare(matrix_):
            raise ValueError("matrix should have same number of rows and cols")
        trace = 0
        for x in range(len(matrix_)):
            trace += matrix_[x][x]
        return trace

    def diagonal_sum(matrix_) -> int|float:
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        if not matrix.ifsquare(matrix_):
            raise ValueError("matrix should have same number of rows and cols")
        total = 0
        for x in range(len(matrix_)):
            total += matrix_[x][x]
            total += matrix_[len(matrix_)-x-1][x]
        if len(matrix_)%2 != 0:
            total -= matrix_[int(len(matrix_)/2)][int(len(matrix_)/2)]
        return total

    def transpose(matrix_):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        rows = len(matrix_)
        cols = len(matrix_[0])
        res = [[0 for y in range(rows)]for x in range(cols)]
        for x in range(rows):
            for y in range(cols):
                res[y][x] = matrix_[x][y]   
        return res
    
    def product(matrix1,matrix2):
        if not matrix.ismatrix(matrix1) or not matrix.ismatrix(matrix2):
            raise ValueError("input should be a matrix")
        rows1 = len(matrix1)
        cols1 = len(matrix1[0])
        rows2 = len(matrix2)
        cols2 = len(matrix2[0])
        if cols1 != rows2:
            raise ValueError("number of columns of a first matrix should be equal to the rows of the second matrix")
        result = [[0 for y in range(cols2)] for x in range(rows1)]
        for x in range(rows1):
            for y in range(cols2):
                dot_product = 0
                for z in range(cols1):
                    dot_product += matrix1[x][z]*matrix2[z][y]
                result[x][y] = dot_product
        return result

    def multiply(matrix_,const):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        for rows in matrix_:
            for x in range(len(rows)):
                rows[x] = rows[x]*const
        return matrix_

    def reciprocal(matrix_):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        for rows in matrix_:
            for x in range(len(rows)):
                rows[x] = 1/rows[x]
        return matrix_

    def remove_column(matrix_,column):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        for rows in matrix_:
            rows.remove(rows[column])
        return matrix_
    
    def remove_row(matrix_,row):
        if not matrix.ismatrix(matrix_):
            raise ValueError("input should be a matrix")
        matrix_.remove(matrix_[row])
        return matrix_

class sets:
    def toset(A:list) -> list:
        new_set = []
        for x in A:
            if x not in new_set:
                new_set.append(x)
        return new_set

    def union(A:list,B:list) -> list:
        A = sets.toset(A)
        B = sets.toset(B)
        for x in B:
            if x not in A:
                A.append(x)
        return quick_sort(A)

    def intersect(A:list,B:list) -> list:
        res = []
        A = sets.toset(A)
        B = sets.toset(B)
        for i in B:
            if i in A:
                res.append(i)
        if len(res) == 0:
            return None
        return quick_sort(res)

    def subset(A:list,B:list) -> bool:
        A = sets.toset(A)
        B = sets.toset(B)
        for i in A:
            if i not in B:
                return False
        return True

    def belongsto(A:list,number:int,at:bool = False) -> (int|bool):
        A = sets.toset(A)
        if number in A:
            if not at:
                return True
            else:
                return A.index(number)
        return False

    def multiply(A:list,B:list) -> list:
        A = sets.toset(A)
        B = sets.toset(B)
        res = []
        for i in A:
            for j in B:
                res.append([i,j])
        return res
    
class area:
    def rectangle(length,breadth) -> int|float:
        return length*breadth
    
    def square(side) -> int|float:
        return side**2
    
    def trapezoid(a,b,height) -> int|float:
        return (a+b)*height/2
    
    def parallelogram(breadth,height) -> int|float:
        return breadth*height
    
    def triangle(base,height) -> int|float:
        return 0.5*base*height
    
    def circle(radius) -> int|float:
        return constants.pi*radius**2
    
    def semi_circle(radius) -> int|float:
        return 0.5*constants.pi*radius**2
    
    def ellipse(minor_axis,major_axis) -> int|float:
        return constants.pi*minor_axis*major_axis

    def equilateral_triangle(side) -> int|float:
        return sqrt(3)/4*side**2
    
    def sector(angle,radius) -> int|float:
        return angle/360*constants.pi*radius**2
    
    def segment(angle,radius) -> int|float:
        return area.sector(angle,radius) - area.triangle(radius,radius)
    
    def annulus(Radius,radius) -> int|float:
        if radius > Radius:
            return constants.pi*(radius-Radius)
        return constants.pi*(Radius-radius)
    
    def regular_hexagon(side) -> int|float:
        return 3*sqrt(3)/2*side**2
    
    def regular_octagon(side) -> int|float:
        return 2*(1+sqrt(2))*side**2
    
    def sector(angle,radius) -> int|float:
        return angle/360*constants.pi*radius**2
    
    def segment(angle,radius) -> int|float:
        return 0.5*radius**2*(angle-sin(angle))
    
class volume:
    def cuboid(length,breadth,height) -> int|float:
        return length*breadth*height
    
    def cube(side) -> int|float:
        return side**3
    
    def sphere(radius) -> int|float:
        return (4/3)*constants.pi*radius**3
    
    def hemisphere(radius) -> int|float:
        return (2/3)*constants.pi*radius**3
    
    def right_circular_cone(radius,height) -> int|float:
        return (1/3)*constants.pi*radius**2*height
    
    def right_circular_cylinder(radius,height) -> int|float:
        return constants.pi*radius**2*height
    
    def rhombus(d1,d2) -> int|float:
        return 0.5*d1*d2
    
class perimeter:
    def rectangle(length,breadth) -> int|float:
        return 2*(length+breadth)
    
    def square(side) -> int|float:
        return 4*side
    
    def circumference(radius) -> int|float:
        return 2*constants.pi*radius
    
    def semi_circle(radius) -> int|float:
        return constants.pi*radius
    
    def rhombus(side) -> int|float:
        return 4*side
    
class calculus:
    def integral(eqn:str,wrt:str = "x",limits:list = [None,None]):
        if len(limits) != 2:
            raise ValueError(f"size of the limits should be 2, not {len(limits)}")
        expr = sympy.sympify(eqn)
        return sympy.integrate(expr,(wrt,limits[0],limits[1]))
    
    def derivative(eqn:str,wrt:str = "x",point:int|float = None):
        expr = sympy.sympify(eqn)
        answer = sympy.diff(expr,wrt)
        if point == None:
            return answer
        return float(answer.evalf(subs = {wrt:point}))

def factorial(number: int) -> int:
    if number == 0:
        return 1
    elif number < 0:
        raise ValueError("number can't be negative!")
    return number*factorial(number-1)

def fibonacci_sequence(number: int) -> list:
    seq = [0, 1]
    if number <= 0:
        raise ValueError("number can't be negative!")
    elif number == 1:
        return seq[0]
    elif number == 2:
        return seq[1]
    else:
        for i in range(2,number):
            next_int = seq[i-1]+seq[i-2]
            seq.append(next_int)
    return seq

def reciprocal(number:int|float) -> int|float:
    return 1/number

def accuracy(actual:list,predicted:list,tolerance:float = 0.01) -> list:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted aren't the same")
    score = 0
    for x in range(len(actual)):
        if (actual[x] - predicted[x]) <= tolerance:
            score += 1
    return score/len(actual)

def exp(number:int) -> float:
    return summation([(number**n)/factorial(n) for n in range(0,100)])

def absolute(number:int|float) -> int|float:
    if number < 0:
        return -1*number
    return number

def floor(number:int|float) -> int:
    if number == int(number):
        return int(number)
    if number < 0:
        return int(number)-1
    return int(number)

def ceil(number:int|float) -> int:
    if number == int(number):
        return int(number)
    if number < 0:
        return int(number)-1
    return int(number)+1

def sqrt(number:int|float) -> int:
    if number < 0:
        return "undefined"
    elif number == 0:
        return 0
    flag = number/2
    while absolute(flag*flag - number) > 0.00001:
        flag = (flag + number/flag)/2
    return flag

def cbrt(number:int|float) -> float:
    flag = number/3
    while absolute(flag**3 - number) > 0.0001:
        flag = (2*flag+number/flag**2)/3
    return flag

def quadratic_roots(coefficients:list) -> list:
    if len(coefficients) != 3:
        raise ValueError("there should be only 3 coefficients!")
    D = coefficients[0]**2-4*coefficients[0]*coefficients[2]
    if D < 0:
        x1 = f"{-coefficients[1]} + {sqrt(absolute(D))}i"
        x2 = f"{-coefficients[1]} - {sqrt(absolute(D))}i"
        return [x1,x2]
    x1 = -coefficients[1]+sqrt(D)
    x2 = -coefficients[1]-sqrt(D)
    return [x1,x2]

def log(number:int|float) -> float:
    """
    `log(number) to the base 10`
    """
    if number <= 0:
        raise ValueError("domain error")
    else:
        n = 0
        while number >= 10:
            number /= 10
            n += 1
        if number == 1:
            return n
        else:
            left,right = 0,1
            while number < 1:
                left -= 1
                right -= 1
                number *= 10
            for _ in range(100):
                mid = (left+right)/2
                if 10**mid < number:
                    left = mid
                else:
                    right = mid
            return n+left

def ln(number:int|float) -> int|float:
    """
    `log(number) to the base e`
    """
    if number <= 0:
        raise ValueError("domain error")
    return 2.303*log(number)

def logn(number:int|float,base:int|float = constants.e) -> int|float:
    """
    `log(number) to the base n(user defined)`
    """
    if number <= 0 or base <= 0 or base == 1:
        raise ValueError("domain error")
    return 2.303*log(number)/(2.303*log(base))

def summation(array:list) -> list:
    sigma = 0
    for x in array:
        sigma += x
    return sigma

def product(array:list) -> list:
    result = 1
    for x in array:
        result *= x
    return result

def sin(theta:int|float) -> float:
    theta %= 2*constants.pi
    if theta > constants.pi:
        theta -= 2*constants.pi
    sinx = 0
    term = theta
    i = 1
    while absolute(term) > 1e-10:
        sinx += term
        term *= -1*theta**2/((2*i)*(2*i+1))
        i += 1
    return round(sinx,5)

def cos(theta:int|float) -> int:
    theta %= 2*constants.pi
    if theta > constants.pi:
        theta -= 2*constants.pi
    cosx = 1
    term = 1
    i = 1
    while absolute(term) > 1e-10:
        term *= -1*theta**2/((2*i-1)*2*i)
        cosx += term
        i += 1
    return round(cosx,5)

def tan(theta:int|float) -> float:
    if cos(theta) == 0:
        raise ValueError(f"tan({theta}) isn't defined at rad({theta})")
    return sin(theta)/cos(theta)

def cot(theta:int|float) -> float:
    if sin(theta) == 0:
        raise ValueError(f"cot({theta}) isn't defined at rad({theta})")
    return cos(theta)/sin(theta)

def cosec(theta:int|float) -> float:
    if sin(theta) == 0:
        raise ValueError(f"cosec({theta}) isn't defined at rad({theta})")
    return 1/sin(theta)

def sec(theta:int|float) -> float:
    if cos(theta) == 0:
        raise ValueError(f"sec({theta}) isn't defined at rad({theta})")
    return 1/cos(theta)

def arcsin(value:int|float) -> float:
    if value < -1 or value > 1:
        raise ValueError("domain error")
    term = 0
    for n in range(0,100):
        term += factorial(2*n)/(factorial(n)**2*4**n*(2*n+1))*value**(2*n+1)
    return term

def arccos(value:int|float) -> float:
    if value < -1 or value > 1:
        raise ValueError("domain error")
    return constants.pi/2-arcsin(value)

def mean(array:list) -> int|float:
    return sum(array)/len(array)

def median(array:list) -> list:
    sorted_array = quick_sort(array)
    if len(sorted_array)%2 == 0:
        mid1 = int(len(sorted_array)/2)
        mid2 = mid1 - 1
        return mean([mid1,mid2])
    else:
        mid = int(len(sorted_array)/2)
        return sorted_array[mid]

def standard_deviation(array:list,kind:str = "population") -> list:
    if kind == "sample":
        d = len(array)-1
    elif kind == "population":
        d = len(array)
    else:
        raise ValueError(f"invalid input {kind}! input should be whether 'population' or 'sample'")
    return sqrt(summation((x - mean(array))**2 for x in array)/(d))

def variance(array:list,kind:str = "population") -> int|float:
    if kind == "sample":
        d = len(array)-1
    elif kind == "population":
        d = len(array)
    else:
        raise ValueError(f"invalid input {kind}! input should be whether 'population' or 'sample'")
    return summation((x - mean(array))**2 for x in array)/d

def skewness(array:list) -> float:
    if len(array) == 0:
        raise ValueError("length of an array shouldn't be 0")
    return summation((x - mean(array))**3 for x in array)/(len(array)*standard_deviation(array,"population")**3)

def kurtosis(array:list) -> float:
    if len(array) == 0:
        raise ValueError("length of an array shouldn't be 0")
    moment = summation((x - mean(array))**4 for x in array)/len(array)
    return (moment/variance(array)**2)-3

def mode(array:list) -> int|float:
    freq = {}
    for each in array:
        if each in freq:
            freq[each] += 1
        else:
            freq[each] = 1
    answer = None
    max_freq = 0
    for each,occurence in freq.items():
        if occurence > max_freq:
            answer = each
            max_freq = occurence
    return answer

def geometric_mean(array:list) -> int|float:
    return product(array)**(1/len(array))

def harmonic_mean(array:list) -> int|float:
    t = 0
    for x in array:
        if x == 0:
            raise ZeroDivisionError("can't divisible by zero!")
        t += 1/x
    return len(array)/t

def square_sum(array:list) -> int|float:
    return summation(x**2 for x in array)

def permutation(n:int,r:int) -> int|float:
    return factorial(n)/factorial(n-r)

def combination(n:int,r:int) -> int|float:
    return factorial(n)/(factorial(r)*factorial(n-r))

def sum_array(array1:list,array2:list) -> list:
    if len(array1) == len(array2):
        return summation([array1[x]+array2[x] for x in range(array1)])
    raise ValueError(f"length of array1 and array2 aren't equal {len(array1)} != {array2}")

def zscore(array:list,number:int) -> int|float:
    return (number-mean(array))*standard_deviation(array)

def euclidean_distance(array1:list,array2:list) -> float:
    if len(array1) < 3 or len(array2) < 3:
        raise ValueError("arrays must have the same length and have atleast 3 coordinates both x and y")
    return sqrt(summation([(array1[x] - array2[x])**2 for x in range(len(array1))]))

def manhattan_distance(array1:list,array2:list) -> float:
    if len(array1) < len(array2) < 3:
        raise ValueError("arrays must have the same length and have atleast 3 coordinates both x and y")
    return summation([absolute(array1[x] - array2[x]) for x in range(len(array1))])

def camberra_distance(array1:list,array2:list) -> float:
    if len(array1) < len(array2) < 3:
        raise ValueError("arrays must have the same length and have atleast 3 coordinates both x and y")
    return summation([absolute(array1[x] - array2[x])/(absolute(array1[x] + array2[x])) for x in range(len(array1))])

def minkowski_distance(array1:list,array2:list,power:int|float) -> float:
    if len(array1) < len(array2) < 3:
        raise ValueError("arrays must have the same length and have atleast 3 coordinates both x and y")
    distance = 0
    for i in range(len(array1)):
        distance += absolute(array1[i] - array2[i])**power
    return distance**(1/power)

def moving_average(array:list,steps:int) -> list:
    if steps <= 0:
        raise ValueError(f"steps must be greater than zero {steps} < {0}")
    if len(array) < steps:
        raise ValueError(f"invalid input {steps} > {len(array)}! array must have atleast as many elements as the number of steps!")
    avgs = []
    for i in range(len(array)-steps+1):
        subset = array[i:i+steps]
        avgs.append(sum(subset)/steps)
    return avgs

def exponential_moving_average(array:list,alpha:float) -> list:
    if 0 <= alpha <= 1:
        ema = [array[0]]
        for x in range(1,len(array)):
            ema.append(alpha*array[x]+(1-alpha)*ema[x-1])
        return ema
    else:
        raise ValueError("invalid input! the value of alpha should lie between 0 and 1 included")

def bubble_sort(array:list) -> list:
    for i in range(len(array)):
        for j in range(0,len(array)-i-1):
            if array[j] > array[j+1]:
                array[j],array[j+1] = array[j+1],array[j]
    return array

def quick_sort(array:list) -> list:
    if len(array) <= 1:
        return array
    pivot = array[len(array)//2]
    left = [x for x in array if x < pivot]
    middle = [x for x in array if x == pivot]
    right = [x for x in array if x > pivot]
    return quick_sort(left)+middle+quick_sort(right)

def descending_sort(array:list) -> list:
    for i in range(len(array)):
        for j in range(i+1,len(array)):
            if array[j] > array[i]:
                array[i],array[j] = array[j],array[i]
    return array

def correlation_coefficient(x:list,y:list) -> list:
    if len(x) != len(y):
        raise ValueError("length of x and y aren't the same!")
    xsum = summation(x)
    ysum = summation(y)
    xysum = summation([x[i]*y[i] for i in range(len(x))])
    xsqrsum = summation([x[i]**2 for i in range(len(x))])
    ysqrsum = summation([y[i]**2 for i in range(len(y))])
    n = len(x)*xysum-xsum*ysum
    d = sqrt((len(x)*xsqrsum-xsum**2)*(len(x)*ysqrsum-ysum**2))
    if d == 0:
        return 0
    return n/d

def slope_intercept(array1:list,array2:list) -> list:
    if len(array1) != len(array2):
        raise ValueError("the size of array aren't the same!")
    xmean = mean(array1)
    ymean = mean(array2)
    xdiff = [x-xmean for x in array1]
    ydiff = [y-ymean for y in array2]
    slope = summation([xdiff[i]*ydiff[i] for i in range(len(array1))])/summation([d**2 for d in xdiff])
    intercept = ymean-slope*xmean
    return [slope,intercept]

def min_max(array):
    min_val = constants.inf
    max_val = -constants.inf
    for x in range(len(array)):
        if min_val > array[x]:
            min_val = array[x]
        if max_val < array[x]:
            max_val = array[x]
    return [min_val,max_val]

def mean_sqrd_error(actual:list,predicted:list) -> int|float:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted data aren't equal!")
    errors = [(actual[i]-predicted[i])**2 for i in range(len(actual))]
    return summation(errors)/len(actual)

def errors(actual:list,predicted:list) -> list:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted data aren't equal!")
    return [actual[x]-predicted[x] for x in range(len(actual))]

def mean_error(actual:list,predicted:list) -> int|float:
    return mean(errors(actual,predicted))

def power(base:int|float,exponent:int|float) -> int|float:
    return base**exponent

def power_sum(array:list,exponent:int|float) -> list:
    return summation(power_array(array,exponent))

def power_array(array:list,exponent:int|float) -> list:
    return [x**exponent for x in array]

def primes(limit:int) -> list:
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    primes = []
    for x in range(2,limit):
        is_prime = True
        for i in range(2,int(sqrt(x))+1):
            if x%i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(x)
    return primes

def isprime(number:int) -> bool:
    if number < 2:
        return False
    for x in range(2,int(sqrt(number))+1):
        if number%x == 0:
            return False
    return True

def root_mean_sqrd_error(actual:list,predicted:list) -> int|float:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted data aren't equal!")
    return sqrt(mean_sqrd_error(actual,predicted))

def cost_function(actual:list, predicted:list) -> int|float:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted data aren't equal!")
    errors = [(actual[i]-predicted[i])**2 for i in range(len(actual))]
    return summation(errors)/(2*len(actual))

def scaling(array:list,feature_range:tuple = (0,1)):
    min_val = min(array)
    max_val = max(array)
    scaled_data = [(val - min_val)/(max_val - min_val)*(feature_range[1]-feature_range[0])+feature_range[0] for val in array]
    return scaled_data

def gaussian(array):
    result = []
    std_dev = standard_deviation(array)
    m = mean(array)
    for x in array:
        each = (1/(std_dev*sqrt(2*constants.pi)))*exp(-((x-m)**2)/(2*(std_dev**2)))
        result.append(each)
    return result

def sigmoid(x:int) -> float:
    return 1/(1+constants.e**(-x))
