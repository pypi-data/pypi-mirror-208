from fractions import Fraction
from math import pi


class Freq(int):

    def __init__(self, v):
        super().__init__(round(v))


class Time(int):

    def __init__(self, v):
        super().__init__(round(v))


class Phase(int):

    def __init__(self, v):
        super().__init__(round(v))


FREQ_RESOLUTION = Fraction(1, 1)
TIME_RESOLUTION = Fraction(1, 1_000_000_000_000_000)
MAX_PHASECODE = 2**32


def time_to_float(a: Time) -> float:
    return float(a * TIME_RESOLUTION)


def freq_to_float(a: Freq) -> float:
    return float(a * FREQ_RESOLUTION)


def phase_to_float(a: Phase) -> float:
    return float(a / MAX_PHASECODE * 2 * pi)


def cast_time(a: float) -> Time:
    return Time(a / TIME_RESOLUTION)


def cast_freq(a: float) -> Freq:
    return Freq(a / FREQ_RESOLUTION)


def cast_phase(a: float) -> Phase:
    return Phase((MAX_PHASECODE + round(
        (a / 2 / pi) * MAX_PHASECODE) % MAX_PHASECODE) % MAX_PHASECODE)


def neg_freq(a: Freq) -> Freq:
    return Freq(-a)


def neg_time(a: Time) -> Time:
    return Time(-a)


def neg_phase(a: Phase) -> Phase:
    return Phase(MAX_PHASECODE - a)


def add_freq_freq(a: Freq, b: Freq) -> Freq:
    return Freq(a + b)


def add_time_time(a: Time, b: Time) -> Time:
    return Time(a + b)


def add_phase_phase(a: Phase, b: Phase) -> Phase:
    return Phase((a + b) % MAX_PHASECODE)


def sub_freq_freq(a: Freq, b: Freq) -> Freq:
    return Freq(a - b)


def sub_time_time(a: Time, b: Time) -> Time:
    return Time(a - b)


def sub_phase_phase(a: Phase, b: Phase) -> Phase:
    return Phase((MAX_PHASECODE + a - b) % MAX_PHASECODE)


def add_freq_float(a: Freq, b: float) -> Freq:
    return Freq(a + round(b / FREQ_RESOLUTION))


def add_time_float(a: Time, b: float) -> Time:
    return Time(a + round(b / TIME_RESOLUTION))


def add_phase_float(a: Phase, b: float) -> Phase:
    return add_phase_phase(a, cast_phase(b))


def sub_freq_float(a: Freq, b: float) -> Freq:
    return Freq(a - round(b / FREQ_RESOLUTION))


def sub_time_float(a: Time, b: float) -> Time:
    return Time(a - round(b / TIME_RESOLUTION))


def sub_phase_float(a: Phase, b: float) -> Phase:
    return sub_phase_phase(a, cast_phase(b))


def mul_freq_time(a: Freq, b: Time) -> Phase:
    return Phase(
        round(a * b * FREQ_RESOLUTION * TIME_RESOLUTION * MAX_PHASECODE) %
        MAX_PHASECODE)


def div_phase_freq(a: Phase, b: Freq) -> Time:
    return Time(
        round(2 * pi * a /
              (MAX_PHASECODE * FREQ_RESOLUTION * TIME_RESOLUTION * b)))


def div_phase_time(a: Phase, b: Time) -> Freq:
    return Freq(
        round(2 * pi * a /
              (MAX_PHASECODE * FREQ_RESOLUTION * TIME_RESOLUTION * b)))


def div_float_time(a: float, b: Time) -> Freq:
    return Freq(round(a / (b * TIME_RESOLUTION * FREQ_RESOLUTION)))


def div_float_freq(a: float, b: Freq) -> Time:
    return Time(round(a / (b * TIME_RESOLUTION * FREQ_RESOLUTION)))

