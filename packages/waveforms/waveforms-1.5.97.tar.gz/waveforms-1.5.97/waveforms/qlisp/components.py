import numpy as np


def mirror(x, lo, hi):
    y = x
    while True:
        y = hi - np.abs(hi - (np.abs(y - lo) + lo))
        if np.all((y <= hi) * (y >= lo)):
            break
    return y


class Component():

    def __init__(self, name, config):
        self.name = name
        self.config = config

    @staticmethod
    def _make_obj(info):
        if info['type'] == 'poly':
            return np.poly1d(info['coeffs'])
        elif info['type'] == 'spec':
            return np.poly1d(info['fun']['coeffs'])
        else:
            raise ValueError(f"Unknown type {info['type']}")

    @property
    def params(self):
        params = self.config.get(f"{self.name}.params")
        ret = {}
        for k, v in params.items():
            if isinstance(v, dict):
                if 'type' in v:
                    ret[k] = self._make_obj(v)
                else:
                    ret[k] = v
            else:
                ret[k] = v
        return ret

    def ports(self):
        return {}

    def get(self, query):
        return self.config.get(f"{self.name}.{query}")


class Qubit(Component):

    def spectrum(self, bias):
        return np.poly1d(self.get('params.spec_poly'))(bias)

    def set_frequency(self, freq):
        pass


class Coupler(Component):

    def spectrum(self, bias):
        return np.poly1d(self.get('params.spec_poly'))(bias)

    def set_frequency(self, freq):
        pass


class FeedLine(Component):
    pass


class Resonator(Component):
    pass


class Amplifier(Component):
    pass