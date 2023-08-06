import importlib
import os
import time

from remotemanager.storage.sendablemixin import SendableMixin
from remotemanager.logging import LoggingMixin


class ConnectionTest(SendableMixin, LoggingMixin):
    """
    Object to store an instance of a connection test.

    Runs the tests, storing any important information

    Args:
        parent:
            parent URL
    """

    def __init__(self, parent):
        self._parent = parent

        self._run = False
        self._passed = False

        self._data = {}
        self._extra = {}

        self._latency = None

        self.dt = 0

    def __bool__(self):
        return self.passed

    @property
    def parent(self):
        return self._parent

    def exec(self) -> None:
        """
        Execute the connection test
        """

        self._run = True

        ncalls_init = self.parent.call_count
        self.dt = 0

        for name in dir(self):
            if name.startswith("test_"):
                self._logger.debug(f"running test {name}")
                self._data[name] = getattr(self, name)()

        self._passed = all(self._data.values())

        delta_calls = self.parent.call_count - ncalls_init
        latency = self.dt / delta_calls
        self._data["ncalls"] = delta_calls
        self._data["dt"] = self.dt
        self._data["latency"] = latency
        self._latency = latency

        print(f"Done! Made {delta_calls} calls, taking {self.dt:.2f}s")
        print(f"Approximate latency, {latency:.2f}s")
        if self.passed:
            print("Tests passed successfully")
        else:
            print("Tests did not pass")

    @property
    def passed(self):
        return self._passed

    @property
    def data(self):
        return self._data

    @property
    def extra(self):
        return self._extra

    @property
    def latency(self):
        return self._latency

    def test_basic(self) -> bool:
        """
        Connects to the host and returns the entry directory

        Returns:
            (bool): True if test succeeded
        """

        print("Checking for entry point...", end=" ")
        try:
            t0 = time.time()
            entry = self.parent.cmd("pwd")
            self.dt += time.time() - t0

            print(f"Success ({entry})")

            self._extra["entrypoint"] = entry
            return True

        except Exception as E:
            self._extra["entrypoint"] = str(E)
            print(f"Failure: {E}")
            return False

    def test_files(self) -> bool:
        """
        Attempts to create and delete files in several directories

        Returns:
            (bool): True if test succeeded
        """

        _ENTRYPOINT_PLACEHOLDER = "home"
        _TESTING_FILENAME = "connection_test_tmp_file"

        def create_file(directory=None):
            if directory != _ENTRYPOINT_PLACEHOLDER:
                filename = os.path.join(directory, _TESTING_FILENAME)
            else:
                filename = _TESTING_FILENAME

            t0 = time.time()
            cmd = self.parent.cmd(f"touch {filename}", raise_errors=False)
            presence = (
                _TESTING_FILENAME
                in self.parent.cmd(f"ls {filename}", raise_errors=False).stdout
            )
            dt = time.time() - t0

            return cmd, presence, filename, dt

        dirs = {_ENTRYPOINT_PLACEHOLDER: False, "/tmp": False, "/scratch": False}

        for directory in dirs:
            print(f"Checking file creation in {directory}...", end=" ")
            cmd, presence, created, dt = create_file(directory)
            dirs[directory] = presence
            print(presence)

            if presence:
                t0 = time.time()
                self.parent.cmd(f"rm {created}")
                self.dt += time.time() - t0
            else:
                self._extra[f"{directory} creation error"] = cmd.stderr

        self._extra["file_creation"] = dirs

        return dirs[_ENTRYPOINT_PLACEHOLDER]

    def test_transport(self) -> bool:
        """
        Tests all available transport methods, returning True if at least one
        is functional

        Returns:
            (bool): True if test succeeded
        """

        transport_collection = importlib.import_module("remotemanager.transport")

        transport_instances = []
        for name in dir(transport_collection):
            # exclude private/protected variables
            # exclude base class and cp (local only)
            if name.startswith("_") or name in ("transport", "cp"):
                continue
            # generate and store an instance
            transport_instances.append(transport_collection.__dict__[name](self.parent))

        written_files = []
        if len(transport_instances) > 0:
            for i in range(3):
                tmp = f"test_file_{i}.txt"
                with open(tmp, "w+") as o:
                    o.write(f"test_{i}")
                    written_files.append(tmp)

        passed = False
        transport_tests = {}
        for tmp_transport in transport_instances:

            name = tmp_transport.__module__
            print(f"Testing {name}:\n\tsend... ", end="")

            t0 = time.time()
            self.parent.cmd("mkdir -p connection_test")

            tmp_transport.queue_for_push(written_files, ".", "connection_test")
            try:
                tmp_transport.transfer()
                send = self.parent.utils.ls("connection_test") == written_files
            except Exception as E:
                send = False
                self._extra[f"{name} send error"] = str(E)

            print(f"{send}\n\tpull... ", end="")

            self.parent.cmd("touch connection_test/retrieve_test")

            tmp_transport.queue_for_pull(["retrieve_test"], ".", "connection_test")
            try:
                tmp_transport.transfer()
                pull = "retrieve_test" in self.parent.utils.ls(".", local=True)
            except Exception as E:
                pull = False
                self._extra[f"{name} pull error"] = str(E)

            print(pull)

            self.parent.cmd("rm -r connection_test")
            self.dt += time.time() - t0
            try:
                os.remove("retrieve_test")
            except FileNotFoundError:
                pass

            transport_tests[tmp_transport.__module__] = (send, pull)

            if send and pull:
                passed = True

        self._extra["transport tests"] = transport_tests

        print("Cleaning up... ", end="")
        for file in written_files:
            os.remove(file)
        print("Done")

        return passed
