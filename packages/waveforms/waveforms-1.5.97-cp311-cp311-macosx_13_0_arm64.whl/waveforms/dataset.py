from typing import Callable

from .scan_iter import Storage


class Dataset():

    def __init__(self, storage: Storage | None = None):
        self.vars = {}
        self.storage = storage

    def __getitem__(self, key: str):
        return self.vars.setdefault(key, Variable(key, self))

    def get_raw_data(self, key: str):
        return self.storage.get(key)


class Variable():

    def __init__(self,
                 name: str,
                 dataset: Dataset,
                 unit: str | None = None,
                 label: str | None = None,
                 transform: Callable | None = None):
        self.name = name
        self.dataset = dataset
        self.unit = unit
        self.dims = ()
        self.label = label if label is not None else name
        self.depends = []
        self.transform = transform
        self.function = None

    def depens_on(self, *keys):
        for key in keys:
            if isinstance(key, str):
                key = self.dataset[key]
            self.depends.append(key)

    def infered_from(self, *keys, function=None):
        for key in keys:
            if isinstance(key, str):
                key = self.dataset[key]
            self.depends.append(key)
        self.function = function

    def aggregate_over(self, values, dims, function):
        pass

    def __repr__(self):
        return 'Variable(name=%r, unit=%r)' % (self.name, self.unit)

    def __str__(self):
        if self.unit is None:
            return self.label
        return f"{self.label} / {self.unit}"

    def mean(self, axis=None):
        pass

    def sum(self, axis=None):
        pass

    def std(self, axis=None):
        pass

    def median(self, axis=None):
        pass

    def max(self, axis=None):
        pass

    def min(self, axis=None):
        pass

    def argmax(self, axis=None):
        pass

    def argmin(self, axis=None):
        pass

    def plot(self):
        pass
