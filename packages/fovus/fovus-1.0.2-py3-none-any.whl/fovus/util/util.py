import os

BYTES_IN_MEGABYTE = 1024**2
BYTES_IN_GIGABYTE = 1024**3

UNIX_OS_NAME = "posix"
WINDOWS_OS_NAME = "nt"


class Util:
    @staticmethod
    def convert_bytes_to_megabytes(file_size_bytes):
        return file_size_bytes / BYTES_IN_MEGABYTE

    @staticmethod
    def convert_bytes_to_gigabytes(file_size_bytes):
        return file_size_bytes / BYTES_IN_GIGABYTE

    @staticmethod
    def is_unix():
        return os.name == UNIX_OS_NAME

    @staticmethod
    def is_windows():
        return os.name == WINDOWS_OS_NAME
