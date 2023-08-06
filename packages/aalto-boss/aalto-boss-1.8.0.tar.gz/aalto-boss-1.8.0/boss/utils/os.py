import contextlib
import os
import shutil
from pathlib import Path

import numpy as np


def remove_boss_files():
    path = Path.cwd()
    for file_path in [path / "boss.in", path / "boss.out", path / "boss.rst"]:
        if file_path.exists():
            file_path.unlink()
    shutil.rmtree(path / "postprocessing", ignore_errors=True)


class execute_in(contextlib.ContextDecorator):
    def __init__(self, rundir):
        self.rundir = Path(rundir)
        self.origin = Path.cwd()
        super().__init__()

    def __enter__(self):
        os.chdir(self.rundir)

    def __exit__(self, *exc):
        os.chdir(self.origin)
