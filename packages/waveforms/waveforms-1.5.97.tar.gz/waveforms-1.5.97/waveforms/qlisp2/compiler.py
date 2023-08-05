from __future__ import annotations

import sys
from functools import wraps
from inspect import signature
from typing import Any, Callable, Iterable, NamedTuple, Optional, Union

import dill

from .context import Context
from .config import CompileConfigMixin
from .library import Library


class Gate(NamedTuple):
    name: str
    type: str
    arguments: tuple
    params: dict
    ctx: Context


def parse_contex(contex, qubits, type):
    if contex is None:
        return None, {}, type
    return None, {}, type


def parse_gate(gate: str | tuple[str, ...], qubits: list[str | int]) -> Gate:
    if isinstance(gate, str):
        name = gate
        type = 'default'
        arguments = []
        ctx = None
    elif isinstance(gate, tuple):
        name = gate[0]
        type = 'default'
        arguments = []
        for arg in gate[1:]:
            if isinstance(arg, tuple) and arg[0] == 'with':
                ctx = arg
            else:
                arguments.append(arg)
    else:
        raise TypeError(f"invalid type: {type(gate)} of gate {gate}")
    ctx, params, type = parse_contex(ctx, qubits, type)

    return Gate(name, type, arguments, params, ctx)


def call_gate(ctx: Context, lib: Library, gate: str | tuple[str, ...],
              qubits: tuple[int | str, ...], *args, **kwds):

    gate = parse_gate(gate)

    gate_cfg = ctx.cfg._getGateConfig(gate.name, *qubits, type=gate.type)

    params = gate_cfg.params.copy()
    params.update(gate.ctx.params)

    gate, sig = lib.getGate(gate.name, gate_cfg.type)
    if gate is None:
        raise KeyError(f'Undefined {gate_cfg.type} type of {gate.name} gate.')

    for cmd in gate(ctx, gate_cfg.qubits, *args):
        if cmd[0].startswith('!'):
            yield cmd
        else:
            yield from call_gate(ctx, lib, cmd, *args, **kwds)
