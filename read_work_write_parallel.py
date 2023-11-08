import multiprocessing
import queue
import threading
from collections import defaultdict
from functools import partial
from typing import Callable, Dict, Tuple, List
import fasttext
from transformers import GPT2TokenizerFast

QUEUE_SIZE = 100000
sentinel = object()

# Keep track of filter removal counters
counter_dict = defaultdict(int)
doc_count = 0
kept_count = 0


def init_process():
    """
    Initializes structures for the process, called when multiprocessing workers are spawned
    """
    # global lang_det, tokenizer
    global lang_det

    # Supress the harmless warnings and load the model
    fasttext.FastText.eprint = lambda x: None
    lang_det = fasttext.load_model("lid.176.bin")

    # load different tokenizers
    # tok_en = transformers.GPT2TokenizerFast.from_pretrained('gpt2')
    # tokenizer_name = "gpt2"
    # tokenizer_name = "tokenizer_gptswe"

    # tokenizer_name = "tokenizer_gptneox"
    # tokenizer = GPT2TokenizerFast.from_pretrained(tokenizer_name)
    # tokenizer.model_max_length = 10 ** 6


def _read_file(file_name, in_queue):
    """
    Reads a file line by line and adds it to the queue

    :param file_name: input file
    :param in_queue: multithreading queue to which the read lines are added
    """
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip(' \n')
            if len(line) > 0:
                in_queue.put((file_name, line))
    in_queue.put(sentinel)


def _process_line_job(line, work_func):
    """
    Dummy func which is probably not needed

    :param line: line to process by workers
    :param work_func: function that processes line
    :return: the processed line
    """
    return work_func(line)


def _process_line(work_func, in_queue, out_queue, num_workers):
    """
    Spawns multiprocessing workers with a pool, iterates over the input queue, processes lines with workers,
    and writes the processed lines to the output queue

    :param work_func: function that processes lines
    :param in_queue: input queue which holds lines from the input file
    :param out_queue: output queue in which processed lines are added
    :param num_workers: number of multiprocessing CPU workers to use
    """

    global doc_count, kept_count
    pool = multiprocessing.Pool(num_workers, initializer=init_process)

    job_partial = partial(_process_line_job, work_func=work_func)
    result_iter = pool.imap(job_partial, iter(in_queue.get, sentinel), chunksize=128)

    for processed_line, filter_indices in result_iter:

        doc_count += 1
        for filter_idx in filter_indices:
            counter_dict[filter_idx] += 1

        keep_doc = len(filter_indices) == 0
        if keep_doc:
            kept_count += 1

        out_queue.put(processed_line)

    pool.close()
    pool.join()

    out_queue.put(sentinel)


def _write_file(file_name, out_queue):
    """
    Reads lines from the output queue and writes them to file

    :param file_name: output file
    :param out_queue: queue of processed lines to read from
    """

    documents_processed = 0
    first_written = False

    with open(file_name, 'w') as f:
        for processed_line in iter(out_queue.get, sentinel):
            if first_written:
                f.write("\n")
            else:
                first_written = True

            f.write(processed_line)

            documents_processed += 1
            if documents_processed % 100000 == 0:
                print(f"#Documents Processed: {documents_processed}")


def read_work_write(in_file: str, out_file: str, work_func: Callable[[str], Tuple[str, List[int]]], num_workers: int
                    ) -> Tuple[int, int, Dict[int, int]]:
    """
    Uses 3 threads including the calling thread, to read a file line by line, do some work on the string, and write it
    to another file.

    :param in_file: file to read lines from
    :param out_file: file to write processed lines to
    :param work_func: function str -> (str, list(int)) that will process lines one at a time
    :param num_workers: number of CPU workers for processing lines
    """

    print("Processing...")
    in_queue = queue.Queue(maxsize=QUEUE_SIZE)
    out_queue = queue.Queue(maxsize=QUEUE_SIZE)
    threading.Thread(target=_read_file, args=(in_file, in_queue)).start()
    threading.Thread(target=_process_line, args=(work_func, in_queue, out_queue, num_workers)).start()
    _write_file(out_file, out_queue)

    return doc_count, kept_count, dict(counter_dict)
