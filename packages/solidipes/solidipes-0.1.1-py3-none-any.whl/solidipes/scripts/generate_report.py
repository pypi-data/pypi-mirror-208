import argparse
import importlib
import pkgutil

import solidipes.reports

command = "report"
command_help = "generate report from directory"

################################################################


def main(args):
    """Generate a .py report for the given directory."""
    dir_path = args.dir_path
    report_type = args.report_type
    report_module = importlib.import_module(f"solidipes.reports.{report_type}")
    report_module.make(dir_path, args.additional_arguments)


def get_report_types():
    """Return a list of available report types."""
    return [module.name for module in pkgutil.iter_modules(solidipes.reports.__path__)]


def populate_arg_parser(parser):
    parser.description = """Generate a .py report for the given directory."""

    parser.add_argument(
        "report_type",
        choices=get_report_types(),
        help="The report to generate",
    )

    parser.add_argument("dir_path", help="Path to directory containing data files")

    parser.add_argument(
        "additional_arguments",
        nargs=argparse.REMAINDER,
        help="Arguments to forward to the report",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
