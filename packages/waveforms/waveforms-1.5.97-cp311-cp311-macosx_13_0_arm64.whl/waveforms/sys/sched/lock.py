import os
import pathlib

import portalocker


class SchedLock():
    def __init__(self):
        self.lockfile = pathlib.Path(os.environ['SCHED_LOCKFILE'])
        self.lockfile.parent.mkdir(parents=True, exist_ok=True)
        self.lockfile.touch(exist_ok=True)

    def aquire(self):
        with portalocker.Lock(self.lockfile, 'rb+', timeout=60) as fh:
            fh.seek(0)
            fh.write(b'1')
            fh.flush()
            os.fsync(fh.fileno())

    def release(self):
        portalocker.unlock(self.lockfile)
        self.lockfile.close()

    def __enter__(self):
        self.aquire()

    def __exit__(self, *args):
        self.release()