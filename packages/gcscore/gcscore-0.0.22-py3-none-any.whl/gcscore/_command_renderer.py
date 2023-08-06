import shlex
from argparse import ArgumentParser
from functools import partial
from pathlib import Path
from pydoc import locate  # NOQA
from typing import Optional

import toml
from jinja2 import Environment, TemplateNotFound, Template

from ._commons import ParserError
from ._error_history import ErrorHistory

__all__ = ['CommandRenderer']


class CommandRenderer:
    """
    Contains the logic for the parsing of commands in the GCS package.
    """

    def __init__(self):
        self.cached_argument_parsers: dict[str, ArgumentParser] = {}
        self.errors_history = ErrorHistory()

    def render_command(self, command_raw: str, environment: Environment) -> Optional[str]:
        """
        Render the given command. The encountered errors are stored in the error_history to be processed later.
        :param command_raw: raw command line: "{path/to/template} [args]..."
        :param environment: jinja2 environment
        :return: the rendered script or None in case of error(s).
        """
        command = shlex.split(command_raw, comments=True, posix=True)
        if len(command) == 0:
            return None

        template_name = command.pop(0)

        arguments = self.parse_arguments(template_name, command, environment)
        if arguments is None:
            return None

        template = self.get_template(template_name, environment)
        if template is None:
            return None

        return template.render(**arguments)

    def get_template(self, template_name: str, environment: Environment) -> Optional[Template]:
        """
        Get the template. Error(s) are stored in the error_history attribute.
        :param template_name: the template to get
        :param environment: the jinja2 environment
        :return: the template or None in case of error(s)
        """
        try:
            template = environment.get_template(template_name)
            return template
        except TemplateNotFound as ex:
            self.errors_history.append(ex)
            return None

    def parse_arguments(self, template_name: str, arguments: list[str], environment: Environment) -> Optional[dict]:
        """
        Parse the given argument for the given template. The errors are stored in the error_history.
        :param environment: the jinja2 environment
        :param template_name: the template name
        :param arguments: the list of arguments to parse
        :return: the arguments dictionary or None in case of errors
        """
        parser: ArgumentParser = self.get_parser(template_name, environment)

        try:
            arguments = parser.parse_args(arguments)
            return arguments.__dict__
        except ParserError as ex:
            self.errors_history.append(ex)
            return None

    def get_parser(self, template_name: str, environment: Environment) -> ArgumentParser:
        """
        Get or create the parser for the template name.
        :param environment: the jinja2 environment
        :param template_name: the template name
        :return: the argument parser
        """
        if template_name in self.cached_argument_parsers:
            return self.cached_argument_parsers[template_name]

        configuration = CommandRenderer.get_configuration(template_name, environment)
        parser = CommandRenderer.create_parser(configuration, template_name)
        self.cached_argument_parsers[template_name] = parser
        return parser

    @staticmethod
    def create_parser(configuration: dict, template_name: str) -> ArgumentParser:
        """
        Create the parser from the given configuration.
        :param configuration: the arguments configuration
        :param template_name: the template's name associated to the parser
        :return: the argument parser
        """
        parser = ArgumentParser(prog=template_name, exit_on_error=False)
        parser.description = configuration.get('description', '')
        parser.error = partial(handle_parser_error, parser=parser)

        for argument_config in configuration.get('argument', []):
            names, argument_config = CommandRenderer.prepare_argument_config(template_name, argument_config)
            parser.add_argument(*names, **argument_config)
        return parser

    @staticmethod
    def prepare_argument_config(template_name: str, argument_config: dict) -> tuple[list[str], dict]:
        """
        Make sure the argument configuration can be used.
        :param template_name: the template's name
        :param argument_config: the argument configuration
        :return: the argument's names, the argument configuration
        """
        # Get names
        if not (('name' in argument_config) ^ ('names' in argument_config)):
            raise KeyError(f'{template_name}.toml: invalid keys "name" and "names". '
                           f'It is either missing or both keys are specified (only one must be set)')
        names = None
        if 'name' in argument_config:
            names = [argument_config.pop('name')]
        if 'names' in argument_config:
            names = argument_config.pop('names')

        # Fix the argument info with defaults
        action = argument_config.get('action')
        # Set default type if the action accepts type parameter.
        if action not in ['store_true', 'store_false', 'store_const', 'append_const']:
            argument_config['type'] = locate(argument_config.get('type', 'str'))

        # Return the prepared configuration
        return names, argument_config

    @staticmethod
    def get_configuration(template_name: str, environment: Environment) -> dict:
        """
        Retrieve the configuration from the template's associated toml file or an empty dictionary.
        :param environment: the jinja2 environment
        :param template_name: the template's name
        :return: the loaded configuration
        """
        try:
            config_filename = environment.get_template(template_name + '.toml').filename
            config_path = Path(config_filename)
            return toml.loads(config_path.read_text())
        except TemplateNotFound:
            return {}


def handle_parser_error(message: str, parser: ArgumentParser):
    """
    Handle the exit_on_error not working issue of the argparse package.
    :param message: the message of the error
    :param parser: the parser calling the error
    :raise ParserError: everytime
    """
    raise ParserError(f'{parser.prog}: {message}')
