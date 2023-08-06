from dataclasses import dataclass
import tempfile
import os
import uuid
import time
import machineid
import sys


@dataclass
class TmpFile:
    stdout_path: str
    stderr_path: str
    allocate_timestamp: int


class SessionManager:
    """SessionManager helps manage tmp files and session IDs"""

    def __init__(self):
        self.custom_tracking_id = None
        self.session_id = str(uuid.uuid4())
        self.machine_id = machineid.id()

    def set_custom_tracking_id(self, id: str):
        """ id is a string provided by users """
        self.custom_tracking_id = id

    def get_custom_tracking_id(self) -> str:
        """ if a custom is set, return it, otherwise None """
        return self.custom_tracking_id

    def get_machine_id(self) -> str:
        """a unique machine ID for tracking"""
        return self.machine_id

    def get_session_id(self) -> str:
        return self.session_id

    def get_new_tmp_file_paths(self) -> TmpFile:
        if sys.platform == "darwin":
            # hack: on Mac OS, $TMPDIR constantly gets root rename events
            # that don't work well with watchdog, so we explicitly set to /tmp
            tmpdir = "/tmp/"
        else:
            tmpdir = tempfile.gettempdir()

        return TmpFile(
            stderr_path=os.path.join(
                tmpdir, f"{self.session_id}_stderr.log"),
            stdout_path=os.path.join(
                tmpdir, f"{self.session_id}_stdout.log"),
            allocate_timestamp=time.time()
        )

    def should_switch_tmp_files(self, tmpfile: TmpFile):
        """ return true if you should switch tmp files"""
        # TODO
        return False
