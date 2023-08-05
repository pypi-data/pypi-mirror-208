from numpy.linalg import solve as linearSolve
from math import sqrt,fabs,e
import numpy as np
def secondOrderDifferentialEquationSolver(a,b,c,x0=0,dxodt=0):
    """
    x'' + a x' + b x = c
    :param a: coefficient of the first derivative term
    :param b: coefficient of the zeroth derivative term
    :param c: term on the right side
    :param x0: inital condition of the function
    :param dxodt: intial condition of the first derivative
    :return: function of the solution to the differential equation, along with a message printed to console regarding the details
    """

    final = c/b
    alpha = a/2
    omega0 = sqrt(b)
    rad = sqrt(fabs(alpha**2-omega0**2))
    if (round(alpha,1)>round(omega0,1)):
        s1 = -alpha+rad
        s2 = -alpha-rad
        left = np.array([[1,1],[-s1,-s2]])
        right = np.array([x0-final,dxodt])
        a1,a2 = linearSolve(left,right)
        print("Overdamped : s1 = {}, s2 = {}, A1 = {}, A2 = {}\nx(t) = A1e^(-s1t) + A2e^(-s2t)".format(s1,s2,a1,a2))
        outP = lambda t : a1*e**(-s1*t)+a2*e**(-s2*t) + final
        return outP
    elif (round(alpha,1)==round(omega0,1)):
        left = np.array([[1,0],[0,1]])
        right = np.array([x0-final,dxodt])
        a1,a2 = linearSolve(left,right)
        print("Critically Damped : \u03B1 = {}, A1 = {}, A2 = {}\nx(t) = e^(-\u03B1t)(A1 + A2t)".format(alpha,a1,a2))
        outP = lambda t : (a1 + a2*t)*e**(-alpha*t)
    else:
        left = np.array([[1,0],[-alpha,rad]])
        right = np.array([x0-final,dxodt])
        coeff = linearSolve(left,right)
        print("Underdamped : \u03B1 = {}, \u03A9 = {}, A1 = {}, A2 = {}\nx(t) = e^(-\u03B1t)(A1cos(\u03A9t) + A2sin(\u03A9t))".format(alpha, rad,coeff[0],coeff[1]))
        outP = lambda t : e**(-alpha*t)*(coeff[0]*cos(rad*t)+coeff[1]*sin(rad*t)) + final
        return outP
