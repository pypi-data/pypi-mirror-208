################# 基础指令 #################

from typing import NamedTuple


class Frame(NamedTuple):
    lo: float = 1
    channel: str = 'CH1'
    phase: float = 0
    time: float = 0

#------- 基础波形 -------
class DragL(NamedTuple):
    amp: float = 1
    length: float = 0
    phi: float = 0
    delta: float = 0
    width: float = 1
    beta: float = 0


class DragR(NamedTuple):
    amp: float = 1
    length: float = 0
    phi: float = 0
    delta: float = 0
    width: float = 1
    beta: float = 0


class Flattop(NamedTuple):
    amp: float = 1
    length: float = 0
    phi: float = 0
    delta: float = 0

#----------------------

################# 下发程序示例 #################

import numpy as np

prog = [
    ('!set', 'R0', 0),
    ('!set', 'R1', 5),
    ('!play', Frame(2e9, 'CH1'), DragL(0.8, 10e-9, 1.3, 10e6, 10e-9, 0.2)),
    ('!play', Frame(2e9, 'CH1'), DragR(0.8, 10e-9, 1.3, 10e6, 20e-9, 0.1)),
    ('!delay', Frame(2e9, 'CH1'), 20e-9),
    ('!play', Frame(2e9, 'CH1'), DragL(1, 10e-9, np.pi / 2, 13e6, 10e-9, 0.2)),
    ('!play', Frame(2e9, 'CH1'), DragR(1, 10e-9, np.pi / 2, 13e6, 10e-9, 0.2)),
    ('!add_phase', Frame(2e9, 'CH1'), np.pi),
    ('!play', Frame(2e9, 'CH1'), DragL(0.5, 5e-9, np.pi / 2, 13e6, 10e-9,
                                       0.2)),
    ('!play', Frame(2e9, 'CH1'), Flattop(0.5, 20e-9, np.pi / 2, 13e6)),
    ('!play', Frame(2e9, 'CH1'), DragR(0.5, 5e-9, np.pi / 2, 13e6, 10e-9,
                                       0.2)),
    ('!delay', Frame(2e9, 'CH1'), 10e-9),
    ('!iadd', 'R0', 1),
    ('!ne', 'R0', 'R1'),
    ('!jne', 2),
    ('!end', ),
]

################# 虚拟机参考实现 #################

from collections import defaultdict


class _Channel():
    wav: np.ndarray = np.zeros(100000)  # 输出波形
    sample_rate: int = 100000000000  # 采样率


class _Frame():
    lo: float = 1  # 基频
    time: float = 0  # 当前时间
    last_length: float = 0  # 当前脉冲已输出的长度
    phase: float = 0  # 基本相位
    channel: _Channel = None  # 硬件通道


channels = defaultdict(_Channel)
frames = defaultdict(_Frame)


def get_frame(frame: Frame):
    ret = frames[frame]
    if ret.channel is None:
        ret.channel = channels[frame.channel]
        ret.lo = frame.lo
    return ret


def get_envelope(pulse, frm, tlist):
    if isinstance(pulse, DragL):
        window = (tlist >= pulse.length - pulse.width / 2)
        X = 0.5 + 0.5 * np.cos(2 * np.pi / pulse.width *
                               (tlist - pulse.length))
        Y = -0.5 * pulse.beta * np.pi * np.sin(2 * np.pi / pulse.width *
                                               (tlist - pulse.length))
        phi = pulse.phi - 2 * np.pi * frm.lo * pulse.length
    elif isinstance(pulse, DragR):
        window = (tlist <= pulse.width / 2)
        X = 0.5 + 0.5 * np.cos(2 * np.pi / pulse.width * tlist)
        Y = -0.5 * pulse.beta * np.pi * np.sin(2 * np.pi / pulse.width * tlist)
        phi = pulse.phi
    elif isinstance(pulse, Flattop):
        X = 1
        Y = 0
        window = 1
        phi = pulse.phi
    else:
        raise ValueError(f'Unknow pulse type {type(pulse)}')
    X, Y = X * np.cos(phi) - Y * np.sin(phi), X * np.sin(phi) + Y * np.cos(phi)
    return pulse.amp * window * X, pulse.amp * window * Y


def play(pulse, frm):
    """播放波形片段
    """
    sample_rate = frm.channel.sample_rate
    start = round(frm.time * sample_rate)
    size = round(pulse.length * sample_rate)

    if start + size > len(frm.channel.wav):
        raise RuntimeError(f'AWG wavform overflow.')
    tlist = np.arange(size) / sample_rate

    Omega_x, Omega_y = get_envelope(pulse, frm, tlist)

    w = 2 * np.pi * (frm.lo + pulse.delta)
    phi = frm.phase - 2 * np.pi * pulse.delta * frm.time
    phi += 4 * np.pi * pulse.delta * frm.last_length

    wav = Omega_x * np.cos(w * tlist + phi) - Omega_y * np.sin(w * tlist + phi)

    frm.channel.wav[start:start + size] += wav
    frm.time += pulse.length
    
    # 连续 play 被看作是输出同一个 pulse 的不同片段
    # 因此记录该 pluse 已输出的时长对于正确处理该 pulse 是必要的
    frm.last_length += pulse.length


def run_prog(prog):
    ptr = 0
    flag = 0
    reg = {f'R{i}': 0 for i in range(8)}
    while True:
        step = prog[ptr]
        ptr += 1
        if step[0] == '!end':
            break
        elif step[0] == '!nop':
            continue

        if step[0] in ['!jmp', '!jne', '!set', '!add', '!iadd', '!eq', '!ne']:
            if step[0] == '!jmp':
                ptr = step[1]
            elif step[0] == '!jne':
                if flag:
                    ptr = step[1]
            elif step[0] == '!je':
                if not flag:
                    ptr = step[1]
            elif step[0] == '!set':
                reg[step[1]] = step[2]
            elif step[0] == '!add':
                reg[step[1]] += reg[step[2]]
            elif step[0] == '!iadd':
                reg[step[1]] += step[2]
            elif step[0] == '!eq':
                flag = (reg[step[1]] == reg[step[2]])
            elif step[0] == '!ne':
                flag = (reg[step[1]] != reg[step[2]])
            continue

        cmd, frame, *args = step
        frm = get_frame(frame)
        if cmd == '!play':
            pulse = args[0]
            play(pulse, frm)
        else:
            frm.last_length = 0
            if cmd == '!delay':
                frm.time += args[0]
            elif cmd == '!add_phase':
                frm.phase += args[0]
            else:
                raise ValueError(f'Unknow command {cmd}')


################# 测试 #################

import matplotlib.pyplot as plt

run_prog(prog)

for name, ch in channels.items():
    plt.plot(ch.wav, '-', label=name)
plt.legend()
plt.show()
