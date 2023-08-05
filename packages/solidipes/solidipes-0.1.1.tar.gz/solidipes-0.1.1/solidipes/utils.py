import os

from .config import solidipes_dirname


def load_file(path):
    """Load a file from path into the appropriate object type"""

    import os

    from .loaders.binary import Binary
    from .loaders.code_snippet import CodeSnippet
    from .loaders.geof_mesh import GeofMesh
    from .loaders.image import Image
    from .loaders.pyvista_mesh import PyvistaMesh
    from .loaders.table import Table
    from .loaders.text import Markdown, Text

    # Note: the first matching type is used
    loader_list = [
        Table,
        PyvistaMesh,
        Image,
        Markdown,
        Text,
        CodeSnippet,
        GeofMesh,
    ]

    if not os.path.isfile(path):
        raise FileNotFoundError(f'File "{path}" does not exist')

    for loader in loader_list:
        if loader.check_file_support(path):
            return loader(path)

    # if no extension or unknown extension, assume binary
    file = Binary(path)

    return file


def find_config_directory(initial_path="", dir_name=solidipes_dirname):
    """Find a directory in the current path or any of its parents"""

    import os

    current_path = os.path.abspath(initial_path)

    while True:
        # Check if current path contains the directory
        test_path = os.path.join(current_path, dir_name)
        if os.path.isdir(test_path):
            return test_path

        # Check if current path is the root
        if current_path == os.path.dirname(current_path):
            break

        # Move up to the parent directory
        current_path = os.path.dirname(current_path)

    raise FileNotFoundError(f'The directory "{dir_name}" was not found in {initial_path} or any of its parents')


def get_solidipes_directory(initial_path=""):
    """Get the path to the .solidipes directory"""

    try:
        return find_config_directory(initial_path, solidipes_dirname)

    except FileNotFoundError as e:
        raise FileNotFoundError(f'{e}. Please run "solidipes init" at the root directory of your study.')


def get_study_root_path(initial_path=""):
    import os

    return os.path.dirname(get_solidipes_directory(initial_path))


def get_git_repository(initial_path=""):
    import os

    from git import Repo

    current_path = os.path.abspath(initial_path)
    git_repository = Repo(current_path, search_parent_directories=True)
    return git_repository


def get_git_root(initial_path=""):
    repo = get_git_repository(initial_path)
    git_root = repo.git.rev_parse("--show-toplevel")
    return git_root


def get_config_path(filename_var, initial_path="", check_existence=False):
    import os

    from . import config

    filename = getattr(config, filename_var)

    config_directory = get_solidipes_directory(initial_path)
    path = os.path.join(config_directory, filename)

    if check_existence and not os.path.isfile(path):
        raise FileNotFoundError(
            f'The file "{path}" does not exist. Please run "solidipes init" at the root directory of your study.'
        )

    return path


def load_yaml(filename):
    import yaml

    with open(filename) as f:
        config = yaml.safe_load(f.read())
    if config is None:
        config = {}
    return config


def save_yaml(filename, config):
    import yaml

    with open(filename, "w") as f:
        f.write(yaml.safe_dump(config))

    return config


def get_study_metadata_path(*args, **kwargs):
    return get_config_path("study_metadata_filename", *args, **kwargs)


def get_mimes_path(*args, **kwargs):
    return get_config_path("mimes_filename", *args, **kwargs)


def get_config(filename_var, *args, **kwargs):
    path = get_config_path(filename_var, *args, **kwargs)
    if not os.path.exists(path):
        return {}
    return load_yaml(path)


def set_config(filename_var, config, *args, **kwargs):
    path = get_config_path(filename_var, *args, **kwargs)
    save_yaml(path, config)


def get_study_metadata(*args, **kwargs):
    return get_config("study_metadata_filename", *args, **kwargs)


def set_study_metadata(config, *args, **kwargs):
    set_config("study_metadata_filename", config, *args, **kwargs)


def get_zenodo_infos(*args, **kwargs):
    return get_config("zenodo_infos_filename", *args, **kwargs)


def set_zenodo_infos(config, *args, **kwargs):
    set_config("zenodo_infos_filename", config, *args, **kwargs)


def get_mimes(*args, **kwargs):
    return get_config("mimes_filename", *args, **kwargs)


def set_mimes(config, *args, **kwargs):
    set_config("mimes_filename", config, *args, **kwargs)


def get_ignore(*args, **kwargs):
    from .config import default_ignore_patterns

    ignore = get_config("ignore_filename", *args, **kwargs)
    if not ignore:
        ignore = default_ignore_patterns

    return ignore


def set_ignore(config, *args, **kwargs):
    set_config("ignore_filename", config, *args, **kwargs)
