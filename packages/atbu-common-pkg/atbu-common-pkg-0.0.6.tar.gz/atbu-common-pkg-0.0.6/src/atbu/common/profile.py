# Copyright 2022 Ashley R. Thomas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Python profile-related helpers.
"""

import io
import logging
import os
from pathlib import Path
from .exception import (
    InvalidFunctionArgument,
    InvalidStateError,
)

class EasyProfile:
    def __init__(self, log_stats: bool = True, profile_file: str = None) -> None:
        """An EasyProfiler manages starting/stopping a Python cProfile. Upon
        calling EasyProfile.stop, the profile stats will be either dumped to
        file and/or printed to the log file as an info message.

        Either log_stats must be True and/or profile_file must be a path to a file
        which does not already exist.

        Args:
            log_stats (bool, optional): If True, print profile stats to the log
                file upon calling the stop method. Defaults to True.
            profile_file (str, optional): If not None, dump the profile stats to
                a file which can be used later with pstats. Defaults to None.

        Raises:
            InvalidFunctionArgument: If the profile_file is specified and already exists.
        """
        if profile_file is not None:
            if not isinstance(profile_file, (str, Path)) or os.path.exists(profile_file):
                raise InvalidFunctionArgument(
                    f"The profile_file must not already exist: "
                    f"profile_file={profile_file}"
                )
        self.profile_file = profile_file
        self.log_stats = log_stats
        if not self.log_stats and self.profile_file is None:
            raise (
                f"Either one or both of log_stats and/or profile_file must be specified."
            )
        self.profiler = None
        self.is_used = False

    def start(self):
        if self.is_used:
            raise InvalidStateError(f"This {EasyProfile.__name__} has already been used.")
        # pylint: disable=import-outside-toplevel
        import cProfile
        logging.info(f"Activating profiler.")
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.is_used = True

    def stop(self):
        # pylint: disable=import-outside-toplevel
        try:
            if self.profiler is None:
                if self.is_used:
                    raise InvalidStateError(f"This profiler has already been stopped.")
                raise InvalidStateError(
                    f"This profiler has not been started yet or there was an error starting it."
                )
            logging.info(f"Disabling profiler.")
            self.profiler.disable()
            if self.profile_file is not None:
                logging.info(f"Writing profiler stats to {self.profile_file}")
                self.profiler.dump_stats(self.profile_file)
            if self.log_stats:
                import pstats
                logging.info(f"Printing profiler stats to the log.")
                s = io.StringIO()
                ps = pstats.Stats(self.profiler, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
                ps.print_stats()
                logging.info(s.getvalue())
        finally:
            self.profiler = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False
