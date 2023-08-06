import os

# Parsed argument keys.
CLIENT_ID = "client_id"
CONFIGURE = "configure"
CREATE_JOB_WITH_UPLOAD = "create_job_with_upload"
DOWNLOAD_JOB_FILES = "download_job_files"
EXCLUDE_INPUT = "exclude_input"
EXCLUDE_OUTPUT = "exclude_output"
GET_JOB_CURRENT_STATUS = "get_job_current_status"
INCLUDE_INPUT = "include_input"
INCLUDE_OUTPUT = "include_output"
JOB_CONFIG_FILE_PATH = "job_config_file_path"
JOB_FILE_ROOT_DIRECTORY = "job_file_root_directory"
JOB_ID = "job_id"
JOB_NAME = "job_name"
OPEN_CONFIG_FOLDER = "open_config_folder"
TIMESTAMP = "timestamp"
USERNAME = "username"
USER_CONFIG_FILE_PATH = "user_config_file_path"
USER_ID = "user_id"
USER_POOL_ID = "user_pool_id"
WORKSPACE_ID = "workspace_id"

# Job config overrides.
BENCHMARKING_PROFILE_ID = "benchmarkingProfileId"
BENCHMARKING_PROFILE_NAME = "benchmarkingProfileName"
COMPUTING_DEVICE = "computingDevice"
LICENSE_TIMEOUT_HOURS = "licenseTimeoutHours"
MONOLITHIC_OVERRIDE = "monolithicOverride"
MIN_GPU = "minGpu"
MAX_GPU = "maxGpu"
MIN_GPU_MEM_GIB = "minGpuMemGiB"
MIN_VCPU = "minvCpu"
MAX_VCPU = "maxvCpu"
MIN_VCPU_MEM_GIB = "minvCpuMemGiB"
OUTPUT_FILE_LIST = "outputFileList"
OUTPUT_FILE_OPTION = "outputFileOption"
PARALLELISM_CONFIG_FILES = "parallelismConfigFiles"
PARALLELISM_OPTIMIZATION = "parallelismOptimization"
RUN_COMMAND = "runCommand"
SCALABLE_PARALLELISM = "scalableParallelism"
SCALING_OUT = "scalingOut"
STORAGE_GIB = "storageGiB"
IS_SUBJECT_TO_AVAILABLE_RESOURCES = "isSubjectToAvailableResources"
ENABLE_HYPERTHREADING = "enableHyperthreading"
SUPPORTED_CPU_ARCHITECTURES = "supportedCpuArchitectures"
TIME_TO_COST_PRIORITY_RATIO = "timeToCostPriorityRatio"
WALLTIME_HOURS = "walltimeHours"

# Additional arguments (if required).
MONOLITHIC_OVERRIDE_ADDITIONAL_ARGUMENTS = {
    "default": [],
    "action": "append",
    "nargs": 4,
    "metavar": ("VENDOR_NAME", "SOFTWARE_NAME", "LICENSE_FEATURE", "NEW_LICENSE_COUNT"),
}

# Argument groups
BOOLEAN_ARGS = (
    SCALABLE_PARALLELISM,
    PARALLELISM_OPTIMIZATION,
    SCALING_OUT,
    IS_SUBJECT_TO_AVAILABLE_RESOURCES,
    ENABLE_HYPERTHREADING,
)

