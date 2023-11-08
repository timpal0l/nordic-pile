import threading
import queue
from typing import Callable

QUEUE_SIZE = 10000
sentinel = object()


def _read_file(file_name, in_queue):
    with open(file_name, 'r') as f:
        for line in f:
            in_queue.put(line)
    in_queue.put(sentinel)


def _process_line(work_func, in_queue, out_queue):
    for line in iter(in_queue.get, sentinel):
        processed_line = work_func(line)
        out_queue.put(processed_line)

    out_queue.put(sentinel)


def _write_file(file_name, out_queue):
    with open(file_name, 'w') as f:
        for line in iter(out_queue.get, sentinel):
            f.write(line.strip() + "\n")


def read_work_write(in_file: str, out_file: str, work_func: Callable[[str], str]) -> None:
    """
    Uses 3 threads including the calling thread, to read a file line by line, do some work on the string, and write it
    to another file.

    :param in_file: file to read lines from
    :param out_file: file to write processed lines to
    :param work_func: function str -> str that will process lines one at a time
    """

    in_queue = queue.Queue(maxsize=QUEUE_SIZE)
    out_queue = queue.Queue(maxsize=QUEUE_SIZE)
    threading.Thread(target=_read_file, args=(in_file, in_queue)).start()
    threading.Thread(target=_process_line, args=(work_func, in_queue, out_queue)).start()
    _write_file(out_file, out_queue)
