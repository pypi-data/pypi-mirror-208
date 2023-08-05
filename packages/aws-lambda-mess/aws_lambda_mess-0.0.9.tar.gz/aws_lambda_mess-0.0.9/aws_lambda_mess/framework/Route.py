import re

# This routine replaces <variable> with a regex to extract the variable into a named group
# somethinmg like this f"(?P<{key}>[a-zA-Z0-9]*)"
#
def replace_with_regex(pattern):
    match = re.findall("<([a-zA-Z0-9_]*)>", pattern)
    for key in match:
        pattern = pattern.replace(f"<{key}>", f"(?P<{key}>[a-zA-Z0-9\\-_]*)")
    return "(/.*?)?" + pattern + ("?" if pattern.endswith("/") else "/?")


class Route:
    def __init__(self, method_pattern, path_pattern, handler):
        self.method_pattern = method_pattern
        self.path_pattern = replace_with_regex(path_pattern)
        self.handler = handler

    def match(self, method, path):
        method_match = re.fullmatch(self.method_pattern, method)
        if method_match is None:
            return False, None

        path_match = re.fullmatch(self.path_pattern, path)
        if path_match is None:
            return False, None

        return True, path_match.groupdict()

    def run(self, params, body):
        return self.handler(params, body)
