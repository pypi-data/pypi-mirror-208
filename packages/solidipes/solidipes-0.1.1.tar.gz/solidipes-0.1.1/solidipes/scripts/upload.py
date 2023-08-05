import argparse
import os

from ..config import study_medatada_mandatory_fields as mandatory_fields
from ..config import study_metadata_filename, zenodo_infos_filename
from ..zenodo_utils import (
    ZenodoException,
    clean_deposition,
    create_deposition,
    get_access_token,
    get_existing_deposition_identifier,
    get_existing_deposition_infos,
    save_deposition_identifier,
    update_deposition_metadata,
    upload_archive,
)

command = "upload"
command_help = "upload study to Zenodo"

removed_fields = [
    "access_right_category",
    "doi",
    "publication_date",
    "relations",
]


def main(args):
    """Upload content to Zenodo"""

    from ..utils import get_study_root_path

    try:
        if args.directory is None:
            root_directory = get_study_root_path()
        else:
            root_directory = args.directory

        # Check if the directory exists
        if not os.path.isdir(root_directory):
            raise ValueError(f"Error: directory {root_directory} does not exist")

        # Check if the metadata file exists and load it
        metadata = load_and_check_metadata(root_directory)

        # Zip directory into temporary file
        archive_path, temp_dir = create_archive(root_directory)

        access_token = get_access_token()

        deposition_url, bucket_url, _ = get_cleaned_deposition_infos(
            args.new_deposition, args.existing_identifier, access_token, args.sandbox, root_directory
        )

        update_deposition_metadata(deposition_url, metadata, access_token)

        def text_progress_bar(filename, size):
            from tqdm import tqdm

            bar = tqdm(
                desc=filename,
                total=size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            )
            return bar

        upload_archive(
            bucket_url,
            archive_path,
            access_token,
            progressbar=text_progress_bar,
        )

        # Final message
        print("Upload complete.")
        print("Please review your deposition and publish it when ready.")

        # Remove temporary file
        temp_dir.cleanup()

    except Exception as e:
        if type(e) is not ZenodoException:
            raise e

        print(e)

        if "has been deleted" in str(e) or "does not exist" in str(e):
            print(
                'Run the command with the "--new-deposition" option to create'
                ' a new entry, or the "--existing-deposition" option to use'
                " another existing entry."
            )

        if "Error deleting file" in str(e):
            print("Please check that the deposition is in draft state.")

        return


def load_and_check_metadata(dir_path):
    """Load/create metadata file and check if mandatory fields are present"""

    from ..utils import get_study_metadata, get_study_metadata_path

    metadata = get_study_metadata(initial_path=dir_path, check_existence=True)
    metadata_path = get_study_metadata_path(initial_path=dir_path)

    # Check if mandatory fields are present
    for field in mandatory_fields:
        if field not in metadata or not metadata[field]:
            raise ValueError(
                f'Error: field "{field}" is missing from metadata file. Please edit {metadata_path} and try again.'
            )

    # Check that creators is a list
    if type(metadata["creators"]) != list:
        raise ValueError(f'Error: field "creators" must be a list. Please edit {metadata_path} and try again.')

    # Check that each creator has a name
    for creator in metadata["creators"]:
        if "name" not in creator or not creator["name"]:
            raise ValueError(
                f'Error: field "name" is missing from one of the creators. Please edit {metadata_path} and try again.'
            )

    # Clean
    for field in removed_fields:
        if field in metadata:
            del metadata[field]

    if "related_identifiers" in metadata:
        for related_identifier in metadata["related_identifiers"]:
            if "relation" in related_identifier and related_identifier["relation"] == "isVersionOf":
                related_identifier["relation"] = "isNewVersionOf"

    return metadata


def create_archive(dir_path, _print=print):
    """Create a temporary zip archive of the directory"""

    import tempfile
    import zipfile

    from ..config import solidipes_dirname
    from ..scanners.scanner import Scanner
    from ..utils import get_ignore

    temp_dir = tempfile.TemporaryDirectory()
    dir_name = os.path.basename(os.path.normpath(dir_path))
    archive_name = dir_name if dir_name != "." else "archive"
    archive_path = os.path.join(temp_dir.name, f"{archive_name}.zip")
    _print(f"Creating archive {archive_path}...")

    scanner = Scanner()
    scanner.excluded_patterns = get_ignore(initial_path=dir_path)
    # Remove .solidipes from excluded patterns
    if solidipes_dirname in scanner.excluded_patterns:
        scanner.excluded_patterns.remove(solidipes_dirname)
    # Add Zenodo metadata file and Zenodo infos file to excluded patterns
    scanner.excluded_patterns.append(os.path.join(solidipes_dirname, study_metadata_filename))
    scanner.excluded_patterns.append(os.path.join(solidipes_dirname, zenodo_infos_filename))

    with zipfile.ZipFile(archive_path, "w") as zip_file:
        for current_dir, sub_dirs, files in os.walk(dir_path):
            # Remove excluded dirs (except .solidipes, which can be matched to ".*")
            sub_dirs[:] = [
                d for d in sub_dirs if (not scanner.is_excluded(os.path.join(current_dir, d))) or d == solidipes_dirname
            ]

            if current_dir != dir_path:  # prevent addition of "."
                zip_file.write(current_dir, os.path.relpath(current_dir, dir_path))

            for filename in files:
                path = os.path.join(current_dir, filename)

                # Exclude files
                if scanner.is_excluded(path):
                    continue

                zip_file.write(
                    path,
                    os.path.relpath(path, dir_path),
                )

    return archive_path, temp_dir


def get_cleaned_deposition_infos(new_deposition, existing_identifier, access_token, sandbox, root_directory="."):
    """Get deposition urls

    If no deposition has been created yet, or if new_deposition is True, create a new deposition.
    Otherwise, the saved deposition or the one specified by existing_identifier is used.
    """

    deposition_identifier = None
    # Get existing deposition identifier, if any
    if existing_identifier:
        deposition_identifier = existing_identifier
    elif not new_deposition:
        # Otherwise, load saved identifier
        deposition_identifier = get_existing_deposition_identifier(root_directory)

    if deposition_identifier:
        # Update existing record
        deposition_url, bucket_url, web_url = get_existing_deposition_infos(
            deposition_identifier, access_token, sandbox
        )
        print(f"Updating deposition at {web_url}")
        # Delete current files
        clean_deposition(deposition_url, access_token)

    else:
        # Create deposition
        deposition_url, bucket_url, web_url = create_deposition(access_token, sandbox)
        print(f"Deposition created: {web_url}")

    # Save deposition identifier if successfully created or accessed
    save_deposition_identifier(web_url, root_directory)

    return deposition_url, bucket_url, web_url


def populate_arg_parser(parser):
    parser.description = """Upload content to Zenodo"""

    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help=(
            "Path to the directory containing the study to upload. Defaults to the root of the current Solidipes study."
        ),
    )

    parser.add_argument(
        "--sandbox",
        help="use Zenodo sandbox test platform",
        action="store_true",
    )

    deposition_group = parser.add_mutually_exclusive_group()

    deposition_group.add_argument(
        "--new-deposition",
        help="create a new deposition instead of updating a previously created one",
        action="store_true",
    )

    deposition_group.add_argument(
        "--exising-deposition",
        dest="existing_identifier",
        nargs="?",
        help="URL or DOI of the study to update. It must be in unplublished state.",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
