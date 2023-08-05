import numpy as np
from numpy import pi

from ..library import Context, gate


@gate()
def U(qubit, /, theta, phi, lambda_):
    yield ('pi2pulse', -lambda_), qubit
    yield ('pi2pulse', -pi - theta - lambda_), qubit
    yield ('P', theta + phi + lambda_), qubit


@gate()
def P(ctx, qubit, /, phi):
    freq = ctx.get('freq', qubit)
    yield ('!add_phase', phi), ('!frame', freq, ('!channel', 'rf', qubit))


@gate(type='Physical')
def P(ctx, qubit, /, phi):
    # (('rfUnitary', pi / 2, arb_phase), qubit)
    # (('rfUnitary', pi / 2, arb_phase), qubit)
    # (('rfUnitary', pi / 2, phi / 2 + arb_phase + k * pi), qubit)
    # (('rfUnitary', pi / 2, phi / 2 + arb_phase + k * pi), qubit)
    freq = ctx.get('freq', qubit)

    yield ('!add_phase', phi), ('!frame', freq, ('!channel', 'rf', qubit))

    yield ('pi2pulse', 0), qubit
    yield ('pi2pulse', 0), qubit

    yield ('!halve_phase', ), ('!frame', freq, ('!channel', 'rf', qubit))

    yield ('pi2pulse', 0), qubit
    yield ('pi2pulse', 0), qubit

    yield ('!set_phase', 0), ('!frame', freq, ('!channel', 'rf', qubit))


@gate()
def pi2pulse(qubit,
             /,
             phi,
             *,
             amp=1,
             duration=20e-9,
             freq=3e9,
             shape='hanning'):
    """
    pi/2 pulse with phase phi

    U = exp(-i pi / 4 * (cos(phi) * sigma_x + sin(phi) * sigma_y))
    or
    U = U3(pi/2, phi - pi/2, pi/2 - phi)

    Parameters
    ----------
    qubit : Qubit
        The qubit to apply the pulse to
    phi : float
        The phase of the pulse
    amp : float, optional
        The amplitude of the pulse, by default 1
    duration : float, optional
        The duration of the pulse, by default 20e-9
    freq : float, optional
        The frequency of the pulse, by default 3e9
    shape : str, optional
        The shape of the pulse, by default 'hanning'
    """
    operation = ('!play', shape, amp, duration, phi)
    target = ('!frame', freq, ('!channel', 'rf', qubit))
    yield operation, target