# CLI arguments
CLI_ARGUMENTS = {
    CLIENT_ID: ("--client-id", "--clientId", "-cid"),
    CONFIGURE: ("--configure", "-c"),
    CREATE_JOB_WITH_UPLOAD: ("--create-job-with-upload", "--createJobWithUpload", "-cjwu"),
    DOWNLOAD_JOB_FILES: ("--download-job-files", "--downloadJobFiles", "-djf"),
    EXCLUDE_INPUT: ("--exclude-input", "--excludeInput", "-ei"),
    EXCLUDE_OUTPUT: ("--exclude-output", "--excludeOutput", "-eo"),
    GET_JOB_CURRENT_STATUS: ("--get-job-current-status", "--getJobCurrentStatus", "-gjcs"),
    INCLUDE_INPUT: ("--include-input", "--includeInput", "-ii"),
    INCLUDE_OUTPUT: ("--include-output", "--includeOutput", "-io"),
    JOB_CONFIG_FILE_PATH: ("--job-config-file-path", "--jobConfigFilePath", "-jcfp"),
    JOB_FILE_ROOT_DIRECTORY: ("--job-file-root-directory", "--jobFileRootDirectory", "-jfdr"),
    OPEN_CONFIG_FOLDER: ("--open-config-folder", "--openConfigFolder", "-ocf"),
    USERNAME: ("--username", "-u"),
    USER_CONFIG_FILE_PATH: ("--user-config-file-path", "--userConfigFilePath", "-ucfp"),
    USER_ID: ("--user-id", "--userId", "-uid"),
    USER_POOL_ID: ("--user-pool-id", "--userPoolId", "-upi"),
    WORKSPACE_ID: ("--workspace-id", "--workspaceId", "-wid"),
    # Job config overrides.
    BENCHMARKING_PROFILE_ID: ("--benchmarking-profile-id", "--benchmarkingProfileId", "-bpi"),
    BENCHMARKING_PROFILE_NAME: ("--benchmarking-profile-name", "--benchmarkingProfileName", "-bpn"),
    COMPUTING_DEVICE: ("--computing-device", "--computingDevice", "-cd"),
    JOB_NAME: ("--job-name", "--jobName", "-jn"),
    JOB_ID: ("--job-id", "--jobId", "-jid"),
    LICENSE_TIMEOUT_HOURS: ("--license-timeout-hours", "--licenseTimeoutHours", "-lth"),
    MONOLITHIC_OVERRIDE: ("--monolithic-override", "--monolithicOverride", "-mo"),
    MIN_GPU: ("--min-gpu", "--minGpu"),
    MAX_GPU: ("--max-gpu", "--maxGpu"),
    MIN_GPU_MEM_GIB: ("--min-gpu-mem-gib", "--minGpuMemGiB", "-mgpuMemGiB"),
    MIN_VCPU: ("--min-vcpu", "--minvCpu", "--min-cpu"),
    MAX_VCPU: ("--max-vcpu", "--maxvCpu", "--max-cpu"),
    MIN_VCPU_MEM_GIB: ("--min-vcpu-mem-gib", "--minvCpuMemGiB", "-mvcpuMemGiB"),
    OUTPUT_FILE_LIST: ("--output-file-list", "--outputFileList", "-ofl"),
    OUTPUT_FILE_OPTION: ("--output-file-option", "--outputFileOption", "-ofo"),
    PARALLELISM_CONFIG_FILES: ("--parallelism-config-files", "--parallelismConfigFiles", "-pcf"),
    PARALLELISM_OPTIMIZATION: ("--parallelism-optimization", "--parallelismOptimization", "-po"),
    RUN_COMMAND: ("--run-command", "--runCommand", "-rc"),
    SCALABLE_PARALLELISM: ("--scalable-parallelism", "--scalableParallelism", "-sp"),
    SCALING_OUT: ("--scaling-out", "--scalingOut", "-so"),
    STORAGE_GIB: ("--storage-gib", "--storageGiB", "-sgib"),
    IS_SUBJECT_TO_AVAILABLE_RESOURCES: (
        "--is-subject-to-available-resources",
        "--isSubjectToAvailableResources",
        "-istar",
    ),
    ENABLE_HYPERTHREADING: ("--enable-hyperthreading", "--enableHyperthreading", "--hyperthreading", "-ht"),
    SUPPORTED_CPU_ARCHITECTURES: ("--supported-cpu-architectures", "--supportedCpuArchitectures", "-sca"),
    TIME_TO_COST_PRIORITY_RATIO: ("--time-to-cost-priority-ratio", "--timeToCostPriorityRatio", "-tcr"),
    WALLTIME_HOURS: ("--walltime-hours", "--walltimeHours", "-wh"),
}

CONFLICTING_CLI_ARGUMENT_SETS = [
    (
        CONFIGURE,
        OPEN_CONFIG_FOLDER,
        CREATE_JOB_WITH_UPLOAD,
        DOWNLOAD_JOB_FILES,
        GET_JOB_CURRENT_STATUS,
    ),
    (INCLUDE_INPUT, EXCLUDE_INPUT),
    (INCLUDE_OUTPUT, EXCLUDE_OUTPUT),
]

PASSWORD_ENVIRONMENT_VARIABLE_KEY = "FOVUS_CLI_PASSWORD"  # nosec
PATH_TO_CONFIG_ROOT = os.path.join(os.path.expanduser("~"), ".fovus")
PATH_TO_JOB_CONFIGS = os.path.join(PATH_TO_CONFIG_ROOT, "job_configs")
PATH_TO_USER_CONFIGS = os.path.join(PATH_TO_CONFIG_ROOT, "user_configs")
PATH_TO_JOB_LOGS = os.path.join(PATH_TO_CONFIG_ROOT, "job_logs")
UNIX_OPEN = "open"
WINDOWS_EXPLORER = "explorer"

