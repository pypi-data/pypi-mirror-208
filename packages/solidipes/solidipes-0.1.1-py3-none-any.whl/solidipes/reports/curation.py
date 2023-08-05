import fnmatch
import os
import subprocess

from solidipes.loaders.file import File
from solidipes.loaders.mime_types import get_possible_extensions
from solidipes.scanners.scanner import Scanner, for_each_file

command = "report"
command_help = "generate report from directory"
################################################################


def display_dir(d, content):
    found_files = False
    for k, v in content.items():
        if isinstance(v, File):
            found_files = True

    if found_files:
        print(f"Directory: {d}")


################################################################


def scan_directories(scanner, dir_path, **_kwargs):
    h = scanner.scan(dir_path)
    for fname, _file in for_each_file(h):
        name = os.path.join(dir_path, fname)
        if os.path.isdir(name):
            display_dir(fname, _file)
        else:
            display_file(_file)


################################################################


def display_file(e, file_wildcard="*", rename=False, _open=False):
    path = e.file_info.path
    if not fnmatch.fnmatch(e.file_info.path, file_wildcard):
        return

    file_title = f"{os.path.abspath(path)}"
    if e.valid_extension():
        file_title += ": ok"
        print(f"{file_title}")
    else:
        file_title = file_title + ":0: "
        file_title += "mismatch extension-mimetype:"
        file_title += f" {e.file_info.type.strip()}"
        print(f"{file_title}")
        if _open:
            subprocess.call(f"emacs {e.file_info.path}", shell=True)
        if rename:
            old_name = e.file_info.path
            ext = get_possible_extensions(e.file_info.type)[0]
            new_name = os.path.splitext(old_name)[0] + "." + ext
            cmd = f"git mv  {old_name} {new_name}"
            print(cmd)
            subprocess.call(cmd, shell=True)

    # e.view()


################################################################


def make(dir_path, options=[]):
    file_wildcard = "*"
    rename = False
    _open = False
    for o in options:
        if o.startswith("--file_wildcards="):
            file_wildcard = o.lstrip("--file_wildcards=")
        if o.startswith("--rename"):
            rename = True
        if o.startswith("--open"):
            _open = True

    print(f'Generating JTCAM report for "{dir_path}"')
    s = Scanner()
    scan_directories(s, dir_path, file_wildcard=file_wildcard, rename=rename, _open=_open)


################################################################
if __name__ == "__main__":
    make("./")
