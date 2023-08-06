import os
import re
import time
from http import HTTPStatus
from math import trunc

from fovus.constants.cli_constants import PASSWORD_ENVIRONMENT_VARIABLE_KEY, TIMESTAMP
from fovus.exception.user_exception import UserException

MILLISECONDS_IN_SECOND = 1000


class FovusCliArgumentParserUtil:
    @staticmethod
    def validate_password_exists():
        if not os.environ.get(PASSWORD_ENVIRONMENT_VARIABLE_KEY):
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                FovusCliArgumentParserUtil.__name__,
                f"Password must be set in environment variable {PASSWORD_ENVIRONMENT_VARIABLE_KEY}."
                + "\nTo set on Unix-based systems, run the following command: "
                + f'export {PASSWORD_ENVIRONMENT_VARIABLE_KEY}="your_password_here"'
                + "\nTo set on Windows, run the following command then close and reopen command prompt: "
                + f'setx {PASSWORD_ENVIRONMENT_VARIABLE_KEY} "your_password_here"',
            )

    @staticmethod
    def get_password():
        return os.environ.get(PASSWORD_ENVIRONMENT_VARIABLE_KEY)

    @staticmethod
    def camel_to_snake(camel_case_str):
        uppercase_letters = "([A-Z])"
        snake_case_regex_substitution = r"_\1"
        snake_case_str = re.sub(uppercase_letters, snake_case_regex_substitution, camel_case_str).lower()
        if snake_case_str.startswith("_"):
            snake_case_str = snake_case_str[1:]
        return snake_case_str

    @staticmethod
    def key_isnt_password(key):
        return key != "password"

    @staticmethod
    def set_timestamp(cli_dict):
        cli_dict[TIMESTAMP] = str(trunc(time.time() * MILLISECONDS_IN_SECOND))
        return cli_dict[TIMESTAMP]
