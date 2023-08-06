from remotemanager.logging import LoggingMixin
from remotemanager import Dataset, Quiet

from IPython.core.magic import Magics, magics_class, cell_magic, needs_local_scope


@magics_class
class RCell(Magics, LoggingMixin):
    """
    Magic function that allows running an ipython cell on a remote machine
    with minimal lines of code.
    """

    @cell_magic
    @needs_local_scope
    def sanzu(self, line: str, cell: str, local_ns: dict) -> None:
        """
        Execute a jupyter cell using an implicit remote Dataset

        Args:
            line:
                magic line, includes arguments for cell and Dataset
            cell:
                Cell contents
            local_ns:
                dict containing current notebook runtime attributes
        """
        fstr, args, fargs = self.parse_line(line, cell, local_ns)

        self._logger.info(f"generated function string {fstr}")
        # Build the runner and run
        ds = Dataset(function=fstr, block_reinit=False, **args)
        ds.append_run(args=fargs)
        ds.run()

        for cmd in ds.run_cmds:
            if cmd.stderr:
                raise RuntimeError(f"error detected in magic run: " f"{cmd.stderr}")
        Quiet.state = True
        ds.wait(1)
        ds.fetch_results()
        Quiet.state = False

        local_ns["magic_dataset"] = ds

    def parse_line(self, line: str, cell: str, local_ns: dict):

        self._logger.info(f"creating magic cell with line {line}")

        # Handle the case where the cell magic is split over lines.
        foundc = False
        remainder = ""
        line = line.split("#")[0].strip()
        if line[-1] == "\\":
            line = line[:-1]
            for cline in cell.split("\n"):
                if foundc:
                    remainder += cline + "\n"
                else:
                    cline = cline.split("#")[0].strip()
                    if cline[-1] != "\\":
                        foundc = True
                        line += cline
                    else:
                        line += cline[:-1]
            cell = remainder.strip()

        # Split the line into arguments for the function and arguments to
        # the dataset.
        if "><" in line:
            line_args, line_fargs = line.split("><")
            fargs = self.extract_in_scope(line_fargs, local_ns)
        else:
            line_args = line
            fargs = None
        args = self.extract_in_scope(line_args, local_ns)

        # Build function string
        fstr = "def f("
        if fargs:
            fstr += ", ".join(list(fargs)) + ", "
        fstr += "):\n"
        for c in cell.split("\n"):
            fstr += "  " + c + "\n"

        return fstr, args, fargs

    def extract_in_scope(self, line: str, local_ns: dict):
        """
        This will convert a line to a dictionary of arguments. 

        It is separated out because we are going to have to selectively
        populate the local scope with `local_ns`.
        """
        def kwargs_to_dict(**kwargs):
            return kwargs

        for k, v in local_ns.items():
            if k in line:
                locals()[k] = v

        return eval("kwargs_to_dict(" + line + ")")
