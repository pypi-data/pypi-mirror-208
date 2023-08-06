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

        def clean_line(inpstr: str) -> str:
            return inpstr.split("#")[0].strip().strip(",")

        # split cell into sanzu args, function args and the actual cell content
        sanzu = [clean_line(line)]  # prime sanzu storage with initial line
        sargs = []
        cell_actual = []

        for line in cell.split("\n"):
            if line.startswith("%%"):
                if "sanzu" in line:
                    sanzu.append(clean_line(line.split("sanzu ")[-1]))
                elif "sargs" in line:
                    sargs.append(clean_line(line.split("sargs ")[1]))
            else:
                cell_actual.append(line)

        self._logger.info(f"sanzu: {sanzu}")
        self._logger.info(f"sargs: {sargs}")
        self._logger.info(f"cell: {cell_actual}")

        fstr = self.parse_line(cell_actual, sargs)

        args = self.extract_in_scope(",".join(sanzu), local_ns)
        fargs = self.extract_in_scope(",".join(sargs), local_ns)

        self._logger.info(f"generated function string {fstr}")
        self._logger.info(f"Dataset args: {args}")
        self._logger.info(f"Function args: {fargs}")
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

    def parse_line(self, cell: list, fargs: list):
        """
        Generate a callable function from the remaining cell content

        Args:
            cell:
                (list): cell content
            fargs:
                (list): function arguments

        Returns:
            (str): formatted function string
        """
        cell = [line for line in cell if line != ""]

        fstr = ["def f("]

        if len(fargs) > 0:
            # if we have fargs, they will be in a list of name = value
            # we only need the name portion
            tmp = []
            for arg in fargs:
                if "=" in arg:
                    tmp.append(arg.split("=")[0].strip())
                else:
                    tmp.append(arg.strip())

            fstr[0] += ", ".join(list(tmp)) + ", "

        fstr[0] += "):"

        fstr += [f"\t{line}" for line in cell]

        fstr = "\n".join(fstr)
        # Validate the function string and add a return
        fstr = self.add_return(fstr)

        return fstr

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

    def add_return(self, fstr):
        """
        This routine adds a return to the end of our generated function.
        """
        import ast

        tree = ast.parse(fstr)
        node = tree.body[0]
        if isinstance(node.body[-1], ast.Expr):
            node.body[-1] = ast.Return(value=node.body[-1].value)
        return ast.unparse(tree)
