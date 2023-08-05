_lib = {}


class Operation:

    def __init__(self, name, namespace=None, *args):
        self.name = name
        self.namespace = namespace
        self.args = args

    def __call__(self, ctx, *args, **kwargs):
        return ctx.call(self.name, *args, **kwargs)


def gate(name=None, number_of_qubits=1, namespace=None, *args):

    def decorator(func, name=name):
        if name is None:
            name = func.__name__

        def wrapper(ctx, *args, **kwargs):
            return func(ctx, *args, **kwargs)

        return wrapper

    return decorator


@gate()
def rfUnitary(ctx, qubit, theta, phi):
    from waveforms import zero

    pulse = zero()

    qubits = (qubit, )

    yield ('!play', pulse, ('rf', qubit), 0)
    yield ('!play', pulse, ('coupler.rf', *qubits))


@gate()
def measure(ctx, qubit, cbit):
    from waveforms import zero

    yield ('!play', zero(), ('detector.rf', qubit), 0)
    yield ('!capture', qubit, cbit, ctx.params)
