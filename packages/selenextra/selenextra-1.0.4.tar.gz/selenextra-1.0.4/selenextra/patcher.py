from undetected_chromedriver.patcher import Patcher

import string
import random
import re
import io


class CustomPatcher(Patcher):
    def __init__(self, executable_path=None, force=False, version_main: int = 0, user_multi_procs=False):
        super().__init__(executable_path, force, version_main, user_multi_procs)

    @staticmethod
    def gen_random_cdc() -> bytes:
        cdc = random.choices(string.ascii_lowercase, k=26)
        cdc[-6:-4] = map(str.upper, cdc[-6:-4])
        cdc[2] = cdc[0]
        cdc[3] = "_"

        return "".join(cdc).encode()

    def patch_exe(self) -> None:
        super().patch_exe()

        replacement = self.gen_random_cdc()

        with io.open(self.executable_path, "r+b") as fh:
            for line in iter(lambda: fh.readline(), b""):
                if not b"cdc_" in line:
                    continue

                fh.seek(-len(line), 1)
                newline = re.sub(b"cdc_.{22}", replacement, line)
                fh.write(newline)
