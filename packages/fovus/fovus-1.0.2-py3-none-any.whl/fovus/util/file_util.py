import fnmatch
import hashlib
import os
from http import HTTPStatus

from fovus.exception.user_exception import UserException
from fovus.util.util import Util

FOVUS_JOB_INFO_FOLDER = ".fovus"


class FileUtil:
    @staticmethod
    def get_files_in_directory(root_directory_path, include_input_list, exclude_input_list):
        local_filepath_list = []
        tasks = set()
        total_file_size_bytes = 0
        for directory_path, _dirs, files in os.walk(root_directory_path):
            for file in files:
                local_filepath = os.path.join(directory_path, file)
                if FileUtil.should_ignore_path(file) or not FileUtil.include_exclude_allows_path(
                    os.path.relpath(local_filepath, root_directory_path), include_input_list, exclude_input_list
                ):
                    continue
                local_filepath_list.append(local_filepath)
                tasks.add(os.path.relpath(local_filepath, root_directory_path).split(os.path.sep)[0])
                total_file_size_bytes += os.path.getsize(local_filepath)
        return local_filepath_list, len(tasks), total_file_size_bytes

    @staticmethod
    def _get_num_directories_in_directory(root_directory_path, include_input_list, exclude_input_list):
        num_directories = 0
        for entry in os.scandir(root_directory_path):
            if entry.is_dir() and FileUtil.include_exclude_allows_path(
                entry.name, include_input_list, exclude_input_list
            ):
                num_directories += 1
        return num_directories

    @staticmethod
    def should_ignore_path(file_name):
        if FileUtil._path_contains_directory(file_name, FOVUS_JOB_INFO_FOLDER):
            return True
        if Util.is_unix():
            return FileUtil._is_swap_or_hidden_file_unix(file_name)
        if Util.is_windows():
            return FileUtil._is_temp_or_hidden_file_windows(file_name)
        raise UserException(
            HTTPStatus.BAD_REQUEST,
            FileUtil.__name__,
            "Unsupported operating system. Only Windows and Unix are supported.",
        )

    @staticmethod
    def include_exclude_allows_path(file_relative_path, include_list, exclude_list):
        if include_list and not FileUtil._should_include_file(file_relative_path, include_list):
            return False
        if exclude_list and FileUtil._should_exclude_file(file_relative_path, exclude_list):
            return False
        return True

    @staticmethod
    def _should_include_file(file_name, include_input_list):
        for include_input in include_input_list:
            if fnmatch.fnmatch(file_name, include_input):
                return True
        return False

    @staticmethod
    def _should_exclude_file(file_name, exclude_input_list):
        for exclude_input in exclude_input_list:
            if fnmatch.fnmatch(file_name, exclude_input):
                return True
        return False

    @staticmethod
    def _path_contains_directory(filepath, directory):
        return directory in filepath.split(os.path.sep)

    @staticmethod
    def directory_contains_directory(directory_path, directory):
        return directory in os.listdir(directory_path)

    @staticmethod
    def _is_swap_or_hidden_file_unix(filepath):
        is_hidden = os.path.basename(filepath).startswith(".")
        is_swap = os.path.basename(filepath).endswith("~")
        return is_hidden or is_swap

    @staticmethod
    def _is_temp_or_hidden_file_windows(filepath):  # pylint: disable=unused-argument
        return False  # TODO

    @staticmethod
    def file_exists(filepath):
        return os.path.exists(filepath)

    @staticmethod
    def get_file_hash(filepath):
        with open(filepath, "rb") as file:
            return hashlib.md5(file.read()).hexdigest()  # nosec

    @staticmethod
    def create_missing_directories(local_root_directory_path, directories):
        for directory in directories:
            local_directory_path = os.path.join(local_root_directory_path, directory)
            os.makedirs(local_directory_path, exist_ok=True)

    @staticmethod
    def windows_to_unix_path(path):
        return path.replace("\\", "/")
