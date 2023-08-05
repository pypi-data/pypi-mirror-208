from math import log10

def volRatioToDB(vol):
    """
    :param vol: ratio of voltage/current
    :return: dB value of voltage/current ratio
    """
    return(20*log10(vol))

def powRatioToDB(pow):
    """
    :param pow: ratio of power
    :return: dB value of power ratio
    """
    return(10*log10(pow))

def dBToVolRatio(db):
    """
    :param db: decibel Value
    :return: current/voltage ratio associated with decibel value
    """
    return(10**(db/20))

def dBToPowRatio(db):
    """
    :param db: decibel Value
    :return: power ratio associated with decibel value
    """
    return(10**(db/10))
