#  Copyright (c) 2020 Netflix.
#  All rights reserved.
#
from pathlib import Path
from typing import Optional
from typing import Text

# Implementation libs
from ntscli_cloud_lib.sslconfig import SslConfig


class SslConfigManager:
    path: Path = Path("~/.config/netflix")

    def __init__(self):
        self.dir = Path(self.path).expanduser()

    def __sizeof__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return self.dir.exists()

    def __iter__(self):
        return self.dir.iterdir()

    def exists(self):  # todo __bool__ ?
        return self.dir.exists()

    def has(self, name: Text) -> bool:  # todo __includes__?
        return (self.dir / name).exists()

    def get(self, name: Text) -> Optional[SslConfig]:
        return SslConfig(str(self.dir / name))
