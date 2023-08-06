import info

author = info.author
version = info.version
homepage = info.homepage

class constants:
    pi = 3.1415926535897932384626433832795
    exp = 2.7182818284590452353602874713527

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

def exp(number:int) -> float:
    return summation([(number**n)/factorial(n) for n in range(0,100)])

def absolute(number:int|float) -> int|float:
    if number < 0:
        return -1*number
    return number

def sqrt(number:int|float) -> float:
    if number < 0:
        return "undefined"
    elif number == 0:
        return 0
    flag = number/2
    while absolute(flag*flag - number) > 0.00001:
        flag = (flag + number/flag)/2
    return flag

def quadratic_roots(a:int|float,b:int|float,c:int|float) -> int|float:
    D = b*b-4*a*c
    if D < 0:
        x1 = f"{-b} + {sqrt(absolute(D))}i"
        x2 = f"{-b} - {sqrt(absolute(D))}i"
        raise Warning(f"discriminant was negative! {[x1,x2]}")
    x1 = -b+sqrt(D)
    x2 = -b-sqrt(D)
    return [x1,x2]

def log(number:int|float) -> float:
    if number <= 0:
        return "invalid input!"
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
    return 2.303*log(number)

def summation(array:list) -> list:
    return sum(array)

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

def mean(array:list) -> int|float:
    return sum(array)/len(array)

def standard_deviation(array:list,kind:str = "population") -> list:
    if kind == "sample":
        d = len(array)-1
    elif kind == "population":
        d = len(array)
    else:
        raise ValueError(f"invalid input {kind}! input should be whether 'population' or 'sample'")
    return sqrt(summation((i - mean(array))**2 for i in array)/(d))

def variance(array:list,kind:str = "population") -> int|float:
    if kind == "sample":
        d = len(array)-1
    elif kind == "population":
        d = len(array)
    else:
        raise ValueError(f"invalid input {kind}! input should be whether 'population' or 'sample'")
    return summation((x - mean(array))**2 for x in array)/d

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

def mean_sqrd_error(actual:list,predicted:list) -> int|float:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted data aren't equal!")
    errors = [(actual[i]-predicted[i])**2 for i in range(len(actual))]
    return summation(errors)/len(actual)

def root_mean_sqrd_error(actual:list,predicted:list) -> int|float:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted data aren't equal!")
    return sqrt(mean_sqrd_error(actual,predicted))

def cost_function(actual:list, predicted:list) -> int|float:
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted data aren't equal!")
    errors = [(actual[i]-predicted[i])**2 for i in range(len(actual))]
    return summation(errors)/(2*len(actual))
