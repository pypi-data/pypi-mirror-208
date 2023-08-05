from __future__ import annotations

import asyncio
import copy
import functools
import hashlib
import importlib
import inspect
import logging
import pickle
import sys
import threading
import time
from abc import ABC, abstractmethod
from collections import deque
from concurrent.futures import Future
from dataclasses import dataclass, field
from functools import cached_property
from typing import (Any, Generator, Iterable, Literal, NamedTuple, Optional,
                    Sequence, Type, Union)

import blinker
import numpy as np
from qlisp import READ, WRITE, Config, Library, ProgramFrame
from waveforms.qlisp import (NOTSET, READ, TRIG, WRITE, Config, ConfigProxy,
                             Library, Signal, get_arch, libraries)
from waveforms.qlisp.arch import Architecture
from waveforms.qlisp.arch.basic.config import LocalConfig
from waveforms.qlisp.libs import std
from waveforms.qlisp.prog import Program
from waveforms.scan_iter import Begin, End, StepStatus, Storage, scan_iters
from waveforms.waveform import Waveform

from ..ipy_events import get_current_cell_id
from ..progress import JupyterProgressBar, Progress
from ..storage.crud import tag_it
from ..storage.models import Record, Report, Session, User

log = logging.getLogger(__name__)

__libs = [std]


def set_library(*libs: tuple[Library]) -> None:
    """Set the library for the current session."""
    __libs.clear()
    __libs.extend(libs)
    __libs.append(std)


def get_library() -> Library:
    return libraries(*__libs)


@dataclass
class CalibrationResult():
    suggested_calibration_level: int = 0
    parameters: dict = field(default_factory=dict)
    info: dict = field(default_factory=dict)


@dataclass
class DataFrame():
    pass


class AnalyzeResult(NamedTuple):
    """
    Result of the analysis.
    """
    score: int = 0
    # how good is the result
    # 100 is perfect
    # 0 implied full calibration is required
    # and negative is bad data

    parameters: dict = {}
    # new values of the parameters from the analysis
    # only required for 100 score

    tags: set[str] = set()

    status: str = 'not analyzed'
    message: str = ''


SIGNAL = Literal['trace', 'iq', 'state', 'count', 'diag', 'population',
                 'trace_avg', 'iq_avg']
QLisp = list[tuple]
TASKSTATUS = Literal['not submited', 'pending', 'compiling', 'submiting',
                     'running', 'finished', 'cancelled', 'failed']


def _form_signal(sig):
    sig_tab = {
        'trace': Signal.trace,
        'iq': Signal.iq,
        'state': Signal.state,
        'count': Signal.count,
        'diag': Signal.diag,
        'population': Signal.population,
        'trace_avg': Signal.trace_avg,
        'iq_avg': Signal.iq_avg
    }
    if isinstance(sig, str):
        if sig == 'raw':
            sig = 'iq'
        try:
            return sig_tab[sig]
        except KeyError:
            pass
    elif isinstance(sig, Signal):
        return sig
    raise ValueError(f'unknow type of signal "{sig}".'
                     f" optional signal types: {list(sig_tab.keys())}")


class TagSet(set):
    updated = blinker.signal('updated')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, tag: str):
        if tag in self:
            return
        super().add(tag)
        self.updated.send(self, tag_text=tag)

    def __repr__(self) -> str:
        return super().__repr__()


def update_tags(sender: TagSet, tag_text, obj: Any, tag_set_id, db) -> None:
    if id(sender) == tag_set_id:
        tag_it(db, tag_text, obj)


