from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Flag, auto
from typing import NamedTuple, Optional


class Signal(Flag):
    trace = auto()
    iq = auto()
    state = auto()

    _avg_trace = auto()
    _avg_iq = auto()
    _avg_state = auto()
    _count = auto()

    trace_avg = trace | _avg_trace

    iq_avg = iq | _avg_iq

    population = state | _avg_state
    count = state | _count
    diag = state | _count | _avg_state


class MeasurementTask(NamedTuple):
    qubit: str
    cbit: int
    time: float
    signal: Signal
    params: dict
    hardware: Optional[ADChannel | MultADChannel] = None
    shift: float = 0


class AWGChannel(NamedTuple):
    name: str
    sampleRate: float
    size: int = -1
    amplitude: Optional[float] = None
    offset: Optional[float] = None
    commandAddresses: tuple = ()


class MultAWGChannel(NamedTuple):
    I: Optional[AWGChannel] = None
    Q: Optional[AWGChannel] = None
    LO: Optional[str] = None
    lo_freq: float = -1
    lo_power: Optional[float] = None


class ADChannel(NamedTuple):
    name: str
    sampleRate: float = 1e9
    trigger: str = ''
    triggerDelay: float = 0
    triggerClockCycle: float = 8e-9
    commandAddresses: tuple = ()


class MultADChannel(NamedTuple):
    I: Optional[ADChannel] = None
    Q: Optional[ADChannel] = None
    IQ: Optional[ADChannel] = None
    Ref: Optional[ADChannel] = None
    LO: Optional[str] = None
    lo_freq: float = -1
    lo_power: Optional[float] = None


class GateConfig(NamedTuple):
    name: str
    qubits: tuple
    type: str = 'default'
    params: dict = {}


class ABCCompileConfigMixin(ABC):
    """
    Mixin for configs that can be used by compiler.
    """

    @abstractmethod
    def _getAWGChannel(self, name, *qubits) -> AWGChannel | MultAWGChannel:
        """
        Get AWG channel by name and qubits.
        """
        pass

    @abstractmethod
    def _getADChannel(self, qubit) -> ADChannel | MultADChannel:
        """
        Get AD channel by qubit.
        """
        pass

    @abstractmethod
    def _getGateConfig(self, name, *qubits) -> GateConfig:
        """
        Return the gate config for the given qubits.

        Args:
            name: Name of the gate.
            qubits: Qubits to which the gate is applied.
        
        Returns:
            GateConfig for the given qubits.
            if the gate is not found, return None.
        """
        pass

    @abstractmethod
    def _getAllQubitLabels(self) -> list[str]:
        """
        Return all qubit labels.
        """
        pass


class CompileConfigMixin(ABCCompileConfigMixin):
    pass
