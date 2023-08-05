import argparse

command = "init"
command_help = "Initialize a study directory with Solidipes"


def main(args):
    from ..utils import get_study_root_path

    if not args.force:
        try:
            root_directory = get_study_root_path(args.directory)

            # No exception: directory already exists, warn user and exit
            print(
                "The directory is already inside a Solidipes study directory,"
                f' whose root is "{root_directory}". Run the command with'
                ' "--force" to initialize anyway.'
            )
            return

        except FileNotFoundError:
            # No solidipes directory
            pass

    create_solidipes_directory(args.directory, args.force)
    create_metadata_file(args.directory)
    create_ignore_file(args.directory)


def create_solidipes_directory(root_directory, force=False):
    import os

    from ..config import solidipes_dirname

    config_directory = os.path.join(root_directory, solidipes_dirname)

    # If the directory alredy exists, force remove it
    if force and os.path.isdir(config_directory):
        import shutil

        shutil.rmtree(config_directory)

    os.mkdir(config_directory)
    print(f'Created directory "{config_directory}"')

    return config_directory


def create_metadata_file(root_directory):
    """Create a metadata file with empty required fields"""

    from ..config import study_medatada_mandatory_fields as mandatory_fields
    from ..utils import get_study_metadata_path, set_study_metadata

    metadata = {}

    # Add empty mandatory fields
    for field in mandatory_fields:
        metadata[field] = ""
    metadata["creators"] = [{"name": "", "affiliation": ""}]
    metadata["keywords"] = []
    metadata["upload_type"] = "dataset"

    # Write to file
    set_study_metadata(metadata, initial_path=root_directory)
    metadata_path = get_study_metadata_path(initial_path=root_directory)

    print(
        f"Metadata file {metadata_path} created. For publication to Zenodo,"
        " please consult https://developers.zenodo.org/#representation under"
        ' "Deposit metadata" for more information about the available and'
        " required fields."
    )


def create_ignore_file(root_directory):
    """Create default ignore file"""

    from ..config import default_ignore_patterns
    from ..utils import set_ignore

    set_ignore(default_ignore_patterns, initial_path=root_directory)


def populate_arg_parser(parser):
    parser.description = command_help

    parser.add_argument(
        "directory",
        nargs="?",
        default="",
        help="Path to the directory to initialize. Defaults to the current directory.",
    )

    parser.add_argument(
        "--force",
        help=(
            "Force the creation of solidipes configuration files in the"
            " current directory. WARNING: This could erase an existing"
            " .solidipes directory!"
        ),
        action="store_true",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