@dataclass
class TaskRuntime():
    priority: int = 0  # Priority of the task
    daemon: bool = False  # Is the task a daemon
    at: float = -1  # Time at which the task is scheduled
    period: float = -1  # Period of the task

    status: TASKSTATUS = 'not submited'
    id: int = -1
    created_time: float = field(default_factory=time.time)
    started_time: float = field(default_factory=time.time)
    finished_time: float = field(default=-1)
    kernel: object = None
    db: Session = None
    user: User = None

    prog: Program = field(default_factory=Program)
    arch: Architecture = None

    #################################################
    compiled_step: int = 0
    finished_step: int = 0
    sub_index: int = 0
    cmds: list = field(default_factory=list)
    skip_compile: bool = False
    storage: Storage = field(default_factory=Storage)
    record: Optional[Record] = None
    system_info: dict = field(default_factory=dict)
    keep_last_status: bool = False
    dry_run: bool = False

    progress: Progress = field(default_factory=Progress)

    threads: dict = field(default_factory=dict)
    _status_lock: threading.Lock = field(default_factory=threading.Lock)
    _kill_event: threading.Event = None

    used_elements: set = field(default_factory=set)


@functools.total_ordering
class Task(ABC):

    def __init__(self,
                 signal: Union[SIGNAL, Signal] = Signal.state,
                 shots: int = 1024,
                 calibration_level: int = 0,
                 arch: str = 'baqis'):
        """
        Args:
            signal: the signal to be measured
            shots: the number of shots to be measured
            calibration_level: calibration level (0~100)
        """
        self.__runtime = TaskRuntime()
        self.parent = None
        self.container = None
        self.signal = signal
        self.shots = shots
        self.calibration_level = calibration_level
        self.no_record = False
        self.reshape_record = False
        self.debug_mode = False
        self._tags: set = TagSet()
        self.__cfg = None
        self.__runtime.arch = get_arch(arch)

    @abstractmethod
    def scan_range(self):
        pass

    @abstractmethod
    def main(self):
        pass

    @abstractmethod
    def analyze(self, result) -> AnalyzeResult:
        pass

    @property
    def priority(self):
        return self.__runtime.priority

    @property
    def id(self):
        return self.__runtime.id

    @property
    def name(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    @property
    def log(self):
        return logging.getLogger(f"{self.name}")

    @property
    def kernel(self):
        from waveforms.sys.sched import main_loop
        return main_loop

    @property
    def meta_info(self):
        return self.__runtime.prog.meta_info

    @property
    def runtime(self):
        return self.__runtime

    @property
    def status(self):
        return self.__runtime.status

    def __deepcopy__(self, memo):
        memo[id(self.__runtime)] = TaskRuntime(
            arch=self.__runtime.arch,
            prog=self.__runtime.prog,
            used_elements=self.__runtime.used_elements)
        ret = copy.copy(self)
        for attr, value in self.__dict__.items():
            setattr(ret, attr, copy.deepcopy(value, memo))
        return ret

    def __lt__(self, other: Task):
        return ((self.runtime.at, self.priority, self.runtime.created_time) <
                (self.runtime.at, other.priority, other.runtime.created_time))

    @property
    def signal(self):
        return self.__signal

    @signal.setter
    def signal(self, sig: Union[SIGNAL, Signal]):
        self.__signal = _form_signal(sig)

    def __repr__(self):
        try:
            return f"{self.name}({self.id}, calibration_level={self.calibration_level}, record_id={self.runtime.record.id})"
        except:
            return f"{self.name}({self.id}, calibration_level={self.calibration_level})"

    @property
    def db(self):
        if self.runtime.db is None:
            self.runtime.db = self.kernel.session()
        return self.runtime.db

    @property
    def cfg(self):
        if self.__cfg is None:
            self.__cfg = LocalConfig(copy.deepcopy(self.runtime.prog.snapshot))
            self.__cfg._history = LocalConfig(self.runtime.prog.snapshot)
        return self.__cfg

    @property
    def tags(self):
        return self._tags

    @property
    def record(self) -> Optional[Record]:
        return self.runtime.record

    @cached_property
    def task_hash(self):
        kwds = self.runtime.prog.task_arguments
        kwds = {k: kwds[k] for k in sorted(kwds.keys())}
        buf = pickle.dumps(kwds)
        return hashlib.sha256(buf).digest()

    def is_children_of(self, task: Task) -> bool:
        return self.parent is not None and self.parent == task.id

    def get_parent(self) -> Optional[Task]:
        if self.parent is not None:
            return self.kernel.get_task_by_id(self.parent)
        return None

    def set_record(self, dims: list[tuple[str, str]], vars: list[tuple[str,
                                                                       str]],
                   coords: dict[str, Sequence]) -> None:

        if self.no_record:
            return
        if self.runtime.record is not None:
            return
        dims, dims_units = list(zip(*dims))
        vars, vars_units = list(zip(*vars))
        self.runtime.record = self.create_record()
        self.db.add(self.runtime.record)
        self.db.commit()

    def create_record(self, db=None) -> Record:
        """Create a record"""
        from ..storage.models import get_data_path

        if db is None:
            db = self.db

        file, key = self.data_path.split(':/')
        file = get_data_path() / (file + '.hdf5')

        record = Record(file=str(file), key=key)
        record.app = self.name
        record.task_hash = self.task_hash
        record.cell_id = get_current_cell_id()
        if self.parent is not None:
            record.parent_id = self.kernel.get_task_by_id(
                self.parent).runtime.record.id
        for tag_text in self.tags:
            tag_it(db, tag_text, record)

        receiver = functools.partial(update_tags,
                                     obj=record,
                                     db=self.db,
                                     tag_set_id=id(self.tags))
        self.tags.updated.connect(receiver)
        record._blinker_update_tag_receiver = receiver  # hold a reference
        return record

    def create_report(self, db=None) -> Report:
        """create a report"""
        from ..storage.models import get_data_path

        if db is None:
            db = self.db

        file, key = self.data_path.split(':/')
        file = get_data_path() / (file + '.hdf5')

        rp = Report(file=str(file), key=key)
        rp.task_hash = self.task_hash
        for tag_text in self.tags:
            tag_it(db, tag_text, rp)

        receiver = functools.partial(update_tags,
                                     obj=rp,
                                     db=self.db,
                                     tag_set_id=id(self.tags))
        self.tags.updated.connect(receiver)
        rp._blinker_update_tag_receiver = receiver  # hold a reference
        return rp

    def set(self, key: str, value: Any, cache: bool = True) -> None:
        self.runtime.cmds.append(WRITE(key, value))
        self.cfg.update(key, value, cache=cache)

    def get(self, key: str, default: Any = NOTSET) -> Any:
        """
        return the value of the key in the kernel config
        """
        ret = self.cfg.query(key)
        if isinstance(ret, tuple) and ret[0] is NOTSET:
            if default is NOTSET:
                raise KeyError(f"key {key} not found")
            return default
        return ret

    def push(self, frame: dict):
        if 'data' not in frame:
            self.runtime.result['data'].append(None)
        for k, v in frame['data'].items():
            self.runtime.result[k].append(v)

    def exec(self,
             circuit: QLisp,
             lib: Optional[Library] = None,
             cfg: Union[Config, ConfigProxy, None] = None,
             skip_compile: bool = False):

        if lib is None:
            lib = get_library()
        if cfg is None:
            cfg = self.cfg

        self._collect_used_elements(circuit)
        return exec_circuit(self,
                            circuit,
                            lib=lib,
                            cfg=cfg,
                            signal=self.signal,
                            skip_compile=skip_compile)

    def flush(self):
        flush_task(self)

    def _collect_used_elements(self, circuit: QLisp) -> None:
        all_qubits = self.cfg._getAllQubitLabels()
        for _, qubits in circuit:
            if not isinstance(qubits, tuple):
                qubits = (qubits, )
            for qubit in qubits:
                if qubit not in all_qubits:
                    raise ValueError(f"{qubit} is not in the config, "
                                     f"please add it to the config")
                # self.tags.add(qubit)
                self.runtime.used_elements.add(qubit)
                q = self.cfg.query(qubit)
                try:
                    self.runtime.used_elements.add(q['probe'])
                except:
                    pass
                try:
                    for coupler in q['couplers']:
                        self.runtime.used_elements.add(coupler)
                except:
                    pass

    def measure(self, keys, labels=None):
        if labels is None:
            labels = keys
        dataMap = {'data': {label: key for key, label in zip(keys, labels)}}
        self.runtime.prog.data_maps[-1].update(dataMap)
        self.runtime.cmds.extend([READ(key) for key in keys])

    def trig(self) -> None:
        cmds = self.get('station.triggercmds')
        for cmd in cmds:
            self.runtime.cmds.append(TRIG(cmd))

    def scan(self) -> Generator:
        self.set_record(dims=[('index', ''), ('shots', ''), ('cbits', '')],
                        vars=[('data', ''), ('state', '')],
                        coords={
                            'shots': np.arange(self.shots),
                        })

        yield from expand_task(self)
        with self.runtime._status_lock:
            if self.status == 'compiling':
                self.runtime.status = 'pending'

    @cached_property
    def data_path(self) -> str:
        if self.parent:
            name = '/'.join([
                self.kernel.get_task_by_id(self.parent).data_path, 'sub_data',
                f"{self.name}_{self.runtime.sub_index}"
            ])
            return name
        else:
            file_name = self.get('station.sample')
            time_str = time.strftime('%Y-%m-%d-%H-%M-%S',
                                     time.localtime(self.runtime.started_time))
            name = f"{self.name}"
            return f"{file_name}:/{name}"

    def clean_side_effects(self) -> None:
        self.kernel.clean_side_effects(self, self.kernel.get_executor(), False)

    def depends(self) -> list[tuple[str, tuple, dict]]:
        """
        """
        return []

    def check(self, lastest: bool = False) -> bool:
        """
        If the latest scan was finished sucessfully in life time,
        then return the finished time, otherwise return -1
        """
        raise NotImplementedError()

    def analyze(self, data) -> CalibrationResult:
        """
        return a CalibrationResult object
        """
        raise NotImplementedError()

    def result(self, reshape: bool = False, skip=None) -> dict:
        self.kernel._fetch_data(self, self.kernel.get_executor())
        try:
            record_id = self.record.id
        except:
            record_id = None
        ret = {
            'calibration_level': self.calibration_level,
            'index': {},
            'meta': {
                'id': record_id,
                'pos': {},
                'iteration': {},
                'reshaped': reshape,
                'system': self.runtime.system_info,
            }
        }

        if skip is None or skip == 0:
            for key in self.runtime.storage._frozen_keys:
                ret['index'][key] = self.runtime.storage[key]
            ret['meta']['key_levels'] = self.runtime.storage._key_levels
            ret['meta']['pos'] = self.runtime.storage.pos
            ret['meta']['iteration'] = self.runtime.storage.iteration
            ret['meta']['arguments'] = self.runtime.prog.task_arguments
            ret['meta']['config'] = self.runtime.prog.snapshot
        ret['meta']['shape'] = self.runtime.storage.shape

        for key in self.runtime.storage.storage:
            if key not in self.runtime.storage._frozen_keys:
                if reshape:
                    ret[key] = self.runtime.storage[key]
                elif skip is None:
                    data, *_ = self.runtime.storage.get(key, skip=0)
                    ret[key] = np.asarray(data)
                else:
                    data, iteration, pos = self.runtime.storage.get(key,
                                                                    skip=skip)
                    ret['meta']['pos'][key] = pos
                    ret['meta']['iteration'][key] = iteration
                    ret[key] = data
        return ret

    def cancel(self):
        for fut, evt in self.runtime.threads.values():
            evt.set()
        self.runtime.progress.finish(False)
        self.kernel.get_executor().cancel()
        with self.runtime._status_lock:
            self.runtime.status = 'cancelled'

    def join(self, timeout=None):
        try:
            if timeout is None:
                while 'compile' not in self.runtime.threads:
                    time.sleep(0.1)
                self.runtime.threads['compile'][0].result()
                if self.runtime.dry_run:
                    return
                while 'run' not in self.runtime.threads:
                    time.sleep(0.1)
                self.runtime.threads['run'][0].result()
            else:
                start = time.time()
                while 'compile' not in self.runtime.threads:
                    used = time.time() - start
                    if used > timeout:
                        raise TimeoutError(f"timeout {timeout}")
                    time.sleep(0.1)
                used = time.time() - start
                self.runtime.threads['compile'][0].result(
                    max(timeout - used, 0.001))
                if self.runtime.dry_run:
                    return
                while 'run' not in self.runtime.threads:
                    used = time.time() - start
                    if used > timeout:
                        raise TimeoutError(f"timeout {timeout}")
                    time.sleep(0.1)
                used = time.time() - start
                self.runtime.threads['run'][0].result(
                    max(timeout - used, 0.001))
        finally:
            for fut, evt in self.runtime.threads.values():
                evt.set()

    def bar(self):
        bar = JupyterProgressBar(description=self.name.split('.')[-1])
        bar.listen(self.runtime.progress)
        bar.display()

    def check_level(self) -> int:
        return 90


class App(Task):

    def plot(self, fig, result):
        raise NotImplementedError()


class UserInput(App):

    def __init__(self, *keys):
        super().__init__()
        self.elements = None
        self.keys = keys
        self.no_record = True

    @property
    def name(self):
        return 'UserInput'

    def check(self):
        # never pass
        return -1

    def analyze(self, data) -> CalibrationResult:
        # always pass
        return CalibrationResult(suggested_calibration_level=100)

    def scan_range(self) -> Union[Iterable, Generator]:
        return {}

    def main(self):
        for key in self.keys:
            self.set(key, input(f"{key} = "), cache=False)

    def result(self):
        return {'data': []}


class CalibrateGate(App):

    def __init__(self, gate_name, qubits, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gate_name = gate_name
        self.qubits = qubits

    @property
    def name(self):
        return 'CalibrateGate'

    def check(self):
        # never pass
        return -1

    def analyze(self, data) -> CalibrationResult:
        # always pass
        return CalibrationResult(suggested_calibration_level=100)

    def scan_range(self) -> Union[Iterable, Generator]:
        return {}

    def main(self):
        pass

    def result(self):
        return {'data': []}


class RunCircuits(App):

    def __init__(self,
                 circuits,
                 shots=1024,
                 signal='state',
                 arch='baqis',
                 lib=None,
                 cfg=None,
                 settings=None,
                 cmds=[],
                 calibration_mode=False):
        super().__init__(signal=signal, shots=shots, arch=arch)
        self.circuits = circuits
        self.custom_lib = lib
        self.custom_cfg = cfg
        self.cmds = cmds
        self.settings = settings
        self.calibration_mode = calibration_mode

    @property
    def name(self):
        return 'RunCircuits'

    def depends(self) -> list[tuple[str, tuple, dict]]:
        from waveforms import compile
        from waveforms.quantum.circuit.qlisp.qlisp import gateName

        if self.calibration_mode:
            return []

        deps = set()

        for circuit in self.circuits:
            for st in compile(circuit,
                              no_link=True,
                              lib=self.custom_lib,
                              cfg=self.custom_cfg):
                deps.add((CalibrateGate, (gateName(st), st[1])))

        return list(deps)

    def check(self):
        # never pass
        return -1

    def analyze(self, data) -> CalibrationResult:
        # always pass
        return CalibrationResult(suggested_calibration_level=100)

    def scan_range(self):
        ret = {'iters': {'circuit': self.circuits}}
        if self.settings is not None:
            if isinstance(self.settings, dict):
                ret['iters']['settings'] = [self.settings] * len(self.circuits)
            else:
                ret['iters']['settings'] = self.settings
        return ret

    def main(self):
        for step in self.scan():
            self.runtime.cmds.extend(self.cmds)
            for k, v in step.kwds.get('settings', {}).items():
                self.set(k, v)
            self.exec(step.kwds['circuit'],
                      lib=self.custom_lib,
                      cfg=self.custom_cfg)


def _getAppClass(name: str) -> Type[App]:
    *module, name = name.split('.')
    if name in ['RunCircuits', 'CalibrateGate', 'UserInput']:
        return globals()[name]
    elif len(module) == 0:
        module = sys.modules['__main__']
    else:
        module = '.'.join(module)
        module = importlib.import_module(module)
    return getattr(module, name)


def create_task(taskInfo: Union[tuple, Task]) -> Task:
    """
    create a task from a string or a class

    Args:
        taskInfo: a task or tuple of (app, [args, [kargs,]])

            app: a string or a subclass of Task
            args: arguments for the class
            kwds: keyword arguments for the class

    Returns:
        a task
    """
    if isinstance(taskInfo, Task):
        return copy_task(taskInfo)

    app, *other = taskInfo
    if isinstance(app, str):
        app_cls = _getAppClass(app)
    if len(other) >= 1:
        args = other[0]
    else:
        args = ()
    if len(other) >= 2:
        kwds = other[1]
    else:
        kwds = {}
    app = app_cls(*args, **kwds)
    bs = inspect.signature(app_cls).bind(*args, **kwds)
    task = app
    task.runtime.prog.task_arguments = bs.arguments
    task.runtime.prog.meta_info['arguments'] = bs.arguments
    return task


def copy_task(task: Task) -> Task:
    memo = {
        id(task.parent): None,
        id(task.container): None,
    }
    return copy.deepcopy(task, memo)


def create_future(task: Task, step: int) -> Union[asyncio.Future, Future]:
    try:
        return asyncio.get_running_loop().create_future()
    except:

        return Future()


def exec_circuit(task: Task,
                 circuit: Union[str, list],
                 lib: Library,
                 cfg: Config,
                 signal: str,
                 skip_compile: bool = False) -> int:
    """Execute a circuit."""
    from waveforms import compile

    if skip_compile and task.runtime.compiled_step > 0:
        task.runtime.skip_compile = True
        for cmd in task.runtime.prog.steps[-2].cmds:
            if (isinstance(cmd, READ) or cmd.address.endswith('.StartCapture')
                    or cmd.address.endswith('.CaptureMode')):
                task.runtime.cmds.append(cmd)
        task.runtime.prog.steps[-1].data_map = task.runtime.prog.steps[
            -2].data_map
    else:
        task.runtime.skip_compile = False
        code = compile(circuit, lib=lib, cfg=cfg)
        code.signal = signal
        code.shots = task.shots
        cmds, dataMap = task.runtime.arch.assembly_code(code)
        task.runtime.prog.steps[-1].code = code
        task.runtime.prog.steps[-1].data_map.update(dataMap)
        task.runtime.cmds.extend(cmds)
    return task.runtime.prog.steps[-1].fut


def expand_task(task: Task):
    task.runtime.compiled_step = 0
    task.runtime.finished_step = 0
    task.runtime.prog.side_effects = {}
    task.runtime.prog.steps = []
    task.runtime.prog.shots = task.shots
    task.runtime.prog.signal = task.signal

    kw = task.scan_range()
    kw['trackers'] = kw.get('trackers', [])
    kw['trackers'].append(task.runtime.storage)

    for step in scan_iters(**kw):
        try:
            if task.runtime._kill_event.is_set():
                break
        except AttributeError:
            pass

        if isinstance(step, StepStatus):
            task.runtime.prog.steps.append(ProgramFrame(step, fut=Future()))
            task.runtime.cmds = []
        yield step
        if isinstance(step, StepStatus):
            flush_task(task)


def flush_task(task):
    from waveforms import Waveform

    if len(task.runtime.prog.steps[-1].cmds) > 0:
        return

    task.trig()
    task.runtime.prog.steps[-1].cmds = task.runtime.cmds

    unused = list(task.runtime.prog.side_effects.keys())
    for cmd in task.runtime.cmds:
        if isinstance(cmd.value, Waveform):
            task.runtime.prog.side_effects.setdefault(cmd.address, 'zero()')
        else:
            task.runtime.prog.side_effects.setdefault(
                cmd.address, task.cfg._history.query(cmd.address))
        try:
            unused.remove(cmd.address)
        except ValueError:
            pass
    if not task.runtime.skip_compile:
        for addr in unused:
            if isinstance(
                    task.runtime.prog.side_effects[addr],
                    str) and task.runtime.prog.side_effects[addr] == 'zero()':
                task.runtime.prog.steps[-1].cmds.insert(
                    0, WRITE(addr, 'zero()'))
                task.runtime.prog.side_effects.pop(addr)

    task.runtime.compiled_step += 1
    task.runtime.progress.max = task.runtime.compiled_step
    time.sleep(0.001)
