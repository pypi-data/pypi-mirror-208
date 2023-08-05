from __future__ import annotations

import sys
from functools import wraps
from inspect import signature
from typing import Any, Callable, NamedTuple

import dill

from .config import CompileConfigMixin
from .context import Context

_NODEFAULT = object()
Module = type(sys)


class GateSignature(NamedTuple):
    ctx: str | None
    cfg: str | None
    qubits: tuple[str] | tuple[tuple[str], str]
    arguments: tuple[str]
    args: str | None
    params: tuple[str]
    kwds: str | None


def gate_signature(fun: Callable) -> GateSignature:

    sig = signature(fun)

    ctx = None
    cfg = None

    qubits = []
    arb_qubits = False
    arguments = []
    args = None
    params = []
    kwds = None

    for p in sig.parameters.values():
        if issubclass(p.annotation, Context):
            ctx = p.name
        elif issubclass(p.annotation, CompileConfigMixin):
            cfg = p.name
        elif p.name == 'qubits':
            arb_qubits = True
        elif p.kind == p.POSITIONAL_ONLY:
            qubits.append(p.name)
        elif p.kind == p.POSITIONAL_OR_KEYWORD:
            arguments.append(p.name)
        elif p.kind == p.KEYWORD_ONLY:
            params.append(p.name)
        elif p.kind == p.VAR_POSITIONAL:
            args = p.name
        elif p.kind == p.VAR_KEYWORD:
            kwds = p.name
        else:
            pass

    qubits = tuple(qubits)
    arguments = tuple(arguments)
    params = tuple(params)

    if arb_qubits:
        qubits = (qubits, 'qubits')

    return GateSignature(ctx, cfg, qubits, arguments, args, params, kwds)


class Library():

    def __init__(self):
        self.parents: tuple[Library, ...] = ()
        self.gates = {}

    def getGate(self, name: str, type: str = 'default'):
        if name in self.gates:
            gate, params = self.gates[name].get(type, (None, {}))
        else:
            gate, params = None, {}
        if gate is None and len(self.parents) > 0:
            for lib in self.parents:
                gate, params = lib.getGate(gate, type)
                if gate is not None:
                    break
        return gate, params

    def gate(self,
             name: str | None = None,
             type: str = 'default') -> Callable[[Callable], Callable]:

        def decorator(func, name=name):
            if name is None:
                name = func.__name__

            sig = gate_signature(func)

            group = self.gates.setdefault(name, dict())
            group[type] = func, sig

            return func

        return decorator

    @classmethod
    def from_module(cls, mod: Module) -> Library:
        return cls()

    @classmethod
    def from_str(cls, name: str) -> Library:
        return cls()

    @classmethod
    def from_code(cls, code: str) -> Library:
        return cls()

    def __getstate__(self):
        state = self.__dict__.copy()
        for gate in state['gates']:
            for t in state['gates'][gate]:
                state['gates'][gate][t] = dill.dumps(state['gates'][gate][t])
        return state

    def __setstate__(self, state):
        for gate in state['gates']:
            for t in state['gates'][gate]:
                state['gates'][gate][t] = dill.loads(state['gates'][gate][t])
        self.__dict__ = state


def get_library_in_module(mod: Module) -> Library:
    if hasattr(mod, '__library__'):
        return mod.__library__
    else:
        mod.__library__ = Library()
        return mod.__library__


def gate(name: str | None = None,
         type: str = 'default') -> Callable[[Callable], Callable]:

    def decorator(func):
        lib = get_library_in_module(sys.modules[func.__module__])
        return lib.gate(name, type)(func)

    return decorator


def libraries(*libs: str | Library | Module) -> Library:
    libs = list(libs)
    for i in range(len(libs)):
        if isinstance(libs[i], Library):
            pass
        elif isinstance(libs[i], str):
            libs[i] = Library.from_str(libs[i])
        elif isinstance(libs[i], Module):
            libs[i] = Library.from_module(libs[i])
        else:
            raise TypeError(
                f"invalid library type: {type(libs[i])} of {i}th argument {libs[i]}"
            )
    ret = Library()
    ret.parents = libs
    return ret
