import numpy as np
from numpy import pi

from ..library import Context, gate

@gate()
def CZ(q1, q2, /, amp, duration, edge):
    """
    CZ gate with amplitude amp and duration duration
    """
    yield ('!play', amp, duration, edge), ('!channel', 'cz', q1, q2)
    