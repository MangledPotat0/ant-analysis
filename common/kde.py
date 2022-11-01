import numpy as np
import math
from matplotlib import pyplot as plt


# For a given histogram, return a KDE
def kde(random_variable, resolution):
    h = bandwidth()
    n = len(random_variable)
    rv = np.around(random_variable, int(math.log(1 / resolution, 10)))
    print(rv)
    start = min(rv)
    end = max(rv)
    bincount = int((end - start) / resolution)
    abcissa = np.linspace(start, end, bincount + 1)
    ordinate = np.linspace(start, end, bincount + 1)
    integ = 0

    for i in range(len(abcissa)):
        ker = kernel((abcissa[i]-rv)/h,'gaussian')
        ordinate[i] = 1/(n * h) * sum(ker)
        integ += ordinate[i] * resolution

    return np.array([abcissa, ordinate/integ])

# Hardcoded value because idk how to properly obtain the bandwidth
def bandwidth():

    return .08

def kernel(argument, kernel_type, params):
    mean, sd = params
    if kernel_type.lower() == 'gaussian':
        output = 1/np.sqrt(2*sd) * np.exp(-(argument - mean)**2 / (2*sd**2))

    return output

# EOF
