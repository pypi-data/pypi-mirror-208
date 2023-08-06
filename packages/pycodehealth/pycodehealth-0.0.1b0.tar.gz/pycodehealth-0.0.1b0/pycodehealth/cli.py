"""
Module that would implement all the other modules to be used
as the default CI Tools by the user
"""
from typing import List, Union, Tuple, Dict, Optional, Callable
import click
import attr
# Local imports
from .tools import PylintRunner, TypeChecker


@attr.s(slots=True)
class PyCITools:
    """Module to be used to call the PyCI Tools"""

    def cli(self) -> None:
        """Command Line Application to perform CI analysis."""

    @property
    def tools(self) -> Callable:
        """Method to return the method grouped by the CLI"""
        # Create the group method
        group = click.group()(self.cli)
        # Obtain the arguments for each tool/method
        args_per_tool = self.__args()
        # Now, start parsing the methods
        for command, c_name in [(self.__pylint, 'pylint'), (self.__mypy, 'mypy'), (self.__all, 'all')]:
            group.add_command(self.__parse_args(command, command_name=c_name,
                                                args=args_per_tool[c_name]))
        # Return the group at the end
        return group

    def __args(self) -> Dict[str, List[Tuple[str, str, Optional[str]]]]:
        """Method to generate a dict with the args for each tool."""
        # Pre-generate a template using the -files and -folder arguments
        arg_template: List[Tuple[str, str, Optional[str]]] = [
            ('-fi', '--files', 'Files to review. Can be a list, tuple or single file.'),
            ('-fo', '--folder', 'Directory to check all the files inside it.')
        ]
        arg_per_tool: Dict[str, List[Tuple[str, str, Optional[str]]]] = {
            'template': arg_template}
        # Now, iterate over each tool
        for tool in ['pylint', 'mypy', 'all']:
            arg_per_tool[tool] = arg_template
        return arg_per_tool

    def __parse_args(self, function: Callable, command_name: str,
                     args: List[Tuple[str, str, Optional[str]]]) -> click.Command:
        """Method to return a callable with the specified arguments using
        the 'click.arguments' method"""
        command = click.command(name=command_name)(function)
        for arg in args:
            click.option(arg[0], arg[1], help=arg[2])(command)
        return command

    # ---------------------------------------------------------------- #
    #                      COMMANDS FOR THE TOOLS                      #
    # ---------------------------------------------------------------- #

    def __pylint(self, files: Optional[Union[List[str], str]] = None, folder: Optional[str] = None) -> None:
        """Perform a static analysis of a given files using the linter 'Pylint'.

        Args:\n
        -----------------------------------------\n
            - files (Optional[[str] | str]): Files to apply the analysis.\n
            - folder (Optional[str]): Directory to check all the files inside it.\n
        """
        PR = PylintRunner()
        PR.set_inputs(files, folder)
        PR.run()

    def __mypy(self, files: Optional[Union[List[str], str]] = None, folder: Optional[str] = None) -> None:
        """Perform a static analysis of the given files using the typing checker 'mypy'.

        Args:\n
        -----------------------------------------\n
            - files (Optional[[str] | str]): Files to apply the analysis.\n
            - folder (Optional[str]): Directory to check all the files inside it.\n
        """
        TC = TypeChecker()
        TC.set_inputs(files, folder)
        TC.run()

    def __all(self, files: Optional[Union[List[str], str]] = None, folder: Optional[str] = None) -> None:
        """Perform a static analysis using all the available commands (pylint, mypy)

        Args:\n
        -----------------------------------------\n
            - files (Optional[[str] | str]): Files to apply the analysis.\n
            - folder (Optional[str]): Directory to check all the files inside it.\n
        """
        for method in [self.__pylint, self.__mypy]:
            method(files, folder)


# So it can be callable
PCT = PyCITools()
tools = PCT.tools
