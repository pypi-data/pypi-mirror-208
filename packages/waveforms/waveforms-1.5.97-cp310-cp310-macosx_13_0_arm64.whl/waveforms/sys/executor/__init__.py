import logging
import queue
import re
import threading
import warnings
from abc import ABC, ABCMeta, abstractmethod
from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, NamedTuple

from qlisp import COMMAND, NOTSET, READ, SYNC, TRIG, WRITE, get_arch
from waveforms.waveform_parser import wave_eval

from waveforms.qlisp.arch.basic.config import LocalConfig

log = logging.getLogger(__name__)


class Executor(ABC):
    """
    Base class for executors.
    """

    @property
    def log(self):
        return logging.getLogger(
            f"{self.__module__}.{self.__class__.__name__}")

    @abstractmethod
    def feed(self, priority: int, task_id: int, step_id: int,
             cmds: list[COMMAND]):
        pass

    @abstractmethod
    def fetch(self, task_id: int, skip: int = 0) -> list:
        pass

    @abstractmethod
    def free(self, task_id: int):
        pass

    @abstractmethod
    def boot(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass

    @abstractmethod
    def reset(self):
        pass


class FakeExecutor(Executor):

    def __init__(self, config={}, **kwds):
        from queue import Queue

        self._cfg = LocalConfig(config)
        self._queue = Queue()
        self._buff = {}

        self._state_caches = {}

        self._cancel_evt = threading.Event()
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        self.thread_pool = ThreadPoolExecutor()

    def run(self):
        from collections import defaultdict

        import numpy as np

        sampleRate = 1e9

        while True:
            if self._cancel_evt.is_set():
                while not self._queue.empty():
                    self._queue.get()
                self._cancel_evt.clear()
            task_id, task_step, cmds, extra, next_feed_time = self._queue.get()
            if task_step < 0:
                if task_id in self._buff:
                    self._buff[task_id]['state'] = 'finished'
                continue
            read_config = defaultdict(lambda: {
                'shots': 1024,
                'fnum': 1,
                'numberOfPoints': 1024
            })
            dataframe = {}

            for cmd in cmds:
                ch = '.'.join(cmd.address.split('.')[:-1])
                if isinstance(cmd, WRITE):
                    if cmd.address.endswith('.Coefficient'):
                        start, stop = cmd.value['start'], cmd.value['stop']
                        fnum = len(cmd.value['wList'])
                        read_config[ch]['start'] = start
                        read_config[ch]['stop'] = stop
                        read_config[ch]['fnum'] = fnum
                        numberOfPoints = int((stop - start) * sampleRate)
                        if numberOfPoints % 1024 != 0:
                            numberOfPoints = numberOfPoints + 1024 - numberOfPoints % 1024
                        read_config[ch]['numberOfPoints'] = numberOfPoints
                    elif cmd.address.endswith('.Shot'):
                        shots = cmd.value
                        read_config[ch]['shots'] = shots
                elif isinstance(cmd, READ):
                    if cmd.address.endswith('.IQ'):
                        shape = (read_config[ch]['shots'],
                                 read_config[ch]['fnum'])
                        dataframe['READ.' +
                                  cmd.address] = (np.random.randn(*shape),
                                                  np.random.randn(*shape))
                    elif cmd.address.endswith('.TraceIQ'):
                        shape = (read_config[ch]['shots'],
                                 read_config[ch]['numberOfPoints'])
                        dataframe['READ.' +
                                  cmd.address] = (np.random.randn(*shape),
                                                  np.random.randn(*shape))
                    else:
                        dataframe['READ.' +
                                  cmd.address] = np.random.randn(1000)
            data_map = extra['dataMap']
            dataframe = get_arch(data_map['arch']).assembly_data(
                dataframe, data_map)

            import time
            time.sleep(0.001)

            if task_id in self._buff:
                self._buff[task_id]['data'].append(dataframe)

    @property
    def cfg(self):
        return self._cfg

    def boot(self):
        pass

    def shutdown(self):
        pass

    def reset(self):
        pass

    def create_task(self, task_id: int, meta: dict = {}):
        self._buff[task_id] = {'state': 'init', 'data': []}

    def start(self, *args):
        pass

    def feed(self,
             task_id: int,
             task_step: int,
             cmds: list[COMMAND],
             extra: dict = {},
             next_feed_time=0):
        self._queue.put((task_id, task_step, cmds, extra, next_feed_time))
        return True

    def free(self, task_id: int) -> None:
        try:
            self._buff.pop(task_id)
        except:
            pass

    def free_all(self) -> None:
        self._buff.clear()

    def fetch(self, task_id: int, skip: int = 0) -> list:
        """get results of task

        Args:
            task_id (int): uuid of task
            skip (int, optional): skip. Defaults to 0.

        Returns:
            list: list of results.
        """
        if task_id not in self._buff:
            return []
        ret = self._buff[task_id]['data'][skip:]
        if len(ret) == 0 and self._buff[task_id]['state'] == 'finished':
            self._buff.pop(task_id)
        return ret

    def save(self, task_id: int, path: str, index: dict) -> None:
        pass

    def cancel(self) -> None:
        self._cancel_evt.set()

