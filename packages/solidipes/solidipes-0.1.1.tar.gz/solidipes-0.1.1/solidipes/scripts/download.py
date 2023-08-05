import argparse
import os

from ..zenodo_utils import ZenodoException, check_response, download_files, get_host_and_id

command = "download"
command_help = "download study from Zenodo"


def main(args):
    """Download content from Zenodo"""

    import requests

    from ..utils import set_study_metadata
    from .init import create_solidipes_directory

    try:
        host, study_id = get_host_and_id(args.identifier)
        url = f"https://{host}/api/records/{study_id}"

        # Scan record
        response = requests.get(url)
        check_response(response, 200, "retrieve record")
        record = response.json()

        print(f"Retrieving study {study_id} from {host}...")

        # Create destination folder if it does not exist
        if not os.path.exists(args.destination):
            os.makedirs(args.destination)

        # Create Solidipes directory if it does not exist
        try:
            create_solidipes_directory(args.destination)
        except FileExistsError:
            pass

        # Save metadata in YAML file
        print("Saving metadata...")
        metadata = process_metadata(record["metadata"])
        set_study_metadata(metadata, initial_path=args.destination)

        if args.only_metadata:
            return

        download_files(record, destination=args.destination, progressbar=True)

    except Exception as e:
        if type(e) is not ZenodoException:
            raise e

        print(e)
        return


def process_metadata(metadata):
    """Process metadata to make dataset uploadable again"""

    if "upload_type" not in metadata:
        if "resource_type" in metadata:
            metadata["upload_type"] = metadata["resource_type"]["type"]
            del metadata["resource_type"]
        else:
            metadata["upload_type"] = "dataset"

    if "journal" in metadata:
        journal = metadata["journal"]
        for field in ["title", "volume", "issue", "pages"]:
            if field in journal:
                metadata[f"journal_{field}"] = journal[field]
        del metadata["journal"]

    return metadata


def populate_arg_parser(parser):
    parser.description = """Download content from Zenodo"""

    parser.add_argument("identifier", help="URL or DOI of the study to download")

    parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Path to the destination folder",
    )

    parser.add_argument(
        "--only-metadata",
        help="Only download metadata (overrides destination directory's metadata!)",
        action="store_true",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
