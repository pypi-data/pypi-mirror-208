import os
from pathlib import Path

from ..config import default_ignore_patterns
from ..utils import get_ignore, load_file


def split_all_path(path):
    head, tail = os.path.split(path)
    _split = [tail]
    path = head
    while path:
        head, tail = os.path.split(path)
        _split.insert(0, tail)
        path = head
    return _split


class Scanner:
    def __init__(self):
        try:
            # Get ignored patterns from .solidipes
            self.excluded_patterns = get_ignore()
        except FileNotFoundError:
            self.excluded_patterns = default_ignore_patterns.copy()

    def scan_dirs(self, paths, recursive=True):
        res = {}
        for p in paths:
            split_p = split_all_path(p)
            _res = res
            for _dir in split_p:
                if _dir not in _res:
                    _res[_dir] = {}
                _res = _res[_dir]
            s = self.scan_dir(p, recursive=recursive)
            _res.update(s)
        return res

    def scan_dir(self, path, recursive=True, scan_files=True):
        found_files = {}

        for f in os.listdir(path):
            fname = os.path.join(path, f)

            if self.is_excluded(fname):
                continue

            if os.path.isdir(fname):
                if recursive:
                    scan = self.scan_dir(os.path.join(path, f), scan_files=scan_files)
                    found_files.update({f: scan})
                continue

            if not scan_files:
                continue

            _file = load_file(fname)
            found_files.update({f: _file})

        return found_files

    def is_excluded(self, path):
        p = Path(path)

        for pattern in self.excluded_patterns:
            # If the pattern ends with a trailing slash, test whether the path
            # is a directory
            if pattern.endswith("/"):
                if p.match(pattern) and p.is_dir():
                    return True

            # Otherwise, only test whether the path matches the pattern
            else:
                if p.match(pattern):
                    return True

        return False

    def scan(self, uri, scan_files=True):
        return self.scan_dir(uri, scan_files=scan_files)


def for_each_file(found, current_dir=""):
    items = []
    for k, v in found.items():
        full_dir = os.path.join(current_dir, k)
        items.append((full_dir, v))
        if isinstance(v, dict):
            items += for_each_file(v, current_dir=full_dir)
    return items
