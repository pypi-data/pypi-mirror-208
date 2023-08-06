import concurrent.futures
import json
import os
from http import HTTPStatus

import boto3
import botocore
from tqdm import tqdm

from fovus.constants.cli_constants import (
    EXCLUDE_INPUT,
    EXCLUDE_OUTPUT,
    INCLUDE_INPUT,
    INCLUDE_OUTPUT,
)
from fovus.constants.util_constants import UTF8
from fovus.exception.system_exception import SystemException
from fovus.exception.user_exception import UserException
from fovus.util.aws_util import AwsUtil
from fovus.util.file_util import FOVUS_JOB_INFO_FOLDER, FileUtil
from fovus.util.fovus_api_util import FovusApiUtil
from fovus.util.fovus_s3_adapter_util import FovusS3AdapterUtil
from fovus.util.util import Util

DOWNLOAD = "Download"
LOCAL_FILEPATH = "local_filepath"
SUCCESS = "success"
UPLOAD = "Upload"

JOB_DATA_FILENAME = "job_data.json"


class FovusS3Adapter:
    def __init__(self, fovus_api_adapter, cli_dict, root_directory_path):
        self.fovus_api_adapter = fovus_api_adapter
        self.cli_dict = cli_dict
        self.local_root_directory_path = root_directory_path
        self.job_id = FovusApiUtil.get_job_id(self.cli_dict)

        # Assigned if upload function is called.
        self.local_filepath_list = None
        self.task_count = None
        self.total_file_size_bytes = None

    def get_job_id(self):
        return self.job_id

    def upload_files(self):
        self._instantiate_upload_instance_variables()
        self._validate_root_directory()
        FovusS3AdapterUtil.print_pre_operation_information(
            UPLOAD, len(self.local_filepath_list), self.total_file_size_bytes, self.task_count
        )
        self._operate_on_s3_in_parallel(self.local_filepath_list, self._upload_file, self._prepare_next_upload_attempt)
        self._create_job_data_file()
        FovusS3AdapterUtil.print_post_operation_success(UPLOAD, is_success=True)

    def _validate_root_directory(self):
        if FileUtil.directory_contains_directory(self.local_root_directory_path, FOVUS_JOB_INFO_FOLDER):
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Root directory cannot contain a .fovus folder. Please remove it and try again. "
                + "\nNote: The .fovus folder is hidden, so you may need to adjust your file explorer's settings "
                + "to show hidden folders.",
            )

    def _create_job_data_file(self):
        job_data = {
            "job_id": self.job_id,
        }
        fovus_job_info_directory_path = os.path.join(self.local_root_directory_path, FOVUS_JOB_INFO_FOLDER)
        os.makedirs(fovus_job_info_directory_path)
        job_data_filepath = os.path.join(fovus_job_info_directory_path, JOB_DATA_FILENAME)
        with open(job_data_filepath, "w", encoding=UTF8) as job_data_file:
            json.dump(job_data, job_data_file)

    def download_files(self):
        s3_list_objects_v2_response = self._get_s3_list_objects_v2_response()
        objects_to_download, total_size_bytes, tasks = AwsUtil.get_s3_object_list_info(
            s3_list_objects_v2_response, self.cli_dict[INCLUDE_OUTPUT], self.cli_dict[EXCLUDE_OUTPUT]
        )
        FovusS3AdapterUtil.print_pre_operation_information(DOWNLOAD, len(objects_to_download), total_size_bytes, tasks)
        FileUtil.create_missing_directories(
            self.local_root_directory_path,
            AwsUtil.get_all_directories(
                objects_to_download,
                s3_list_objects_v2_response["Prefix"],
                self.cli_dict[INCLUDE_OUTPUT],
                self.cli_dict[EXCLUDE_OUTPUT],
            ),
        )
        self._operate_on_s3_in_parallel(objects_to_download, self._download_file, self._prepare_next_download_attempt)
        FovusS3AdapterUtil.print_post_operation_success(DOWNLOAD, is_success=True)

    def _operate_on_s3_in_parallel(self, remaining_items, file_operation, prepare_next_attempt_action):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            progress_bar = tqdm(total=len(remaining_items), unit="files", desc="Progress")
            while True:
                s3_info = prepare_next_attempt_action(futures)
                remaining_items = self._try_operate_on_file_list(
                    file_operation, s3_info, futures, executor, remaining_items, progress_bar
                )
                if not remaining_items:
                    progress_bar.close()
                    return

    def _try_operate_on_file_list(  # pylint: disable=too-many-arguments
        self, file_operation, s3_info, futures, executor, remaining_objects, progress_bar
    ):
        failed_objects = []
        for obj in remaining_objects:
            futures.append(executor.submit(file_operation, s3_info, obj))
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result[SUCCESS]:
                progress_bar.update()
            else:
                failed_objects.append(result[LOCAL_FILEPATH])
        return failed_objects

    def _instantiate_upload_instance_variables(self):
        self.local_filepath_list, self.task_count, self.total_file_size_bytes = FileUtil.get_files_in_directory(
            self.local_root_directory_path, self.cli_dict[INCLUDE_INPUT], self.cli_dict[EXCLUDE_INPUT]
        )

    def _prepare_next_upload_attempt(self, futures):
        futures.clear()
        s3_info = self.fovus_api_adapter.get_temporary_s3_upload_credentials(self.cli_dict)
        return s3_info

    def _upload_file(self, s3_info, local_filepath):
        s3_client, s3_bucket, s3_prefix = s3_info
        local_relative_filepath = os.path.relpath(local_filepath, self.local_root_directory_path)
        s3_path = os.path.join(s3_prefix, self.job_id, local_relative_filepath)
        if Util.is_windows():
            s3_path = FileUtil.windows_to_unix_path(s3_path)

        result = {SUCCESS: True, LOCAL_FILEPATH: local_filepath}
        try:
            s3_client.upload_file(local_filepath, s3_bucket, s3_path)
        except boto3.exceptions.S3UploadFailedError as error:
            if AwsUtil.is_expired_token_error(error):
                result[SUCCESS] = False
            else:
                raise SystemException(HTTPStatus.INTERNAL_SERVER_ERROR, error)  # pylint: disable=raise-missing-from
        return result

    def _get_s3_list_objects_v2_response(self):
        s3_client, s3_bucket, s3_prefix = self._prepare_next_download_attempt([])
        s3_objects_list = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
        return s3_objects_list

    def _prepare_next_download_attempt(self, futures):
        futures.clear()
        s3_client, s3_bucket, s3_prefix = self.fovus_api_adapter.get_temporary_s3_download_credentials(self.cli_dict)
        s3_prefix += self.job_id
        return (s3_client, s3_bucket, s3_prefix)

    def _download_file(self, s3_info, s3_object):
        s3_client, s3_bucket, s3_prefix = s3_info
        result = {SUCCESS: True}
        if not AwsUtil.s3_object_is_directory(s3_object):
            local_filepath = self._get_local_filepath(s3_object, s3_prefix)
            result[LOCAL_FILEPATH] = local_filepath

            if FileUtil.include_exclude_allows_path(
                os.path.relpath(local_filepath, self.local_root_directory_path),
                self.cli_dict[INCLUDE_OUTPUT],
                self.cli_dict[EXCLUDE_OUTPUT],
            ) and FovusS3AdapterUtil.should_download_file(local_filepath, s3_object):
                os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
                try:
                    s3_client.download_file(s3_bucket, s3_object["Key"], local_filepath)
                except botocore.exceptions.ClientError as error:
                    if AwsUtil.is_expired_token_error(error):
                        result[SUCCESS] = False
                    else:
                        raise SystemException(  # pylint: disable=raise-missing-from
                            HTTPStatus.INTERNAL_SERVER_ERROR, error
                        )
        return result

    def _get_local_filepath(self, s3_object, s3_prefix):
        return os.path.join(
            self.local_root_directory_path, AwsUtil.get_s3_object_key_without_prefix(s3_object, s3_prefix)
        )
