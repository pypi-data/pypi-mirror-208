import matplotlib.pyplot as plt
from math import pi
import numpy as np
e0 = 8.854*10**(-12)
def matPlotLibPlotAndShow(start,end,func,n=100000):
    """
    :param start: lower bound for domain
    :param end: upper bound for domain
    :param func: function to be plotted
    :param n: number of data points to be plotted - will be spread evenly across the domain
    :return: None - a matPlotLib window of the plot will open
    """
    inp = np.linspace(start, end, n)
    outP = np.zeros(n)
    i = 0
    for val in inp:
        outP[i] = func(val)
        i += 1
    plt.plot(inp, outP)
    plt.show()

def numericalDerivative(func,x,deltaX = 0.0000000001):
    """
    :param func: function to be taken derivative of
    :param x: integer or float value at which derivative is evaluated
    :param deltaX: integer or float change in input used to calculate derivative
    :return: integer or float derivative of function at that point calculated using numerical methods
    """
    return((func(x+deltaX)-func(x-deltaX))/(2*deltaX))

def electricField(q0,p0,p):
    """
    :param q0: charge creating electric field
    :param p0: position of charge
    :param p: position where electrical field is being measured from - must be same dimension as p0
    :return:
    """
    r = p-p0
    return q0*r/(4*pi*e0*abs(r)**2)




