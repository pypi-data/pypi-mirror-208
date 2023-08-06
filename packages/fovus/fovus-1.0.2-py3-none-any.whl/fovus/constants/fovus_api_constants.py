# API
from fovus.config.config import DOMAIN_NAME

COGNITO_REGION = "us-east-1"
TIMEOUT_SECONDS = 10

CREATE_JOB = "CREATE_JOB"
GET_JOB_INFO = "GET_JOB_STATUS"

GET_FILE_DOWNLOAD_TOKEN = "GET_FILE_DOWNLOAD_TOKEN"  # nosec
GET_FILE_UPLOAD_TOKEN = "GET_FILE_UPLOAD_TOKEN"  # nosec

LIST_SOFTWARE = "LIST_SOFTWARE"

FILE = "file"
JOB = "job"
SOFTWARE = "software"

__APIS = {JOB: DOMAIN_NAME + "/job"}
APIS = {
    JOB: {CREATE_JOB: __APIS[JOB] + "/create-job", GET_JOB_INFO: __APIS[JOB] + "/get-job-info"},
    FILE: {
        GET_FILE_DOWNLOAD_TOKEN: DOMAIN_NAME + "/file/get-file-download-token",
        GET_FILE_UPLOAD_TOKEN: DOMAIN_NAME + "/file/get-file-upload-token",
    },
    SOFTWARE: {
        LIST_SOFTWARE: DOMAIN_NAME + "/software/list-software",
    },
}

# Payload
AUTHORIZATION_HEADER = "Authorization"
CONTAINERIZED = "containerized"
ENVIRONMENT = "environment"
LICENSE_COUNT_PER_TASK = "licenseCountPerTask"
LICENSE_FEATURE = "licenseFeature"
MONOLITHIC_LIST = "monolithicList"
PAYLOAD_CONSTRAINTS = "constraints"
PAYLOAD_JOB_CONSTRAINTS = "jobConstraints"
PAYLOAD_JOB_NAME = "jobName"
PAYLOAD_TASK_CONSTRAINTS = "taskConstraints"
PAYLOAD_TIME_COST_PRIORITY_RATIO = "timeToCostPriorityRatio"
PAYLOAD_TIMESTAMP = "timestamp"
PAYLOAD_WORKSPACE_ID = "workspaceId"
SOFTWARE_NAME = "softwareName"
STATUS_CODE = "statusCode"
VENDOR_NAME = "vendorName"

# Response
BODY = "body"
ERROR_MESSAGE = "errorMessage"
JOB_STATUS = "jobStatus"
