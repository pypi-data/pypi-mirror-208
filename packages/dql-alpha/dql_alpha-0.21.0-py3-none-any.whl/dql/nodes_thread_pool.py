import concurrent
import concurrent.futures
import threading
from abc import ABC, abstractmethod

from tqdm import tqdm


class NodeChunk:
    def __init__(self, nodes, size_limit=10 * 1024 * 1024, file_limit=100):
        self.nodes = nodes
        self.size_limit = size_limit
        self.file_limit = file_limit

    def __iter__(self):
        return self

    def next_downloadable(self):
        node = next(self.nodes, None)
        while node and not node.is_downloadable:
            node = next(self.nodes, None)
        return node

    def __next__(self):
        node = self.next_downloadable()

        total_size = 0
        total_files = 0
        bucket = []

        while (
            node
            and total_size + node.size < self.size_limit
            and total_files + 1 < self.file_limit
        ):
            bucket.append(node)
            total_size += node.size
            total_files += 1
            node = self.next_downloadable()

        if node:
            bucket.append(node)
            total_size += node.size
            total_files += 1

        if bucket:
            return bucket
        else:
            raise StopIteration


class NodesThreadPool(ABC):
    def __init__(self, max_threads):
        self._max_threads = max_threads
        self._thread_counter = 0
        self._thread_lock = threading.Lock()

    def run(
        self,
        chunk_gen,
        progress_bar_descr,
        total_size,
        shared_progress_bar=None,
    ):
        results = []
        with concurrent.futures.ThreadPoolExecutor(self._max_threads) as thPool:
            tasks = set()

            self._thread_counter = 0
            progress_bar = shared_progress_bar or tqdm(
                desc=progress_bar_descr,
                unit="B",
                unit_scale=True,
                unit_divisor=1000,
                total=total_size,
            )

            chunk = next(chunk_gen, None)
            while chunk:
                while len(tasks) >= self._max_threads:
                    done, _ = concurrent.futures.wait(
                        tasks, timeout=1, return_when="FIRST_COMPLETED"
                    )
                    self.done_task(done)

                    tasks = tasks - done
                    self.update_progress_bar(progress_bar)

                tasks.add(thPool.submit(self.do_task, chunk))

                self.update_progress_bar(progress_bar)

                chunk = next(chunk_gen, None)

            while tasks:
                done, _ = concurrent.futures.wait(
                    tasks, timeout=1, return_when="FIRST_COMPLETED"
                )
                task_results = self.done_task(done)
                if task_results:
                    results.extend(task_results)

                tasks = tasks - done
                self.update_progress_bar(progress_bar)

            thPool.shutdown()

        return results

    def update_progress_bar(self, progress_bar):
        with self._thread_lock:
            if self._thread_counter:
                progress_bar.update(self._thread_counter)
                self._thread_counter = 0

    def increase_counter(self, value):
        with self._thread_lock:
            self._thread_counter += value

    @abstractmethod
    def do_task(self, chunk):
        pass

    @abstractmethod
    def done_task(self, done):
        pass
