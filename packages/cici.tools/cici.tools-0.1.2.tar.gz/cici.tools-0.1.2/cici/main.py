import argparse
from pathlib import Path

from .cli.bundle import bundle_command
from .cli.update import update_command


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(required=True)

    parser_bundle = subparsers.add_parser(
        "bundle", help="distill a CI file to a job and its dependencies"
    )
    parser_bundle.add_argument(
        "config_path",
        metavar="DIR",
        nargs="?",
        type=Path,
        default=(Path.cwd() / ".cici").absolute(),
    )
    parser_bundle.add_argument(
        "-a",
        "--all",
        dest="include_hidden_jobs",
        action="store_true",
        help="include hidden jobs in output",
    )
    parser_bundle.add_argument("-g", "--groups", help="job group patterns")
    parser_bundle.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        dest="output_path",
        type=Path,
        default=Path.cwd().absolute(),
    )
    parser_bundle.add_argument(
        "-p",
        "--pipeline",
        metavar="DIR",
        dest="pipeline_name",
        default=str(Path.cwd().name),
    )
    parser_bundle.set_defaults(func=bundle_command)

    parser_update = subparsers.add_parser("update")
    parser_update.add_argument("filename", nargs="?", default=".gitlab-ci.yml")
    parser_update.set_defaults(func=update_command)

    args = parser.parse_args()
    args.func(args)
