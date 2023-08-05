from collections import defaultdict


class Frame():
    __slots__ = ['channel', 'frequency', 'time', 'phase']

    def __init__(self, channel, frequency):
        self.channel = channel
        self.frequency = frequency
        self.time = 0
        self.phase = 0


class VirtualMachine:

    def __init__(self):
        self.waveforms = defaultdict(list)
        self.frames = defaultdict(lambda key: Frame(*key))
        self.captures = defaultdict(list)
        self.channels = defaultdict(list)
        self.stack = []
        self.mem = []
        self.sp = 0  # stack pointer
        self.bp = 0  # base pointer
        self.sl = 0  # static link
        self.pc = 0  # program counter
        self.clk = 0

    def get_frame(self, channel, frequency=None):
        if frequency is None:
            return [
                self.frames[(channel, frequency)]
                for frequency in self.channels[channel]
            ]
        if (channel, frequency) not in self.frames:
            self.frames[(channel, frequency)] = Frame(channel, frequency)
            self.channels[channel].append(frequency)

        return self.frames[(channel, frequency)]


def decode(instruction):
    op_code = instruction[0]
    arguments = instruction[1:]
    return op_code, arguments


def execute(vm: VirtualMachine, instruction):
    op_code, arguments = decode(instruction)
    dispatch_table = {
        '!play': play,
        '!play_data': play_data,
        '!capture': capture,
        '!capture_trace': capture_trace,
        '!capture_iq': capture_iq,
        '!delay': delay,
        '!align': align,
        '!add_phase': add_phase,
        '!set_phase': set_phase,
        '!halve_phase': halve_phase,
    }


def play(vm: VirtualMachine, shape, amplitude, duration, phase, frequency,
         channel):
    frame = vm.get_frame(channel, frequency)
    time = frame.time
    phase = frame.phase + phase
    vm.waveforms.setdefault(channel, []).append(
        (time, frequency, phase, amplitude, shape))
    frame.time += duration


def play_data(vm: VirtualMachine, shape, amplitude, duration, phase, frequency,
              channel):
    frame = vm.get_frame(channel, frequency)
    time = frame.time
    phase = frame.phase + phase
    vm.waveforms.setdefault(channel, []).append(
        (time, frequency, phase, amplitude, shape))
    frame.time += duration


def capture(vm: VirtualMachine, channel, frequency, duration, time, threshold,
            phi, dest):
    frame = vm.get_frame(channel, frequency)
    time = frame.time
    vm.captures.setdefault(channel, []).append(
        (time, frequency, duration, time, threshold, phi, dest))
    frame.time += duration


def capture_trace(vm: VirtualMachine, channel, duration, time, dest):
    vm.waveforms.setdefault(channel, []).append((time, duration, dest))


def capture_iq(vm: VirtualMachine, channel, frequency, duration, time, dest):
    frame = vm.get_frame(channel, frequency)
    time = frame.time
    phase = frame.phase + phase
    vm.waveforms.setdefault(channel, []).append((time, frequency, phase, dest))
    frame.time += duration


def delay(vm: VirtualMachine, duration, channel, frequency):
    frame = vm.get_frame(channel, frequency)
    frame.time += duration


def align(vm: VirtualMachine, channel, frequency):
    frame = vm.get_frame(channel, frequency)
    frame.time = 0


def add_phase(vm: VirtualMachine, channel, frequency, phase):
    frame = vm.get_frame(channel, frequency)
    frame.phase += phase


def set_phase(vm: VirtualMachine, channel, frequency, phase):
    frame = vm.get_frame(channel, frequency)
    frame.phase = phase


def halve_phase(vm: VirtualMachine, channel, frequency):
    frame = vm.get_frame(channel, frequency)
    frame.phase /= 2
