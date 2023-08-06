import copy
import json
import os

import requests

from fovus.adapter.aws_cognito_adapter import AwsCognitoAdapter, UserAttribute
from fovus.constants.cli_constants import (
    FOVUS_PROVIDED_CONFIGS,
    JOB_CONFIG_CONTAINERIZED_TEMPLATE,
    JOB_CONFIG_FILE_PATH,
    JOB_NAME,
    MONOLITHIC_OVERRIDE,
    PATH_TO_CONFIG_FILE_IN_REPO,
    TIMESTAMP,
    USER_ID,
    WORKSPACE_ID,
)
from fovus.constants.fovus_api_constants import (
    APIS,
    AUTHORIZATION_HEADER,
    BODY,
    CONTAINERIZED,
    CREATE_JOB,
    ENVIRONMENT,
    FILE,
    GET_FILE_DOWNLOAD_TOKEN,
    GET_FILE_UPLOAD_TOKEN,
    GET_JOB_INFO,
    JOB,
    JOB_STATUS,
    LICENSE_COUNT_PER_TASK,
    LICENSE_FEATURE,
    LIST_SOFTWARE,
    MONOLITHIC_LIST,
    PAYLOAD_JOB_NAME,
    PAYLOAD_TIMESTAMP,
    PAYLOAD_WORKSPACE_ID,
    SOFTWARE,
    SOFTWARE_NAME,
    TIMEOUT_SECONDS,
    VENDOR_NAME,
)
from fovus.constants.util_constants import UTF8
from fovus.root_config import ROOT_DIR
from fovus.util.fovus_api_util import FovusApiUtil
from fovus.validator.fovus_api_validator import FovusApiValidator


