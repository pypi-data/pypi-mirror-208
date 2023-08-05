from cmath import polar as pol
from math import sin,cos,pi,e,ceil,log10 as log,log as ln,sqrt,acosh,asinh,cosh,sinh,fabs
from .dBtoRatio import *

def ChebyshevPolynomial(n,x):
    """
    :param n: degree of chebyshev polynomial
    :param x: value where chebyshev polynomial is evaluated
    :return: uses recursion to calculate value of chebyshev polynomial at x
    """
    if(n==0):
        return 1
    if(n==1):
        return x
    return 2*x*ChebyshevPolynomial(n-1,x) - ChebyshevPolynomial(n-2,x)

def polarComplex(m,th):
    return complex(m*cos(th),m*sin(th))

def zeroMultiplierFuncGenerator(poles,s):
    """
    :param poles: list of values s1,s2,s3,...
    :param s: point where output needs to be evaluated
    :return: value of (1 + s/s1)(1 + s/s2)(1 + s/s3)...
    """
    outP = 1
    for pole in poles:
        outP *= (1+s/pole)
    return outP

class Filter:
    """
    initializes the abstract filter class,
    parent of the four different types of filter -
    lowpass, highpass, bandpass, bandstop
    ASSUMES SYMMETRIC PASSBAND AND STOPBAND GAIN FOR BANDPASS/BANDSTOP FILTERS,
    THUS USE STRICTEST AND FASTEST DROPOFF
    """
    passBandGainDB = 0
    stopBaandGainDB = -20
    degree = 0
    poles = []
    zeroes = []
    implemented = False
    FilterType = ""
    def tfunc(s):
        return
    def __init__(self):
        pass
    def __init__(self,passBandGain,stopBandGain,DB=True):
        if (stopBandGain >= passBandGain):
            raise ValueError("Passband gain has to be higher than stopband gain")
        self.passBandGainDB = passBandGain
        self.stopBandGainDB = stopBandGain
    def setPassBandGain(self,passBandGain,DB=True):
        self.passBandGainDB = passBandGain



class LPF(Filter):
    """
    LOWPASS FILTER CLASS:
    first set it's pasband frequency, stopband frequency, stopband gain, passband gain
    before calling the implementChebyshevTypeI() or implementButterworth() methods
    more implementations will be supported soon
    after implementation, poles, zeroes, and transfer functions can be requested
    """
    def __init__(self,passBandGain,stopBandGain,passBandFrequency,stopBandFrequency,DB=True,kHz=False,power=False):
        if(stopBandGain >= passBandGain):
            raise ValueError("Passband gain has to be higher than stopband gain")
        if (passBandFrequency >= stopBandFrequency):
            raise ValueError("Passband frequency has to be lower than stopband frequency in a LPF")
        self.passBandGainDB = passBandGain
        self.passBandPowerGain = dBToPowRatio(self.passBandGainDB)
        self.stopBandGainDB = stopBandGain
        self.stopBandPowerGain = dBToPowRatio(self.stopBandGainDB)
        self.passBandFrequency = passBandFrequency
        self.stopBandFrequency = stopBandFrequency

    def implementButterworth(self):
        self.FilterType = "Butterworth"
        self.degree = ceil(0.5*log((1/self.stopBandPowerGain - 1)/(1/self.passBandPowerGain - 1))/log(self.stopBandFrequency/self.passBandFrequency))
        f3 = 0.5*((self.passBandFrequency)/(1/self.passBandPowerGain - 1)**(1/(2*self.degree)) + ((self.stopBandFrequency)/(1/self.stopBandPowerGain - 1)**(1/(2*self.degree))))
        for i in range(self.degree):
            self.poles.append(polarComplex(2*pi*f3,pi/(2*self.degree) + pi*i/self.degree + pi/2))
        self.tfunc = lambda s: 1/zeroMultiplierFuncGenerator(self.poles,s)
        self.implemented = True

    def implementChebyshevTypeI(self):
        self.FilterType = "Chebyshev Type I"
        self.degree = ceil(acosh(sqrt((1/self.stopBandPowerGain - 1)/(1/self.passBandPowerGain - 1)))/acosh(self.stopBandFrequency/self.passBandFrequency))
        eps = 0.5 * ((1/self.passBandPowerGain - 1) + (1/self.stopBandPowerGain - 1)/(ChebyshevPolynomial(self.degree,self.stopBandFrequency/self.passBandFrequency)**2))
        z = asinh(sqrt(1/eps))/self.degree
        for i in range(self.degree * 2):
            x = complex(2*pi*self.passBandFrequency*sin((2*i - 1)*pi/(2*self.degree))*sinh(z),2*pi*self.passBandFrequency*cos((2*i - 1)*pi/(2*self.degree))*cosh(z))
            if(fabs(pol(x)[1]) >= pi/2):
                self.poles.append(x)
        self.tfunc = lambda s : 1/zeroMultiplierFuncGenerator(self.poles,s)
        self.implemented = True


    def getTransferFunction(self):
        return self.tfunc

    def getDegree(self):
        return self.degree

    def getPoles(self):
        return self.poles

    def getFilterType(self):
        return self.FilterType

    def __str__(self):
        outP = "{} LPF filter:\nPASSBAND GAIN: {}dB\nSTOPBAND GAIN: {}dB\nPASSBAND FREQUENCY: {}Hz\nSTOPBAND FREQUENCY: {}Hz\n".format(self.FilterType,self.passBandGainDB,self.stopBandGainDB,self.passBandFrequency,self.stopBandFrequency)
        if(self.implemented):
            outP += "DEGREE: {}".format(self.degree)
        return outP











