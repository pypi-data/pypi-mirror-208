from cmath import polar as pol
from math import pi
import warnings

w = 2*pi*60
freqSet = False

def setFrequency(freq):
    """
    :param freq: sets frequency for calcuations
    :return: None
    """
    w = freq
    freqSet = True

def phasorToFunction(z):
    """
    :param z: phasor
    :param freq: frequency - default frequency that's set previously will be used
    :return: string representation of the functional representation of the phasor
    Warns if frequency is not set before use
    """
    p = pol(z)

    if(not freqSet):
        warnings.warn("Frequency value is not set. Call setFrequency to set it. Default frequency value of 60Hz will be used.")

    return("f(t) = {}cos({}t + {})".format(p[0],w,p[1]))

def capacitor(c,unit="uf"):
    """
    :param c: capacitance
    :param unit: units of capacitance - default is microFarads
    :return: complex number representing the phasor
    Raises error if units are not recognized
    Warns if frequency is not set before use
    """
    unitDict = {"f":1,"mf":10**(-3),"uf":10**(-6),"nf":10**(-9)}
    try:
        factor = unitDict[unit]
    except:
        raise Exception("Improper Units")
    if(not freqSet):
        warnings.warn("Frequency value is not set. Call setFrequency to set it. Default frequency value of 60Hz will be used.")
    return (1/complex(0,w*c*factor))

def resistor(r,unit="kohm"):
    """
    :param r: resistance
    :param unit: units of resistance - default is kiloOhm
    :return: number representing the phasor
    Raises error if units are not recognized
    """
    unitDict = {"ohm": 1, "kohm": 10 ** (3)}
    try:
        factor = unitDict[unit]
    except:
        raise Exception("Improper Units")
    return complex(factor*r,0)

def inductor(l,unit="mh"):
    """
    :param c: inductance
    :param unit: units of inductance - default is milliHenrys
    :return: complex number representing the phasor
    Raises error if units are not recognized
    Warns if frequency is not set before use
    """
    unitDict = {"h":1,"mh":10**(-3),"uh":10**(-6)}

    try:
        factor = unitDict[unit]
    except:
        raise Exception("Improper Units")

    if(not freqSet):
        warnings.warn("Frequency value is not set. Call setFrequency to set it. Default frequency value of 60Hz will be used.")

    return complex(0,w*l*factor)


def totalZpar(*argv):
    """
    :param x: impedences of all the components in parallel
    :return: impedence of the equivalent component
    """
    if len(argv) == 1:
        return argv[0]

    s = argv[0]*argv[1]/(argv[0]+argv[1])
    for element in argv[2:]:
        s = s*element/(s+element)
    return s