class FovusApiAdapter:
    def __init__(self, auth_type, auth_parameters, client_id):
        self.cognito_adapter = AwsCognitoAdapter()
        self.cognito_adapter.authenticate(auth_type, auth_parameters, client_id)

    def create_job(self, request):
        request = self._fill_missing_vendor_names(request)
        headers = self._get_api_authorization_header()
        response = requests.post(APIS[JOB][CREATE_JOB], json=request, headers=headers, timeout=TIMEOUT_SECONDS)
        FovusApiUtil.confirm_successful_response(response.json(), self.__class__.__name__)
        return response.json()

    def _fill_missing_vendor_names(self, create_job_request):
        print("Attempting to fill missing/empty vendorName fields (if needed)...")
        if MONOLITHIC_LIST in create_job_request[ENVIRONMENT]:
            list_software_response = {}
            monolithic_list_copy = copy.deepcopy(create_job_request[ENVIRONMENT][MONOLITHIC_LIST])
            for i, monolithic_list_item in enumerate(monolithic_list_copy):
                if FovusApiUtil.should_fill_vendor_name(monolithic_list_item):
                    if not list_software_response:
                        list_software_response = self.list_software()
                    vendor_name = FovusApiUtil.get_software_vendor(
                        list_software_response, monolithic_list_item[SOFTWARE_NAME]
                    )
                    create_job_request[ENVIRONMENT][MONOLITHIC_LIST][i][VENDOR_NAME] = vendor_name
                    print(
                        f"Filled name for {SOFTWARE_NAME} {monolithic_list_item[SOFTWARE_NAME]} "
                        + f"with {VENDOR_NAME} {vendor_name}"
                    )
        elif CONTAINERIZED in create_job_request[ENVIRONMENT]:
            print("Request is for a containerized job. Filling missing/empty vendorName fields is not required.")
        return create_job_request

    def get_file_download_token(self, request):
        headers = self._get_api_authorization_header()
        response = requests.post(
            APIS[FILE][GET_FILE_DOWNLOAD_TOKEN], json=request, headers=headers, timeout=TIMEOUT_SECONDS
        )
        FovusApiUtil.confirm_successful_response(response.json(), self.__class__.__name__)
        return response.json()

    def get_file_upload_token(self, request):
        headers = self._get_api_authorization_header()
        response = requests.post(
            APIS[FILE][GET_FILE_UPLOAD_TOKEN], json=request, headers=headers, timeout=TIMEOUT_SECONDS
        )
        FovusApiUtil.confirm_successful_response(response.json(), self.__class__.__name__)
        return response.json()

    def get_temporary_s3_upload_credentials(self, cli_dict):
        upload_credentials = self.get_file_upload_token(self.get_file_upload_download_token_request(cli_dict))
        FovusApiUtil.confirm_successful_response(upload_credentials, self.__class__.__name__)
        return FovusApiUtil.get_s3_info(upload_credentials[BODY])

    def get_temporary_s3_download_credentials(self, cli_dict):
        upload_credentials = self.get_file_download_token(self.get_file_upload_download_token_request(cli_dict))
        FovusApiUtil.confirm_successful_response(upload_credentials, self.__class__.__name__)
        return FovusApiUtil.get_s3_info(upload_credentials[BODY])

    def get_job_current_status(self, cli_dict, job_id):
        job_info = self.get_job_info(FovusApiAdapter.get_job_info_request(cli_dict, job_id))
        return job_info[BODY][JOB_STATUS]

    def get_job_info(self, request):
        headers = self._get_api_authorization_header()
        response = requests.post(APIS[JOB][GET_JOB_INFO], json=request, headers=headers, timeout=TIMEOUT_SECONDS)
        FovusApiUtil.confirm_successful_response(response.json(), self.__class__.__name__)
        return response.json()

    def list_software(self):
        headers = self._get_api_authorization_header()
        response = requests.get(APIS[SOFTWARE][LIST_SOFTWARE], headers=headers, timeout=TIMEOUT_SECONDS)
        FovusApiUtil.confirm_successful_response(response.json(), self.__class__.__name__)
        return response.json()

    def get_user_id(self):
        return self.cognito_adapter.get_user_attribute(UserAttribute.USER_ID)

    def _get_api_authorization_header(self):
        return {
            AUTHORIZATION_HEADER: self.cognito_adapter.get_id_token(),
        }

    @staticmethod
    def get_create_job_request(cli_dict):
        with open(os.path.expanduser(cli_dict[JOB_CONFIG_FILE_PATH]), encoding=UTF8) as job_config_file:
            create_job_request = json.load(job_config_file)
            FovusApiAdapter._add_create_job_request_remaining_fields(create_job_request, cli_dict)
            FovusApiAdapter._apply_cli_overrides_to_request(create_job_request, cli_dict)
            FovusApiValidator.validate(create_job_request, CREATE_JOB)
            FovusApiValidator.validate_additional_create_job_fields(create_job_request)
            return create_job_request

    @staticmethod
    def _add_create_job_request_remaining_fields(create_job_request, cli_dict):
        create_job_request[PAYLOAD_TIMESTAMP] = cli_dict[TIMESTAMP]
        create_job_request[PAYLOAD_WORKSPACE_ID] = cli_dict[WORKSPACE_ID]
        if cli_dict.get(JOB_NAME):
            create_job_request[PAYLOAD_JOB_NAME] = cli_dict[JOB_NAME]
        else:
            create_job_request[PAYLOAD_JOB_NAME] = f"{create_job_request[PAYLOAD_TIMESTAMP]}-{cli_dict[USER_ID]}"

    @staticmethod
    def _apply_cli_overrides_to_request(create_job_request, cli_dict):
        print("Applying CLI overrides to create job request...")
        FovusApiAdapter._apply_single_field_overrides(create_job_request, cli_dict)
        FovusApiAdapter._apply_monolithic_list_overrides(create_job_request, cli_dict)

    @staticmethod
    def _apply_single_field_overrides(create_job_request, cli_dict):
        # The empty create job request is used to reference keys in the event that the provided config is not complete
        # and CLI arguments are being used to replace the remaining values.
        with open(
            os.path.join(
                ROOT_DIR, FOVUS_PROVIDED_CONFIGS[JOB_CONFIG_CONTAINERIZED_TEMPLATE][PATH_TO_CONFIG_FILE_IN_REPO]
            ),
            encoding=UTF8,
        ) as empty_job_config_file:
            empty_create_job_request = json.load(empty_job_config_file)
            del empty_create_job_request[ENVIRONMENT]

            for empty_sub_dict, create_job_request_sub_dict in FovusApiAdapter._get_deepest_sub_dict_pairs(
                empty_create_job_request, create_job_request
            ):
                FovusApiAdapter._apply_cli_overrides_to_sub_dict(create_job_request_sub_dict, empty_sub_dict, cli_dict)

    @staticmethod
    def _apply_monolithic_list_overrides(create_job_request, cli_dict):
        environment = create_job_request[ENVIRONMENT]
        if MONOLITHIC_LIST in environment:
            for monolithic in environment[MONOLITHIC_LIST]:
                for vendor_name, software_name, license_feature, new_license_count_per_task in cli_dict[
                    MONOLITHIC_OVERRIDE
                ]:
                    if (
                        monolithic[VENDOR_NAME] == vendor_name
                        and monolithic[SOFTWARE_NAME] == software_name
                        and monolithic[LICENSE_FEATURE] == license_feature
                    ):
                        print(
                            f"CLI override found for monolithic item with keys: {vendor_name}, {software_name}, and "
                            f"{license_feature}. Overriding default license count per task of "
                            f"{monolithic[LICENSE_COUNT_PER_TASK]} with {new_license_count_per_task}."
                        )
                        monolithic[LICENSE_COUNT_PER_TASK] = int(new_license_count_per_task)

    @staticmethod
    def _get_deepest_sub_dict_pairs(empty_create_job_request, create_job_request):
        sub_dict_pairs = []
        for key in empty_create_job_request.keys():
            if isinstance(empty_create_job_request[key], dict):
                if key not in create_job_request:
                    create_job_request[key] = {}
                sub_sub_dict_pairs = FovusApiAdapter._get_deepest_sub_dict_pairs(
                    empty_create_job_request[key], create_job_request[key]
                )
                if sub_sub_dict_pairs:
                    sub_dict_pairs.extend(sub_sub_dict_pairs)
                else:
                    sub_dict_pairs.append((empty_create_job_request[key], create_job_request[key]))
        return sub_dict_pairs

    @staticmethod
    def _apply_cli_overrides_to_sub_dict(sub_dict, empty_sub_dict, cli_dict):
        for sub_dict_parameter_key in empty_sub_dict.keys():
            cli_dict_value = cli_dict.get(sub_dict_parameter_key)
            if cli_dict[sub_dict_parameter_key] is not None:
                print(
                    f"CLI override found for key: {sub_dict_parameter_key}. Overriding default job config value of "
                    f"{sub_dict.get(sub_dict_parameter_key)} with {cli_dict[sub_dict_parameter_key]}."
                )
                if isinstance(cli_dict_value, str) and cli_dict_value.isdigit():
                    cli_dict_value = int(cli_dict_value)
                sub_dict[sub_dict_parameter_key] = cli_dict_value

    @staticmethod
    def get_file_upload_download_token_request(cli_dict, duration_seconds=3600):
        return {"workspaceId": cli_dict["workspace_id"], "durationSeconds": duration_seconds}

    @staticmethod
    def get_job_info_request(cli_dict, job_id):
        return {"workspaceId": cli_dict["workspace_id"], "jobId": job_id}
