#!/usr/bin/env python3
import sys

from fovus.cli.cli_action_runner import CliActionRunner
from fovus.cli.fovus_cli_argument_parser import FovusCliArgumentParser

OK_RETURN_STATUS = 0


def main():
    parser = FovusCliArgumentParser()
    parser.parse_args()
    parser.merge_args_with_config()
    cli_action_runner = CliActionRunner(parser.get_args_dict())
    cli_action_runner.run_actions()

    return OK_RETURN_STATUS


if __name__ == "__main__":
    sys.exit(main())