DEFAULT_USER_CONFIG_FILE_NAME = "FOVUS_default_user_config.json"
DEFAULT_USER_CONFIG_FILE_PATH = os.path.join(PATH_TO_USER_CONFIGS, DEFAULT_USER_CONFIG_FILE_NAME)

FOVUS_PROVIDED_CONFIGS_FOLDER_REPO = "fovus_provided_configs"
JOB_CONFIG_CONTAINERIZED_TEMPLATE_FILE_NAME = "FOVUS_job_template_containerized.json"
JOB_CONFIG_MONOLITHIC_TEMPLATE_FILE_NAME = "FOVUS_job_template_monolithic.json"
EXAMPLE_JOB_CONFIG_CONTAINERIZED_FILE_NAME = "FOVUS_example_job_config_containerized.json"
EXAMPLE_JOB_CONFIG_MONOLITHIC_LIST_FILE_NAME = "FOVUS_example_job_config_monolithic.json"
USER_CONFIG_TEMPLATE_FILE_NAME = "FOVUS_user_config_template.json"

FILE_NAME = "FILE_NAME"
PATH_TO_CONFIG_FILE_IN_REPO = "PATH_TO_CONFIG_FILE_IN_REPO"
PATH_TO_CONFIG_FILE_LOCAL = "PATH_TO_CONFIG_FILE_LOCAL"

JOB_CONFIG_CONTAINERIZED_TEMPLATE = "JOB_CONFIG_CONTAINERIZED"
JOB_CONFIG_MONOLITHIC_TEMPLATE = "JOB_CONFIG_MONOLITHIC"
EXAMPLE_JOB_CONFIG_CONTAINERIZED = "EXAMPLE_JOB_CONFIG_CONTAINERIZED"
EXAMPLE_JOB_CONFIG_MONOLITHIC = "EXAMPLE_JOB_CONFIG_MONOLITHIC"
USER_CONFIG = "USER_CONFIG"
FOVUS_PROVIDED_CONFIGS = {
    JOB_CONFIG_CONTAINERIZED_TEMPLATE: {
        PATH_TO_CONFIG_FILE_IN_REPO: os.path.join(
            FOVUS_PROVIDED_CONFIGS_FOLDER_REPO, JOB_CONFIG_CONTAINERIZED_TEMPLATE_FILE_NAME
        ),
        PATH_TO_CONFIG_FILE_LOCAL: os.path.join(PATH_TO_JOB_CONFIGS, JOB_CONFIG_CONTAINERIZED_TEMPLATE_FILE_NAME),
    },
    JOB_CONFIG_MONOLITHIC_TEMPLATE: {
        PATH_TO_CONFIG_FILE_IN_REPO: os.path.join(
            FOVUS_PROVIDED_CONFIGS_FOLDER_REPO, JOB_CONFIG_MONOLITHIC_TEMPLATE_FILE_NAME
        ),
        PATH_TO_CONFIG_FILE_LOCAL: os.path.join(PATH_TO_JOB_CONFIGS, JOB_CONFIG_MONOLITHIC_TEMPLATE_FILE_NAME),
    },
    EXAMPLE_JOB_CONFIG_CONTAINERIZED: {
        PATH_TO_CONFIG_FILE_IN_REPO: os.path.join(
            FOVUS_PROVIDED_CONFIGS_FOLDER_REPO, EXAMPLE_JOB_CONFIG_CONTAINERIZED_FILE_NAME
        ),
        PATH_TO_CONFIG_FILE_LOCAL: os.path.join(PATH_TO_JOB_CONFIGS, EXAMPLE_JOB_CONFIG_CONTAINERIZED_FILE_NAME),
    },
    EXAMPLE_JOB_CONFIG_MONOLITHIC: {
        PATH_TO_CONFIG_FILE_IN_REPO: os.path.join(
            FOVUS_PROVIDED_CONFIGS_FOLDER_REPO, EXAMPLE_JOB_CONFIG_MONOLITHIC_LIST_FILE_NAME
        ),
        PATH_TO_CONFIG_FILE_LOCAL: os.path.join(PATH_TO_JOB_CONFIGS, EXAMPLE_JOB_CONFIG_MONOLITHIC_LIST_FILE_NAME),
    },
    USER_CONFIG: {
        PATH_TO_CONFIG_FILE_IN_REPO: os.path.join(FOVUS_PROVIDED_CONFIGS_FOLDER_REPO, USER_CONFIG_TEMPLATE_FILE_NAME),
        PATH_TO_CONFIG_FILE_LOCAL: os.path.join(PATH_TO_USER_CONFIGS, USER_CONFIG_TEMPLATE_FILE_NAME),
    },
}
