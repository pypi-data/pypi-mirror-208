from typing import NamedTuple, Sequence


class Address(NamedTuple):
    identifier: str
    offset: int = 0


class Fetch(NamedTuple):
    address: Address


class Channel(NamedTuple):
    identifier: str
    qubits: tuple[str, ...]


class Frame(NamedTuple):
    channel: Channel
    frequency: float = 0.0


class Demodulator(NamedTuple):
    channel: Channel
    frame: Frame
    demodulate: int


class Play(NamedTuple):
    frame: Frame
    duration: float
    window: str
    amplitude: float
    phase: float
    delta: float


class PlayEvenlope(NamedTuple):
    frame: Frame
    size: int
    I: Sequence
    Q: Sequence
    phase: float
    delta: float


class Capture(NamedTuple):
    channel: Channel
    demodulator: Demodulator
    dest: Address


class CaptureIQ(NamedTuple):
    channel: Channel
    demodulator: Demodulator
    dest: Address


class CaptureTrace(NamedTuple):
    channel: Channel
    duration: float
    dest: Address
