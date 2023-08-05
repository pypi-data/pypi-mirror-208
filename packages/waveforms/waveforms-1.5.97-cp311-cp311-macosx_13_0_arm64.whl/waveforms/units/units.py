from fractions import Fraction

# SI prefixes
_prefixes = [
    ('Y',  Fraction(10**24)),
    ('Z',  Fraction(10**23)),
    ('E',  Fraction(10**18)),
    ('P',  Fraction(10**15)),
    ('T',  Fraction(10**12)),
    ('G',  Fraction(10**9)),
    ('M',  Fraction(10**6)),
    ('k',  Fraction(10**3)),
    ('h',  Fraction(10**2)),
    ('da', Fraction(10**1)),
    ('d',  Fraction(1, 10**1)),
    ('c',  Fraction(1, 10**2)),
    ('m',  Fraction(1, 10**3)),
    ('u',  Fraction(1, 10**6)),
    ('n',  Fraction(1, 10**9)),
    ('p',  Fraction(1, 10**12)),
    ('f',  Fraction(1, 10**15)),
    ('a',  Fraction(1, 10**18)),
    ('z',  Fraction(1, 10**21)),
    ('y',  Fraction(1, 10**24))
    ] # yapf: disable

class UnitFinder(dict):
    """A dictionary of units and their conversion factors to SI units.

    The keys are the unit names, and the values are the conversion factors
    """

    def __missing__(self, key):
        return []


class Dimension(dict):
    units = {}

    def __init__(self, **kwds):
        self.update(kwds)

    def __missing__(self, key):
        self[key] = Fraction(0, 1)
        return self[key]

    def __mul__(self, other):
        d = Dimension()
        for key in set(self.keys()) | set(other.keys()):
            d[key] = self[key] + other[key]
        return d

    def __truediv__(self, other):
        d = Dimension()
        for key in set(self.keys()) | set(other.keys()):
            d[key] = self[key] - other[key]
        return d

    def __pow__(self, n):
        d = Dimension()
        for key in self:
            d[key] = self[key] * n
        return d

    def __eq__(self, other):
        if isinstance(other, (int, float, complex)) and other == 1:
            return all(v == 0 for v in self.values())
        if not isinstance(other, Dimension):
            raise TypeError()
        for key in set(self.keys()) | set(other.keys()):
            if self[key] != other[key]:
                return False
        return True

    @classmethod
    def add_unit(cls, unit, dimension):
        pass

    @classmethod
    def get_units(cls, dimension, scalar=True):
        pass


class Value():

    def __init__(self, num, denominator, dimension, SI_unit=''):
        self.num = num
        self.denominator = denominator
        self.dimension = dimension
        self.SI_unit = SI_unit

    def __add__(self, other):
        if isinstance(other, (int, float, complex)):
            other = Value(other, 1, Dimension(), '')
        assert self.dimension == other.dimension
        return self.__class__(self.num + other.num, self.denominator,
                              self.dimension)

    def __radd__(self, other):
        return self + other

    def __mul__(self, v):
        if isinstance(v, (int, float, complex)):
            return self.__class__(round(self.num * v), self.denominator,
                                  self.dimension)
        elif isinstance(v, Value):
            return self.__class__(round(self.num * v.num),
                                  self.denominator * v.denominator,
                                  self.dimension * v.dimension)
        else:
            raise TypeError()

    def __rmul__(self, v):
        return self * v

    def __float__(self):
        return self.num / self.denominator

    def __str__(self):
        from matplotlib.ticker import EngFormatter
        return EngFormatter().format_eng(
            self.num / self.denominator) + self.SI_unit


ns = Value(1000, 1e12, Dimension(T=1), 's')
us = Value(1000000, 1e12, Dimension(T=1), 's')
ms = Value(1000000000, 1e12, Dimension(T=1), 's')
s = Value(1000000000000, 1e12, Dimension(T=1), 's')
Hz = Value(1, 1, Dimension(T=-1), 'Hz')
kHz = Value(1000, 1, Dimension(T=-1), 'Hz')
MHz = Value(1000000, 1, Dimension(T=-1), 'Hz')
GHz = Value(1000000000, 1, Dimension(T=-1), 'Hz')