import sys
import json
from marko.ext.gfm import gfm as markdown


def trim(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


def build_html(structure):

    html = f'<div class="{structure["type"]}" id="{structure["id"]}">'
    html += markdown.render(structure.get('description') or '')
    if 'children' in structure and structure['children']:
        for child_structure in structure['children']:
            html += build_html(child_structure)
    html += '</div>'
    return html


class ExtendedEncoder(json.JSONEncoder):

    def default(self, obj):
        if callable(obj):
            return obj.__name__
        return super().default(obj)