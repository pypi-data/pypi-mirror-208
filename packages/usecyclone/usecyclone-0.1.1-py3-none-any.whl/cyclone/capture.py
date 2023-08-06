import os
import sys
import threading
import io
import signal
import functools

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from cyclone.session import SessionManager
from cyclone.networking import CycloneClient

API_KEY = "cyclone_test_key"


class FileAppendOnWriteHandler(FileSystemEventHandler):

    def __init__(self, output_file, watch_file, cyclone_client, source_name):
        """
        watch_file: opened file used for reading, will start from current position until the end
        output_file: write to output file
        """
        self.output_file = output_file
        self.watch_file = watch_file
        self.cyclone_client = cyclone_client
        self.source_name = source_name

    def on_modified(self, event):
        data = self.watch_file.read()
        self.output_file.write(data)
        # since output_file may be a char device, flush buffer after write
        self.output_file.flush()

        self.cyclone_client.send_cli(data, self.source_name)


def watch(watch_file_path, output_file, cyclone_client, source_name):
    """watch the watch_file_path and write output to output_file
    """
    watch_file = open(watch_file_path, 'r')

    # start from the end, in case the file is not empty
    watch_file.seek(0, io.SEEK_END)

    if sys.platform == "darwin":
        # use KqueueObserver instead of Fsevents (default for watchdog)
        # KqueueObserver provides more timely file system events
        from watchdog.observers.kqueue import KqueueObserver
        observer = KqueueObserver()
    else:
        observer = Observer()

    event_handler = FileAppendOnWriteHandler(
        output_file, watch_file, cyclone_client, source_name)

    # watchdog does not recognize symbolic links when recursive=False
    # this is a problem for Mac OS, where /tmp is linked to /private/tmp
    observer.schedule(event_handler, path=watch_file_path, recursive=True)

    observer.start()


def intercept_fd(fileno, tracked_output, cyclone_client, source_name):
    """start a thread that intercepts the file no and write to tracked_output, return 
    in a non-blocking way"""
    # create a backup of the fd
    original_fd = os.dup(fileno)
    # open a file to the original fd
    original = os.fdopen(original_fd, 'w')

    tracked_output_file = open(tracked_output, 'a+')

    watch(tracked_output, original, cyclone_client, source_name)

    # replace fd with the tracked file
    os.dup2(tracked_output_file.fileno(), fileno)


def capture_start(cyclone_client):
    # capture argv at program start
    cyclone_client.send_argv()


def spawn_start_up_thread(cyclone_client):
    """return a thread that captures basic os metadata"""
    thread = threading.Thread(target=capture_start, args=(cyclone_client,))
    thread.start()
    return thread


def captured_main(original_main, project_name=None):
    """captured_main will fork another process to run original_main
    original_main should have no argument

    the forked process will:
    1. have its stdout, stderr captured and sent to Cyclone backend

    Limitations:
    1. the new stdout / stderr will fail the isatty() check. That causes
    output highlight to be lost.
    2. it does not yet track stdin

    A proper fix to limit 1 is to use pseudo tty. That becomes much more
    involved than redirecting file descriptors.
    http://www.rkoucha.fr/tech_corner/pty_pdip.html
    """
    if project_name is None:
        project_name = sys.argv[0]

    session_manager = SessionManager()
    cyclone_client = CycloneClient(API_KEY, project_name, session_manager)

    start_thread = spawn_start_up_thread(cyclone_client)

    def sigint_handler(sig, frame):
        cyclone_client.send_signal("SIGINT")
        raise KeyboardInterrupt()

    signal.signal(signal.SIGINT, sigint_handler)

    tmp_file = session_manager.get_new_tmp_file_paths()
    intercept_fd(
        sys.stdout.fileno(), tmp_file.stdout_path, cyclone_client, "stdout")
    intercept_fd(
        sys.stderr.fileno(), tmp_file.stderr_path, cyclone_client, "stderr")

    try:
        original_main()
    finally:
        start_thread.join()

        try:
            os.remove(tmp_file.stdout_path)
            os.remove(tmp_file.stderr_path)
        except Exception:
            # don't throw anything during exit
            pass


def capture(project_name=None):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return captured_main(lambda: func(*args, **kwargs), project_name=project_name)
        return wrapper
    return actual_decorator
