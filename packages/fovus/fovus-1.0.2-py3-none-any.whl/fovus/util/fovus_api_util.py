from http import HTTPStatus

import boto3

from fovus.constants.cli_constants import JOB_ID, TIMESTAMP, USER_ID
from fovus.constants.fovus_api_constants import ERROR_MESSAGE, STATUS_CODE
from fovus.constants.util_constants import (
    SERVER_ERROR_PREFIX,
    SUCCESS_STATUS_CODES,
    USER_ERROR_PREFIX,
)
from fovus.exception.system_exception import SystemException
from fovus.exception.user_exception import UserException

NO_ERROR_MESSAGE = "No error message provided"


# Only 200, 201, 202, 4XX, and 5XX status codes are returned from the API.
class FovusApiUtil:  # pylint: disable=too-few-public-methods
    @staticmethod
    def confirm_successful_response(response, source):
        response_status_code = response[STATUS_CODE]
        if response_status_code not in SUCCESS_STATUS_CODES:
            if str(response_status_code).startswith(USER_ERROR_PREFIX):
                raise UserException(response_status_code, source, FovusApiUtil._get_error_message(response))
            if str(response_status_code).startswith(SERVER_ERROR_PREFIX):
                raise SystemException(response_status_code, source, FovusApiUtil._get_error_message(response))

    @staticmethod
    def _get_error_message(response):
        return response.get(ERROR_MESSAGE, NO_ERROR_MESSAGE)

    @staticmethod
    def get_job_id(cli_dict):
        if cli_dict.get(JOB_ID):
            return cli_dict[JOB_ID]
        cli_dict[JOB_ID] = FovusApiUtil._get_job_id_with_timestamp(cli_dict)
        return cli_dict[JOB_ID]

    @staticmethod
    def _get_job_id_with_timestamp(cli_dict):
        return f"{cli_dict[TIMESTAMP]}-{cli_dict[USER_ID]}"

    @staticmethod
    def get_s3_info(temporary_credentials_body):
        return (
            boto3.client(
                "s3",
                aws_access_key_id=temporary_credentials_body["credentials"]["accessKeyId"],
                aws_secret_access_key=temporary_credentials_body["credentials"]["secretAccessKey"],
                aws_session_token=temporary_credentials_body["credentials"]["sessionToken"],
            ),
            temporary_credentials_body["authorizedBucket"],
            temporary_credentials_body["authorizedFolder"],
        )

    @staticmethod
    def get_software_vendor(list_software_response, software_name):
        software_map = list_software_response["softwareMap"]
        for vendor in software_map.keys():
            if software_name in software_map[vendor]:
                return vendor
        raise UserException(
            HTTPStatus.BAD_REQUEST,
            FovusApiUtil.__name__,
            f"Software {software_name} not found in list of available software, unable to retrieve version.",
        )

    @staticmethod
    def should_fill_vendor_name(monolithic_list_item):
        return monolithic_list_item.get("softwareName") and not monolithic_list_item.get("vendorName")
