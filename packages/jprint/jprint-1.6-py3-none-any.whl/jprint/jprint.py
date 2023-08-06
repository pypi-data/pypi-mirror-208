#!/usr/bin/env python

import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from typing import Union


def format(obj: Union[dict, str], **kwargs) -> str:
    """
    Set sensible defaults for json.dumps
    """
    kwargs["indent"] = kwargs.get("indent", 4)
    kwargs["default"] = kwargs.get("default", str)
    kwargs["sort_keys"] = kwargs.get("sort_keys", True)
    return json.dumps(obj, **kwargs)


def jprint(obj: Union[dict, list, tuple, set, str], **kwargs):
    """
    Pretty print Python dictionaries, lists, and JSON strings.
    If str is not valid json it will be printed as is.
    """
    if isinstance(obj, tuple):
        obj = list(obj)

    if isinstance(obj, (dict, list, tuple, set)):
        json_str = format(obj, **kwargs)
    else:
        try:
            json_str = format(json.loads(obj), **kwargs)
        except json.JSONDecodeError:
            json_str = format(obj, **kwargs)

    colorized_json = highlight(json_str, JsonLexer(), TerminalFormatter())
    print(colorized_json)
