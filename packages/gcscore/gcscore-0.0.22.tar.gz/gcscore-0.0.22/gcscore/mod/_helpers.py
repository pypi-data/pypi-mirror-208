import importlib.util
import re
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Optional
from jsonpath_ng.ext import parse
from io import StringIO

__all__ = ['TargetFieldQuery', 'import_module', 'compact_script']


@dataclass
class TargetFieldQuery:
    """
    Represent a query using jsonpath to get information from the raw instance.
    """
    key: str
    path: Any
    required: bool = True

    def __post_init__(self):
        self.path = parse(self.path)

    def find(self, obj: dict) -> Optional[Any]:
        """
        Find the query value in the given object or return None.
        :param obj:
        :return:
        """
        result = self.path.find(obj)
        if len(result) > 0:
            return result[0].value
        return None


def import_module(name: str, path: str) -> ModuleType:
    """
    Dynamically import the module from the given path.
    :param name: name of the module
    :param path: path to the module file/directory
    :return: the module
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass
class _CompactScriptPattern:
    comment_line: re.Pattern
    sol_tabs: re.Pattern
    no_semi_colon: re.Pattern
    to_semi_colon: re.Pattern
    final_validation: re.Pattern
    inline_comment_waring: re.Pattern
    duplicated_semi_colons: re.Pattern


COMPACT_SCRIPT_PATTERNS: dict[str, _CompactScriptPattern] = {
    'shell': _CompactScriptPattern(
        comment_line=re.compile(r'^[ \t]*#.*$', re.MULTILINE),
        sol_tabs=re.compile(r'^[\t ]+', re.MULTILINE),
        no_semi_colon=re.compile(r'[ \t]*(then|do|else|in|\{|\()[ \t]*\n'),
        to_semi_colon=re.compile(r'\n+'),
        final_validation=re.compile(r';*(.*);*'),
        inline_comment_waring=re.compile(r'^[ \t]*[^ \t\n#]+.*#[^"\'\n]*$'),
        duplicated_semi_colons=re.compile(r';;+')

    ),
    'powershell': _CompactScriptPattern(
        comment_line=re.compile(r'^[ \t]*#.*$', re.MULTILINE),
        sol_tabs=re.compile(r'^[\t ]+', re.MULTILINE),
        no_semi_colon=re.compile(r'[ \t]*(try|catch|\{|})[ \t]*\n'),
        to_semi_colon=re.compile(r'\n+'),
        final_validation=re.compile(r';*(.*);*'),
        inline_comment_waring=re.compile(r'^[ \t]*[^ \t\n#]+.*#[^"\'\n]*$'),
        duplicated_semi_colons=re.compile(r';;+')
    )
}


def compact_script(language: str, script: str) -> str:
    """
    Compact the script on one line.
    :param language: the script language
    :param script: the not compacted script
    :return: the compacted script
    :raise ValueError: if the language is unknown
    """
    if language not in COMPACT_SCRIPT_PATTERNS:
        raise KeyError(f'Unknown language compaction: "{language}"')

    patterns = COMPACT_SCRIPT_PATTERNS[language]

    for line in script.splitlines():
        if patterns.inline_comment_waring.match(line) is not None:
            print(f'\033[93mWARNING: potential inline comment that will break the compaction:\n> {line}\033[0m')

    script = patterns.comment_line.sub('', script)
    script = patterns.sol_tabs.sub('', script)
    script = patterns.no_semi_colon.sub(r'\g<1> ', script)
    script = patterns.to_semi_colon.sub(';', script)
    script = patterns.duplicated_semi_colons.sub(';', script)
    script = patterns.final_validation.sub(r'\g<1>', script)
    return script
