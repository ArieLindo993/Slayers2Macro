"""Bounded, restartable local workers for visual analysis and OCR.

Call ``poll`` from the UI tick before reading the returned Futures. Unlike a
thread executor, an analysis stuck inside a native library can be terminated.
Only the child process runs the callable; screen capture and input stay in the
main process. Queue feeder threads send image arrays without waiting in submit.
"""
from concurrent.futures import Future
import multiprocessing as mp
from queue import Empty, Full
import time


class BackgroundError(RuntimeError):
    pass


class BackgroundTimeout(BackgroundError):
    pass


class BackgroundBusy(BackgroundError):
    pass


def _run_requests(requests, results):
    # Bound readers retain their lazily loaded OCR model between requests.
    callables = {}
    results.put((0, True, None))
    while True:
        request = requests.get()
        if request is None:
            return
        identity, key, function, args, kwargs = request
        if key not in callables:
            if len(callables) >= 8:
                callables.clear()
            callables[key] = function
        try:
            value = callables[key](*args, **kwargs)
        except Exception as exc:
            # Arbitrary exception instances need not support pickling.
            results.put((identity, False, (type(exc).__name__, str(exc)[:300])))
        else:
            results.put((identity, True, value))


class BackgroundWorker:
    """One lazy process, a bounded queue, and a deadline for every submitted job.

    This object is owned by the UI thread. A timeout/crash fails all outstanding
    Futures and terminates the worker. The next submit starts a fresh process.
    ``max_pending`` bounds running plus queued work, including image copies.
    Callables and their arguments must be picklable for Windows spawn. Bound
    methods are cached in the child by instance identity, preserving OCR models.
    """
    def __init__(self, name="background", timeout=15., max_pending=1):
        if timeout <= 0 or max_pending < 1:
            raise ValueError("Worker timeout and capacity must be positive")
        self.name = name
        self.timeout = float(timeout)
        self.max_pending = int(max_pending)
        self._context = mp.get_context("spawn")
        self._process = None
        self._requests = None
        self._results = None
        self._pending = {}
        self._outbox = []
        self._ready = False
        self._retired = []
        self._identity = 0
        self._closed = False
        self.restarts = 0

    @property
    def pending_count(self):
        return len(self._pending)

    @property
    def available(self):
        return not self._closed and self.pending_count < self.max_pending

    @property
    def can_submit(self):
        self._reap()
        return self.available and not self._retired

    @property
    def pid(self):
        return self._process.pid if self._process is not None else None

    def _reap(self):
        remaining = []
        for process, retired_at in self._retired:
            if process.is_alive():
                if time.monotonic() - retired_at >= .5:
                    try:
                        process.kill()
                    except OSError:
                        pass
                remaining.append((process, retired_at))
            else:
                process.join(timeout=0)
                process.close()
        self._retired = remaining

    def _start(self):
        self._reap()
        # Never accumulate replacement processes if OS termination is delayed.
        if self._retired:
            raise BackgroundBusy(self.name + ": reiniciando análise")
        self._requests = self._context.Queue(maxsize=self.max_pending)
        self._results = self._context.Queue(maxsize=self.max_pending)
        self._ready = False
        self._process = self._context.Process(
            target=_run_requests, args=(self._requests, self._results),
            name=self.name, daemon=True)
        try:
            self._process.start()
            # These pipe ends belong only to the child. Leaving the request
            # reader open in the parent would keep its feeder blocked forever
            # on a large image when the child is terminated mid-transfer.
            self._requests._reader.close()
            self._requests._ignore_epipe = True
            self._results._writer.close()
        except Exception:
            self._dispose_queues()
            self._process.close()
            self._process = None
            raise

    def submit(self, function, *args, **kwargs):
        self.poll()
        if self._closed:
            raise RuntimeError("Worker is closed")
        if not self.available:
            raise BackgroundBusy(self.name + ": fila de análise ocupada")
        if self._process is None:
            self._start()
        self._identity += 1
        identity = self._identity
        owner = getattr(function, "__self__", None)
        key = (getattr(function, "__module__", ""),
               getattr(function, "__qualname__", type(function).__qualname__),
               id(owner) if owner is not None else id(function))
        future = Future()
        # Work is committed to the bounded queue; it cannot be individually
        # cancelled after submission without discarding its whole worker.
        future.set_running_or_notify_cancel()
        # Wait for the child's startup handshake before sending large images.
        # On Windows, terminating during spawn can leave an unclaimed reader
        # handle; sending before the handshake could strand a feeder thread.
        self._outbox.append((identity, key, function, args, kwargs))
        self._pending[identity] = (future, time.monotonic())
        return future

    def _dispose_queues(self):
        self._outbox = []
        self._ready = False
        for channel in (self._requests, self._results):
            if channel is not None:
                # A killed consumer cannot drain the feeder; never join it.
                channel.cancel_join_thread()
                channel.close()
        self._requests = self._results = None

    def _retire(self, error):
        process = self._process
        self._process = None
        if process is not None:
            if process.is_alive():
                try:
                    process.terminate()
                except OSError:
                    pass
            self._retired.append((process, time.monotonic()))
        self._dispose_queues()
        pending, self._pending = self._pending, {}
        for future, _ in pending.values():
            if not future.done():
                future.set_exception(error)
        self._reap()

    def poll(self, now=None):
        self._reap()
        if self._closed or self._process is None:
            return 0
        changed = 0
        try:
            while True:
                identity, success, value = self._results.get_nowait()
                if identity == 0:
                    self._ready = True
                    continue
                pending = self._pending.pop(identity, None)
                if pending is None:
                    continue
                future, _ = pending
                if success:
                    future.set_result(value)
                else:
                    kind, message = value
                    future.set_exception(BackgroundError(
                        self.name + ": " + kind + (": " + message if message else "")))
                changed += 1
        except Empty:
            pass
        except (EOFError, OSError, ValueError) as exc:
            changed += self.pending_count
            self.restarts += 1
            self._retire(BackgroundError(self.name + ": " + type(exc).__name__))
            return changed
        now = time.monotonic() if now is None else now
        if self._pending and any(now - started >= self.timeout
                                 for _, started in self._pending.values()):
            changed += self.pending_count
            self.restarts += 1
            self._retire(BackgroundTimeout(self.name + ": tempo de análise excedido"))
        elif self._process.exitcode is not None:
            changed += self.pending_count
            self.restarts += 1
            self._retire(BackgroundError(self.name + ": processo de análise encerrado"))
        if self._process is not None and self._ready:
            while self._outbox:
                try:self._requests.put_nowait(self._outbox[0])
                except Full:break
                self._outbox.pop(0)
        return changed

    def shutdown(self, wait=True, cancel_futures=True):
        # Bounded even when a native library never returns. Compatibility
        # arguments intentionally do not turn this into an unbounded wait.
        if self._closed:
            return
        self._closed = True
        self._retire(BackgroundError(self.name + ": análise encerrada"))
        if wait:
            deadline = time.monotonic() + 1.
            while self._retired and time.monotonic() < deadline:
                self._retired[0][0].join(timeout=.05)
                self._reap()
