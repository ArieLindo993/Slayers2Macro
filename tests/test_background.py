import multiprocessing as mp
import os
from pathlib import Path
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from background import BackgroundWorker, BackgroundBusy, BackgroundError, BackgroundTimeout


def add(left, right):
    return left + right


def hang():
    time.sleep(60)


def crash():
    os._exit(7)


def fail():
    raise ValueError("failed analysis")


def payload_size(payload):
    return len(payload)


class LazyReader:
    def __init__(self):
        self.calls = 0

    def read(self):
        self.calls += 1
        return self.calls


class BackgroundTests(unittest.TestCase):
    def worker(self, **kwargs):
        worker = BackgroundWorker(name="test-analysis", **kwargs)
        self.addCleanup(worker.shutdown)
        return worker

    def completed(self, worker, future, timeout=15):
        deadline = time.monotonic() + timeout
        while not future.done() and time.monotonic() < deadline:
            worker.poll()
            time.sleep(.01)
        self.assertTrue(future.done(), "background job did not finish")
        return future

    def submit_after_restart(self, worker, function, *args):
        deadline = time.monotonic() + 3
        while True:
            try:
                return worker.submit(function, *args)
            except BackgroundBusy:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.01)

    def test_lazy_process_reuses_reader_and_does_not_modify_parent(self):
        worker = self.worker(timeout=10)
        self.assertIsNone(worker.pid)
        reader = LazyReader()
        first = worker.submit(reader.read)
        self.assertEqual(self.completed(worker, first).result(), 1)
        pid = worker.pid
        second = worker.submit(reader.read)
        self.assertEqual(self.completed(worker, second).result(), 2)
        self.assertEqual(worker.pid, pid)
        self.assertEqual(reader.calls, 0)

    def test_capacity_is_bounded_and_timeout_restarts_worker(self):
        worker = self.worker(timeout=10, max_pending=2)
        stuck = worker.submit(hang)
        queued = worker.submit(add, 2, 3)
        with self.assertRaises(BackgroundBusy):
            worker.submit(add, 3, 4)
        old_pid = worker.pid
        worker.poll(now=time.monotonic() + 11)
        for future in (stuck, queued):
            with self.assertRaises(BackgroundTimeout):
                future.result()
        self.assertEqual(worker.pending_count, 0)
        resumed = self.submit_after_restart(worker, add, 8, 9)
        self.assertEqual(self.completed(worker, resumed).result(), 17)
        self.assertNotEqual(worker.pid, old_pid)
        self.assertEqual(worker.restarts, 1)

    def test_crashed_process_fails_future_and_accepts_next_job(self):
        worker = self.worker(timeout=10)
        future = worker.submit(crash)
        with self.assertRaises(BackgroundError):
            self.completed(worker, future).result()
        next_job = self.submit_after_restart(worker, add, 3, 9)
        self.assertEqual(self.completed(worker, next_job).result(), 12)

    def test_task_error_is_local_and_worker_remains_usable(self):
        worker = self.worker(timeout=10)
        failed = worker.submit(fail)
        with self.assertRaisesRegex(BackgroundError, "ValueError"):
            self.completed(worker, failed).result()
        future = worker.submit(add, 4, 7)
        self.assertEqual(self.completed(worker, future).result(), 11)
        self.assertEqual(worker.restarts, 0)

    def test_shutdown_terminates_native_style_hang_without_waiting(self):
        worker = self.worker(timeout=10)
        future = worker.submit(hang)
        pid = worker.pid
        started = time.monotonic()
        worker.shutdown()
        self.assertLess(time.monotonic() - started, 1.5)
        self.assertTrue(future.done())
        self.assertNotIn(pid, [process.pid for process in mp.active_children()])
        with self.assertRaises(RuntimeError):
            worker.submit(add, 1, 1)

    def test_terminated_large_image_transfer_does_not_leave_feeder_thread(self):
        existing = set(threading.enumerate())
        worker = self.worker(timeout=10, max_pending=2)
        self.completed(worker,worker.submit(add,1,1)).result()
        first = worker.submit(hang)
        # Larger than a pipe buffer: the feeder waits while the child is busy.
        second = worker.submit(payload_size, bytes(16 * 1024 * 1024))
        worker.poll()
        time.sleep(.1)
        worker.shutdown()
        self.assertTrue(first.done())
        self.assertTrue(second.done())
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            new_feeders = [thread for thread in threading.enumerate()
                           if thread not in existing and thread.name == "QueueFeederThread"]
            if not new_feeders:
                break
            time.sleep(.01)
        self.assertFalse(new_feeders, "terminated analysis left a blocked image sender")


if __name__ == "__main__":
    mp.freeze_support()
    unittest.main()
