import copy
import json
import os
import time

from remotemanager.storage.database import Database
from remotemanager.storage import SendableMixin, TrackedFile
from remotemanager.storage.sendablemixin import SERIALISED_STORAGE_KEY
from remotemanager.logging.utils import format_iterable
from remotemanager.utils.uuid import generate_uuid
from remotemanager.utils import object_from_uuid, _time_format
from remotemanager.logging import LoggingMixin
from remotemanager.logging.verbosity import Verbosity

from datetime import datetime

localwinerror = """Local runs on windows machines are not supported.
Please use a URL which connects to a non-windows machine or consider using
Docker to continue."""


class Runner(SendableMixin, LoggingMixin):
    """
    The Runner class stores any info pertaining to this specific run. E.g.
    Arguments, result, run status, files, etc.

    .. warning::
        Interacting with this object directly could cause unstable behaviour.
        It is best to allow Dataset to handle the runners. If you require a
        single run, you should create a Dataset and append just that one run.
    """

    _defaults = {"skip": True}

    _default_local_dir = "temp_runner_local"
    _default_remote_dir = "temp_runner_remote"

    _submit_status = {
        "initial": "creating files and submitting...",
        "final": "command executed remotely",
    }

    _args_replaced_key = "~serialised_args~"

    _do_not_package = ["_serialiser", "_parent", "_database"]

    def __init__(
        self,
        arguments: dict,
        dbfile: str,
        parent,
        self_id: str,
        extra_files_send: list = None,
        extra_files_recv: list = None,
        verbose: int = None,
        **kwargs,
    ):

        self._verbose = Verbosity(verbose)

        self._run_options = self._set_defaults(kwargs)

        self._extra_files = {
            "send": extra_files_send if extra_files_send is not None else [],
            "recv": extra_files_recv if extra_files_recv is not None else [],
        }

        if arguments is not None and not isinstance(arguments, dict):
            raise ValueError(
                f"runner arguments ({type(arguments)}) " "must be dict-type"
            )

        # parent and id setting
        self._parent = parent
        self._parent_uuid = parent.uuid  # used for parent memory recovery

        self._id = self_id

        # check that we can properly serialise the args
        # this needs to be within the runner, so we can properly generate uuids
        self._args_replaced = False
        try:
            json.dumps(arguments)
            uuid_slug = copy.deepcopy(arguments) or {}
        except TypeError:
            file = f"{self.parent.argfile}-" f"{self.id}{self.serialiser.extension}"
            lpath = os.path.join(self.parent.local_dir, file)

            if not os.path.isdir(self.parent.local_dir):
                os.makedirs(self.parent.local_dir)

            content = self.parent.serialiser.dumps(arguments)
            with open(lpath, self.serialiser.write_mode) as o:
                o.write(content)

            # adding the file in here forces the kwargs to swap out
            # kwargs for a repo.load
            arguments = {file: Runner._args_replaced_key}
            self._args_replaced = True

            uuid_slug = {"uuid_base": generate_uuid(str(content))}

            extra_files_send.append(lpath)

        # uuid generation
        uuid_slug.update(**kwargs)
        self._runner_uuid = generate_uuid(format_iterable(uuid_slug))
        self._uuid = generate_uuid(self._runner_uuid + str(self.parent.uuid))

        self._logger.info(f"new runner (id {self.uuid}) created")

        self._args = arguments
        self._state_time = None
        self._last_submitted = -1
        self._state = None
        self._extension = "yaml"

        self._dependency_info = {}

        self._dbfile = dbfile

        self._manual_run = False
        self._history = {}
        self.state = "created"

        self._identifier = f"{self.parent.name}-" f"{self.parent.short_uuid}-{self.id}"

    def __hash__(self) -> hash:
        return hash(self.uuid)

    def __repr__(self) -> str:
        return self.identifier

    @property
    def verbose(self) -> Verbosity:
        return self._verbose

    @property
    def database(self) -> Database:
        """
        Access to the stored database object.
        Creates a connection if none exist.

        Returns:
            Database
        """
        if not hasattr(self, "_database"):
            self._database = Database(file=self._dbfile)
        return self._database

    @property
    def parent(self):
        if self.is_missing("_parent"):
            self._parent = object_from_uuid(self._parent_uuid, "Dataset")
        return self._parent

    @property
    def serialiser(self):
        return self.parent.serialiser

    @staticmethod
    def _set_defaults(kwargs: dict = None) -> dict:
        """
        Sets default arguments as expected. If used as a staticmethod, returns
        the defaults
        """

        if kwargs is None:
            kwargs = {}

        for k, v in Runner._defaults.items():
            if k not in kwargs:
                kwargs[k] = v

        return kwargs

    @property
    def uuid(self) -> str:
        """
        The uuid of this runner
        """
        return self._uuid

    @property
    def short_uuid(self) -> str:
        """
        A short uuid for filenames
        """
        return self.uuid[:8]

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._id

    @property
    def identifier(self) -> str:
        return self._identifier

    def _format_filename(self, identifier: str, ftype: str, ext: str) -> str:
        """
        Formats internal file names consistently.

        Args:
            identifier (str):
                dataset name and runner id as string
            ftype (str):
                file type. Jobscript, result file, etc.
            ext (str):
                file extension

        Returns:
            str: formatted filename
        """
        self._logger.info(
            f"creating filename for content {identifier}, "
            f"filetype {ftype} and "
            f"extension {ext}"
        )
        return f"{identifier}-{ftype}{ext}"

    @property
    def runfile(self) -> TrackedFile:
        """
        Filename of the python runfile
        """
        base_name = self._format_filename(self.identifier, "run", ".py")

        return TrackedFile(self.local_dir, self.remote_dir, base_name)

    @property
    def jobscript(self) -> TrackedFile:
        """
        Filename of the run script
        """
        base_name = self._format_filename(self.identifier, "jobscript", ".sh")

        return TrackedFile(self.local_dir, self.remote_dir, base_name)

    @property
    def resultfile(self) -> TrackedFile:
        """
        Result file name
        """
        base_name = self._format_filename(
            self.identifier, "result", f".{self.result_extension}"
        )

        paths = [self.remote_dir]
        if self.run_dir != self.remote_dir and self.run_dir is not None:
            paths.append(self.run_dir)
        joined = "/".join(paths)

        return TrackedFile(self.local_dir, joined, base_name)

    @property
    def errorfile(self) -> TrackedFile:
        """
        File tracker for error dumpfile
        """
        return TrackedFile(self.local_dir, self.remote_dir, self.parent.stderr_dump)

    def _relative_remote_dir(self, file: str) -> str:
        """
        remote dir path relative to run dir
        """
        self._logger.info(
            f"getting relative path to remote dir for file "
            f"{file} where remote={self.remote_dir} and run="
            f"{self.run_dir}"
        )
        if self.run_dir is None:
            self._logger.info("no run dir, returning file as rel path")
            return file
        return os.path.join("..", file)

    @property
    def result_extension(self) -> str:
        """
        Resultfile file format extension
        """
        return self._extension

    @result_extension.setter
    def result_extension(self, ext: str) -> None:
        """
        Sets the resultfile format extension

        .. warning::
            This does not change anything aside from the extension that
            the runner looks for when trying to find a result file. If you
            require a different serialisation, you should set the serialiser.
        """
        self._extension = ext.strip(".")

    @property
    def local_dir(self) -> str:
        """
        Local staging directory
        """
        return self._run_options.get("local_dir", Runner._default_local_dir)

    @local_dir.setter
    def local_dir(self, path: str) -> None:
        """
        Sets the local_dir
        """
        self._run_options["local_dir"] = path

    @property
    def remote_dir(self) -> str:
        """
        Target directory on the remote for transports
        """
        if "remote_dir" in self._run_options:
            return self._run_options["remote_dir"]
        return self._run_options.get("run_dir", Runner._default_remote_dir)

    @remote_dir.setter
    def remote_dir(self, path: str) -> None:
        """
        Sets the remote_dir
        """
        self._logger.debug(f"setting remote dir to {path}")
        self._run_options["remote_dir"] = path

    @property
    def run_dir(self) -> [str, None]:
        """
        Intended running directory. If not set, uses remote_dir

        .. note::
            If both remote_dir and run_dir are set, the files will be
            transferred to remote_dir, and then executed within run_dir
        """
        if "run_dir" in self._run_options:
            abs_rundir = self._run_options["run_dir"]
            common = os.path.commonpath((self.remote_dir, abs_rundir))

            run = os.path.split(abs_rundir.replace(common, ""))[1]
            return run
        return None

    @run_dir.setter
    def run_dir(self, dir: str) -> None:
        """
        Sets the run_dir
        """
        self._run_options["run_dir"] = dir

    @property
    def args(self) -> dict:
        """
        Arguments for the function
        """
        if self._args is None:
            return {}
        return self._args

    @property
    def extra_files(self) -> dict:
        """
        Returns the extra files set for this runner
        """
        return self._extra_files

    @property
    def result(self):
        """
        Result (If available)
        """
        if hasattr(self, "_result"):
            try:
                if SERIALISED_STORAGE_KEY in self._result:
                    self._result = self.parent.serialiser.loads(self._result[1])
            except TypeError:
                pass

            return self._result
        return None

    @result.setter
    def result(self, result) -> None:
        """
        Creates and sets the result property, setting the state to "completed"

        Args:
            result:
                run result
        """
        self._result = result
        self.state = "completed"

    def clear_result(self) -> None:
        """
        Removes any results, and sets the state to "result wiped"
        """
        try:
            del self._result
        except AttributeError:
            pass

        def remove_file(path):
            self._logger.info(f"attempting to clear result file {path}")
            try:
                os.remove(path)
                self._logger.info("Done")
            except FileNotFoundError:
                self._logger.info("file not found")

        remove_file(self.resultfile.local)
        remove_file(self.resultfile.remote)

        self.state = "result wiped"

    @property
    def state(self) -> str:
        """
        Returns the most recent runner state
        """
        return self._state

    @state.setter
    def state(self, newstate: str) -> None:
        """
        Update the state and store within the runner history
        """

        state_time = datetime.now()

        self.insert_history(state_time, newstate)

        t = int(time.time())
        self._state_time = t

        if newstate == Runner._submit_status["final"]:
            self._last_submitted = t
        self._state = newstate

    @property
    def last_updated(self) -> int:
        """
        Time that this runner state last changed
        """
        return self._state_time

    @property
    def last_submitted(self) -> int:
        """
        Time that this runnerwas last submitted
        """
        return self._last_submitted

    def format_time(self, t: datetime.time) -> str:
        """
        Format the datetime object into a dict key

        Args:
            t (datetime.time):
                time object to be formatted to string

        Returns:
            (str):
                formatted time
        """
        return t.strftime(_time_format)

    @property
    def history(self) -> dict:
        """
        State history of this runner
        """
        return self._history

    @property
    def status_list(self) -> list:
        """
        Returns a list of status updates
        """
        return list(self._history.values())

    def insert_history(self, t: datetime, newstate: str) -> None:
        """
        Insert a state into this runner's history

        Args:
            t (datetime.time):
                time this state change occurred
            newstate (str):
                status to update
        """
        if not isinstance(t, datetime):
            raise ValueError(
                f"time of type {type(t)} should be a datetime " f"instance"
            )

        base_timekey = self.format_time(t)
        idx = 0
        timekey = f"{base_timekey}/{idx}"
        while timekey in self._history:
            idx += 1

            timekey = f"{base_timekey}/{idx}"
            self._logger.info(f"timekey updated to {timekey}")

        self._logger.info(f"updating runner {self.short_uuid} state -> " f"{newstate}")
        self._history[timekey] = newstate

    def run(self, dry_run: bool = False, **kwargs) -> None:
        """
        Perform a manual run

        .. warning::
            This method should be used sparingly, as it creates a Datset
            object within the function from the Database. This is a costly
            process and potentially unstable.

        Args:
            dry_run (bool):
                create files, but do not run
        """

        parent = self.unserialise(self.database.find(self.parent.uuid))

        if not self._assess_run(**self._run_options):
            return None

        if os.name == "nt" and parent.url.is_local:
            raise RuntimeError(localwinerror)

        self._manual_run = True  # set internal flag for a manual run
        self._run_options.update(kwargs)
        self.state = Runner._submit_status["initial"]
        self._write_runfile(parent)

        parent.transport.queue_for_push(
            self.runfile.name, self.local_dir, self.remote_dir
        )

        script = parent._script_sub(**self.run_args)

        self._write_script(parent.url.python, script)

        parent.transport.queue_for_push(
            self.jobscript.name, self.jobscript.local_dir, self.jobscript.remote_dir
        )

        cmd = (
            f"cd {self.jobscript.remote_dir} &&"
            f" {parent.submitter} {self.jobscript.name}"
        )

        if not dry_run:
            parent.transport.transfer()
            parent.url.cmd(cmd, asynchronous=False)
            self.state = Runner._submit_status["final"]
        else:
            parent.transport.wipe_transfers()
            self._logger.important(f"launch command: {cmd}")
            self.state = "dry run"

    def _assess_run(self, **kwargs) -> bool:

        self._extra_files["send"] += kwargs.pop("extra_files_send", [])
        self._extra_files["recv"] += kwargs.pop("extra_files_recv", [])

        self._run_options.update(kwargs)

        self._logger.important(f"assessing run for runner {self}", end="... ")
        self._logger.info("\nrun args:")
        self._logger.info(format_iterable(self.run_args))
        self._logger.info(f"current state is {self.state}")

        if self.run_option("force", False):
            self._logger.warning("force running")
            return True

        if self.state == Runner._submit_status["final"]:
            self._logger.warning("skipping already submitted run")
            return False

        # old skip test unpacks a runner from the database
        if self.is_finished and self.run_option("skip", True):
            self._logger.warning("skipping already completed run")
            return False

        self._logger.important("checks passed, running")
        return True

    def _write_runfile(self, dataset, write_file: bool = True) -> str:
        """
        Writes the python file which actually runs the function

        Args:
            dataset:
                parent dataset
            write_file (bool):
                skip writing runfile if false, used only for debugging purposes

        Returns:
            (str): runfile contents
        """

        self._logger.info(f"pre-running function {self.uuid}")

        if self._manual_run:
            self._logger.info("forcing dataset repo write")
            dataset._write_to_repo()

        # check if we have replaced args with a file, and use that if so
        if self._args_replaced:
            argstore = list(self.args.keys())[0]
            argline = f'kwargs = repo.load("' f'{self._relative_remote_dir(argstore)}")'
        else:
            argline = f"kwargs = {self.args}"

        runscript = [
            f"repo = __import__('{dataset.repofile}')",
            argline,
            f"result = repo.{dataset.function.name}(**kwargs)",
            f"repo.dump(result, '{self.resultfile.name}')",
        ]

        if dataset.is_child:
            runscript.insert(2, self._dependency_info["parent_import"])
        if dataset.is_parent:
            for line in self._dependency_info["child_submit"]:
                runscript.append(line)

        output = "\n".join(runscript)
        if write_file:
            if not os.path.isdir(self.local_dir):
                self._logger.info(f"creating local dir {self.local_dir}")
                os.makedirs(self.local_dir)
            with open(self.runfile.local, "w+") as o:
                o.write(output)
            self.state = "runfile written"
        else:
            self.state = "runfile write skipped"

        return output

    def _write_script(self, python: str, script, write_file: bool = True) -> str:
        """
        Writes the jobscript for this runner

        Args:
            python (str):
                python command to launch runfile
            script (str, URL.script):
                script header
        """
        tmp = []
        if isinstance(script, str):
            self._logger.debug("initialising script array with string input:")
            self._logger.debug(script)
            tmp.append(script)
        else:
            self._logger.info("script passed to runner requires substitution")
            tmp.append(script(**self.run_args))

        if self.run_dir and self.run_dir != self.remote_dir:
            self._logger.debug("run dir is separate to remote dir, appending extras")
            cmd = (
                f"pydir=$PWD\n"
                f"mkdir -p {self.run_dir} && "
                f"cd {self.run_dir} && "
                f"{python} ${{pydir}}/{self.runfile.name}"
            )
        else:
            runline = f"{python} {self.runfile.name}"
            self._logger.debug(f"directly appending line {runline}")
            cmd = runline  # run file

        tmp.append(cmd)

        path = self.jobscript.local
        output = "\n".join(tmp)
        if write_file:
            self._logger.info(f"writing run script to {path}")
            with open(path, "w+") as o:
                o.write(output)
            self.state = "jobscript written"
        else:
            self.state = "jobscript write skipped"

        return output

    @property
    def is_finished(self) -> bool:
        """
        Attempts to determine if this runner has completed its run

        Returns (bool):
            completion status
        """
        fin = hasattr(self, "_result")
        self._logger.info(
            f"checking finished state of runner " f"{self.short_uuid} -> {fin}"
        )
        return fin

    def update_run_options(self, run_args: dict) -> None:
        """
        Update run args with dict `run_args`
        Args:
            run_args (dict):
                new run arguments

        Returns:
            None
        """
        self._logger.info("updating run options with new run args:")
        self._logger.info(format_iterable(run_args))

        self._run_options.update(run_args)

    def run_option(self, option: str, default=None):
        """
        Return a run option

        Args:
            option (str):
                key to search for
            default:
                default argument to provide to get

        Returns:
            option if available, else None
        """
        ret = self._run_options.get(option, default)
        self._logger.debug(f"getting run option {option}: {ret}")
        return ret

    @property
    def run_args(self) -> dict:
        """
        Display the run arguments

        Returns:
            (dict) run_args
        """
        return self._run_options
