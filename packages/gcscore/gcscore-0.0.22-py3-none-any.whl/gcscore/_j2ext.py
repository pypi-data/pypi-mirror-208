import re
from typing import Union, Callable, Protocol

from jinja2.ext import Extension
from jinja2.nodes import Node, CallBlock
from jinja2.parser import Parser
from jinja2 import Environment, Undefined

__all__ = ['ScriptTemplatesExtension']

DEFAULT_PATTERN_COMMENTED_LINE = re.compile(r'^ *#')
DEFAULT_SCRIPTS_SPLITTER = '\n\n\n'


class CommandRenderer(Protocol):
    def render_command(self, command: str, environment: Environment) -> str: ...


class ScriptTemplatesExtension(Extension):
    """
    Allow the use of templated scripts from a command line like call.
    """

    tags = {'commands'}

    _configuration_consumed: bool = True
    _commands_renderer: CommandRenderer = Undefined
    _script_splitter: str = Undefined

    @classmethod
    def configure(cls,
                  commands_renderer: CommandRenderer,
                  script_splitter: str = DEFAULT_SCRIPTS_SPLITTER
                  ):
        """
        Method to call before initializing a new Jinja2 environment with this extension
        :param script_splitter: string that will be put between the rendered commands in the final script
        :param commands_renderer: the CommandRenderer that will render the commands
        """
        cls._configuration_consumed = False
        cls._commands_renderer = commands_renderer
        cls._script_splitter = script_splitter

    def __init__(self, environment: Environment):
        if self._configuration_consumed:
            raise AttributeError(f'ScriptTemplatesExtension.configure(...) must be called '
                                 f'before initializing a new jinja2 environment')
        self._consume_configuration()
        super().__init__(environment)

    def _consume_configuration(self):
        self._commands_renderer = self.__class__._commands_renderer
        self._script_splitter = self.__class__._script_splitter
        self.__class__._configuration_consumed = True

    def parse(self, parser: Parser) -> Union[Node, list[Node]]:
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(('name:endcommands',), drop_needle=True)
        return CallBlock(
            self.call_method('_render_commands'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _render_commands(self, caller: Callable[[], str]) -> str:
        content = caller().removeprefix('\n')
        final_content = []
        for line in content.splitlines():
            rendered_script = self._commands_renderer.render_command(line, self.environment)
            if rendered_script is not None:
                final_content.append(rendered_script)

        return self._script_splitter.join(final_content)
