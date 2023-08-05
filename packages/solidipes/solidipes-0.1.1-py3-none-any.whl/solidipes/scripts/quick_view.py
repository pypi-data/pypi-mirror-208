import argparse

command = "view"
command_help = "generate a view from a file"

################################################################


def main(args):
    """Generate a .py report for the given directory."""
    from .. import viewer_backends
    from ..utils import load_file

    path = args.path
    _file = load_file(path)
    print(_file)

    if viewer_backends.current_backend == "streamlit":
        import streamlit as st

        st.set_page_config(layout="wide")

    _file.view()


def populate_arg_parser(parser):
    parser.description = """Generate view for the given file."""

    parser.add_argument("path", help="Path to file to be viewed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
