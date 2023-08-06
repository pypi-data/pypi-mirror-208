"""
Handles file transfer via the `rsync` protocol
"""
import pathlib

from remotemanager.transport.transport import Transport


class rsync(Transport):
    """
    Class for `rsync` protocol

    Args:
        checksum (bool):
            Adds checksum arg, which if True will add --checksum flag to
            parameters
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # flags can be exposed, to utilise their flexibility
        flags = kwargs.pop("flags", "auv")
        self.flags = flags

        if kwargs.get("checksum", False):
            print("adding checksum to rsync")
            self.flags += "--checksum"

        self._logger.info("created new rsync transport")

        self._cmd = "rsync {flags} {password}{inner_dir}{primary} {secondary}"

    def cmd(self, primary, secondary):

        if self.url.passfile and self.url.keyfile:
            raise RuntimeError(
                "rsync appears to have an issue when "
                "specifying sshpass AND ssh-key. Either set up "
                "your ssh config and remove the keyfile or use "
                "transport.scp"
            )

        def get_remote_dir(path):
            if ":" not in path:
                return path
            return path.split(":")[1]

        password = ""
        if self.url.passfile is not None:
            password = f'--rsh="sshpass -f {self.url.passfile} ssh" '

        cmd = self._cmd
        inner_dir = ""
        if len(pathlib.Path(secondary).parts) > 1:
            # the target is a nested dir. If the whole tree doesn't exist,
            # rsync with throw an error
            if ":" in secondary:
                # target is a remote folder, use the --rsync-path hack
                inner_dir = (
                    f'--rsync-path="mkdir -p ' f'{get_remote_dir(secondary)} && rsync" '
                )
            else:
                cmd = f"mkdir -p {secondary} && {self._cmd}"

        base = cmd.format(
            flags=self.flags,
            password=password,
            primary=primary,
            secondary=secondary,
            inner_dir=inner_dir,
        )
        self._logger.debug(f'returning formatted cmd: "{base}"')
        return base
