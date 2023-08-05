from math import fabs



def rect(t):
    t = fabs(t)
    if(fabs(t)==0.5):
        return 0.5
    if(t<0.5):
        return 1
    return 0

def unitStep(t):
    if t > 0:
        return 1
    if t == 0:
        return 0.5
    return 0

def ramp(t):
    if t > 0:
        return t
    return 0

def tri(t):
    if(fabs(t)<1):
        return 1-fabs(t)
    return 0

def funcSection(func,a,b):
    def outP(t):
        return func(t) * rect((t-(a+b)*0.5)/(a-b))
    return outP




