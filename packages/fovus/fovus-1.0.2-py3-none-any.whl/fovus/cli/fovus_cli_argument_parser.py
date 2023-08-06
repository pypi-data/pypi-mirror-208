#!/usr/bin/env python3
import argparse
import json
import os

from fovus.constants.cli_constants import (
    BENCHMARKING_PROFILE_NAME,
    BOOLEAN_ARGS,
    CLI_ARGUMENTS,
    COMPUTING_DEVICE,
    CONFIGURE,
    CREATE_JOB_WITH_UPLOAD,
    DEFAULT_USER_CONFIG_FILE_PATH,
    DOWNLOAD_JOB_FILES,
    ENABLE_HYPERTHREADING,
    EXCLUDE_INPUT,
    EXCLUDE_OUTPUT,
    GET_JOB_CURRENT_STATUS,
    INCLUDE_INPUT,
    INCLUDE_OUTPUT,
    IS_SUBJECT_TO_AVAILABLE_RESOURCES,
    JOB_CONFIG_FILE_PATH,
    JOB_FILE_ROOT_DIRECTORY,
    JOB_ID,
    JOB_NAME,
    LICENSE_TIMEOUT_HOURS,
    MAX_GPU,
    MAX_VCPU,
    MIN_GPU,
    MIN_GPU_MEM_GIB,
    MIN_VCPU,
    MIN_VCPU_MEM_GIB,
    MONOLITHIC_OVERRIDE,
    MONOLITHIC_OVERRIDE_ADDITIONAL_ARGUMENTS,
    OPEN_CONFIG_FOLDER,
    OUTPUT_FILE_LIST,
    OUTPUT_FILE_OPTION,
    PARALLELISM_CONFIG_FILES,
    PARALLELISM_OPTIMIZATION,
    RUN_COMMAND,
    SCALABLE_PARALLELISM,
    STORAGE_GIB,
    SUPPORTED_CPU_ARCHITECTURES,
    TIME_TO_COST_PRIORITY_RATIO,
    USER_CONFIG_FILE_PATH,
    USERNAME,
    WALLTIME_HOURS,
    WORKSPACE_ID,
)
from fovus.constants.util_constants import UTF8
from fovus.util.cli_action_runner_util import CliActionRunnerUtil
from fovus.util.fovus_cli_argument_parser_util import FovusCliArgumentParserUtil

OK_RETURN_STATUS = 0

JOB_DIRECTORY_REQUIRES_FOVUS_FOLDER_NOTE_WITH_DIRECTORY_AND_JOB_ID_EXPLANATION = (
    "(Note: If the job file directory is provided, the directory must contain a .fovus "
    "folder, which is automatically generated when a job is created with the Fovus CLI. "
    "If both a job file directory and job ID are provided, the job ID will be used.)"
)
USED_FOR_OVERRIDING_JOB_CONFIG_VALUES = (
    "(Note: Used for overriding job config values. If this value is provided in the job "
    "config file, this argument is optional.)"
)
USED_FOR_OVERRIDING_USER_CONFIG_VALUES = (
    "(Note: Used for overriding user config values. If this value is provided in the user "
    "config file, this argument is optional.)"
)
WILDCARD_EXAMPLE = (
    "Wildcard characters (*, ?) can be "
    "used to specify file and directory patterns (e.g., out?/*.txt specifies all .txt files in out1, "
    "out2, and out3 folders under the working directory of each task). "
)
WILDCARD_EXPLANATION = WILDCARD_EXAMPLE + (
    "Supported wildcards: * (matches any number of characters), ? (matches any single character). "
    "Note: if a wildcard is used in an input, the input must be surrounded by quotes "
    '(e.g., "folder?/input*"). '
)
ANY_NUMBER_OF_EXPRESSIONS = "Any number of space-separated values can be provided."


class FovusCliArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._add_parser_arguments()
        self.args_dict = {}

    def _add_parser_arguments(self):
        # Core functionality.
        self.parser.add_argument(
            *CLI_ARGUMENTS[CONFIGURE],
            action="store_true",
            help="Guided prompt to configure the default user config for the Fovus CLI. "
            "The default user config will be stored at ~/.fovus/user_configs/FOVUS_default_user_config.json, and "
            + "it will be used in the absence of the --user-config-file-path argument.",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[CREATE_JOB_WITH_UPLOAD],
            action="store_true",
            help="Upload files to Fovus and create a new job. Creates .fovus folder inside the provided job file root "
            + "directory, which contains data about the job and enables checking job status and downloading job files "
            + "using the job file root directory. Required additional parameters: "
            + ", ".join(
                CliActionRunnerUtil.get_argument_string_list_from_keys([JOB_CONFIG_FILE_PATH, JOB_FILE_ROOT_DIRECTORY])
            )
            + ".",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[DOWNLOAD_JOB_FILES],
            action="store_true",
            help="Download job files from Fovus for a given job. Any files that already exist on the local system and "
            + "have not been modified will not be downloaded. Requires one of the following parameters: "
            + ", ".join(CliActionRunnerUtil.get_argument_string_list_from_keys([JOB_ID, JOB_FILE_ROOT_DIRECTORY]))
            + ". "
            + JOB_DIRECTORY_REQUIRES_FOVUS_FOLDER_NOTE_WITH_DIRECTORY_AND_JOB_ID_EXPLANATION,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[OPEN_CONFIG_FOLDER],
            action="store_true",
            help="Open the Fovus CLI config folder, located at ~/.fovus. Also adds Fovus-provided config "
            + "file templates and examples to the folder for reference.",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[GET_JOB_CURRENT_STATUS],
            action="store_true",
            help="Get job status. Requires one of the following parameters: "
            + ", ".join(CliActionRunnerUtil.get_argument_string_list_from_keys([JOB_ID, JOB_FILE_ROOT_DIRECTORY]))
            + ". "
            + JOB_DIRECTORY_REQUIRES_FOVUS_FOLDER_NOTE_WITH_DIRECTORY_AND_JOB_ID_EXPLANATION,
        )

        # File paths.
        self.parser.add_argument(
            *CLI_ARGUMENTS[JOB_CONFIG_FILE_PATH],
            default=None,
            type=str,
            help="Absolute file path to a Fovus job config JSON. Values given in this file will be used unless they "
            + "are overridden by CLI input. The job config JSON must follow the structure given in the provided job "
            + "config templates, which are generated when the --open-config-folder command is used and will be located "
            + "in ~/.fovus/job_configs"
            + ".",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[USER_CONFIG_FILE_PATH],
            default=None,
            type=str,
            help="Absolute file path to a Fovus user config JSON. Values given in this file will be used unless they "
            + "are overridden by CLI input. If this argument is not provided, the default user config will be used "
            + "(see --configure). The user config must follow the structure given in the provided user config "
            + "file, which is generated when the --open-config-folder command is used and will be located in "
            + "~/.fovus/user_configs"
            + ".",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[JOB_FILE_ROOT_DIRECTORY],
            default=None,
            type=str,
            help="Root directory of job folder. A job folder contains one or multiple task folders. Each folder "
            + "uploaded under the job folder will be considered a task of the job. Each task folder is a "
            + "self-contained folder containing the necessary input files and scripts to run the task. For a job "
            + "that has N tasks (e.g. a DOE job with N simulation tasks), N task folders must exist under the job "
            + "folder and be uploaded.",
        )

        # CLI behavior options
        self.parser.add_argument(
            *CLI_ARGUMENTS[EXCLUDE_INPUT],
            dest=EXCLUDE_INPUT,
            default=None,
            type=str,
            nargs="+",
            help="Used with create job for uploading job files."
            + "Exclude input file path(s) (relative to the job root directory) that match the expression. If a "
            + "filepath "
            + "matches any expression, it will not be uploaded. "
            + " ".join((WILDCARD_EXPLANATION, ANY_NUMBER_OF_EXPRESSIONS)),
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[EXCLUDE_OUTPUT],
            dest=EXCLUDE_OUTPUT,
            default=None,
            type=str,
            nargs="+",
            help="Used with download job files. "
            "Exclude output file path(s) (relative to the job root directory) that match the expression. If a filepath "
            + "matches "
            + "any expression, it will not be downloaded. "
            + " ".join((WILDCARD_EXPLANATION, ANY_NUMBER_OF_EXPRESSIONS)),
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[INCLUDE_INPUT],
            dest=INCLUDE_INPUT,
            default=None,
            type=str,
            nargs="+",
            help="Used with create job for uploading job files. "
            + "Include input file path(s) (relative to the job root directory) that match the expression. If a "
            + "filepath does "
            + "not match any expression, it will not be uploaded. "
            + " ".join((WILDCARD_EXPLANATION, ANY_NUMBER_OF_EXPRESSIONS)),
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[INCLUDE_OUTPUT],
            dest=INCLUDE_OUTPUT,
            default=None,
            type=str,
            nargs="+",
            help="Used with download job files. "
            "Include output file path(s) (relative to the job root directory) that match the expression. If a "
            + "filepath does "
            + "not match any expression, it will not be downloaded. "
            + " ".join((WILDCARD_EXPLANATION, ANY_NUMBER_OF_EXPRESSIONS)),
        )

        # User config.
        self.parser.add_argument(
            *CLI_ARGUMENTS[USERNAME],
            dest=USERNAME,
            default=None,
            type=str,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(USERNAME).upper(),
            help=f"The email address used for your Fovus account. {USED_FOR_OVERRIDING_USER_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[WORKSPACE_ID],
            dest=WORKSPACE_ID,
            default=None,
            type=str,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(WORKSPACE_ID).upper(),
            help="The ID for the workspace you would like to use. The workspace ID can be found by clicking on the "
            + f"user icon in the web UI. {USED_FOR_OVERRIDING_USER_CONFIG_VALUES}",
        )

        # Job config.
        self.parser.add_argument(
            *CLI_ARGUMENTS[BENCHMARKING_PROFILE_NAME],
            dest=BENCHMARKING_PROFILE_NAME,
            default=None,
            type=str,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(BENCHMARKING_PROFILE_NAME).upper(),
            help="Fovus will optimize the cloud strategies for your job execution, including determining the "
            + "optimal choices of virtual HPC infrastructure and computation parallelism, if applicable, based "
            + "upon the selected benchmarking profile. For the best optimization results, select the benchmarking "
            + "profile whose characteristics best resemble the workload under submission. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[COMPUTING_DEVICE],
            dest=COMPUTING_DEVICE,
            default=None,
            type=str,
            choices=["cpu", "cpu+gpu"],
            help=f"The target computing device(s) for running your workload. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[JOB_NAME],
            dest=JOB_NAME,
            default=None,
            type=str,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(JOB_NAME).upper(),
            help="Job name. If not provided, a job name will be automatically generated using the current timestamp. "
            + "If a job name is not provided, the job ID will be used.",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[JOB_ID],
            dest=JOB_ID,
            default=None,
            type=str,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(JOB_ID).upper(),
            help="Job ID. Used for checking job status and downloading job files if the root file directory is not "
            + "provided.",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[LICENSE_TIMEOUT_HOURS],
            dest=LICENSE_TIMEOUT_HOURS,
            default=None,
            type=float,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(LICENSE_TIMEOUT_HOURS).upper(),
            help="For license-required jobs, the maximum time the job is allowed to be waiting in a queue for "
            + "deployment when no license is available. A job will be terminated once the timeout timer expires. "
            + "Not applicable to license-free jobs. Format: Real (e.g., 1.5). Range: ≥1. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[MONOLITHIC_OVERRIDE],
            dest=MONOLITHIC_OVERRIDE,
            **MONOLITHIC_OVERRIDE_ADDITIONAL_ARGUMENTS,
            help="Override a monolithic software environment. All four values are required to reference a monolithic "
            + "software and its license usage constraint. Currently, the only supported override for a monolithic "
            + "software environment is the license count, and as a result, only the "
            + f"license count is overridden. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[MIN_GPU],
            dest=MIN_GPU,
            default=None,
            type=int,
            metavar="MIN_GPU",
            help="The minimum number of GPUs required to parallelize the execution of each task. Only values "
            + f"supported by the selected BP are allowed. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[MAX_GPU],
            dest=MAX_GPU,
            default=None,
            type=int,
            metavar="MAX_GPU",
            help="The maximum number of GPUs allowed to parallelize the execution of each task. Only values "
            + f"supported by the selected BP are allowed. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[MIN_GPU_MEM_GIB],
            dest=MIN_GPU_MEM_GIB,
            default=None,
            type=float,
            metavar="MIN_GPU_MEM_GIB",
            help="The minimum total size of GPU memory required to support the execution of each task, summing "
            + "the required memory size for each GPU. Format: Real (e.g., 10.5). Only values supported by the "
            + "selected BP are allowed. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[MIN_VCPU],
            dest=MIN_VCPU,
            default=None,
            type=int,
            metavar="MIN_VCPU",
            help="The minimum number of vCPUs required to parallelize the execution of each task. A vCPU refers "
            + "to a thread of a CPU core. Only values supported by the selected BP are allowed. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[MAX_VCPU],
            dest=MAX_VCPU,
            default=None,
            type=int,
            metavar="MAX_VCPU",
            help="The maximum number of vCPUs allowed to parallelize the execution of each task. A vCPU refers "
            + "to a thread of a CPU core. Only values supported by the selected BP are allowed. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[MIN_VCPU_MEM_GIB],
            dest=MIN_VCPU_MEM_GIB,
            default=None,
            type=float,
            metavar="MIN_VCPU_MEM_GIB",
            help="The minimum total size of system memory required to support the execution of each task, summing "
            + "the required memory size for each vCPU. Format: Real (e.g., 10.5). Only values supported by the "
            + "selected BP are allowed. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[OUTPUT_FILE_LIST],
            dest=OUTPUT_FILE_LIST,
            default=None,
            type=str,
            nargs="+",
            metavar=FovusCliArgumentParserUtil.camel_to_snake(OUTPUT_FILE_LIST)[: -len("_List")].upper(),
            help="Specify the output files to include or exclude from transferring back to the cloud storage "
            + "using relative paths from the working directory of each task. "
            + " ".join((WILDCARD_EXPLANATION, ANY_NUMBER_OF_EXPRESSIONS, USED_FOR_OVERRIDING_JOB_CONFIG_VALUES)),
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[OUTPUT_FILE_OPTION],
            dest=OUTPUT_FILE_OPTION,
            default=None,
            type=str,
            choices=["include", "exclude"],
            help="Specify whether the output files in outputFileList should be included or excluded from "
            + "transferring back to the cloud storage after the job is completed. See outputFileList for more "
            + "information. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[PARALLELISM_CONFIG_FILES],
            dest=PARALLELISM_CONFIG_FILES,
            default=None,
            type=str,
            nargs="+",
            metavar=FovusCliArgumentParserUtil.camel_to_snake(PARALLELISM_CONFIG_FILES)[:-1].upper(),
            help="Specify the configuration files that contain Fovus Environment Tokens, if any, using "
            + "relative paths from the working directory of each task. All Fovus Environment Tokens in the "
            + "configuration files specified will be resolved to values prior to task execution. "
            + " ".join((WILDCARD_EXPLANATION, ANY_NUMBER_OF_EXPRESSIONS, USED_FOR_OVERRIDING_JOB_CONFIG_VALUES)),
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[PARALLELISM_OPTIMIZATION],
            dest=PARALLELISM_OPTIMIZATION,
            default=None,
            type=str,
            choices=["true", "false"],
            help="If enabled, Fovus will determine the optimal parallelism for parallelizing the computation of "
            + "each task to minimize the total runtime and cost based on the time-to-cost priority ratio (TCPR) "
            + "specified. To pass in the optimal parallelism to your software program, you can directly use the Fovus "
            + "environment tokens, e.g., $FovusOptVcpu, $FovusOptGpu, in your command lines or or in the input "
            + "configuration files specified by the parallelismConfigFiles job config field."
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[RUN_COMMAND],
            dest=RUN_COMMAND,
            default=None,
            type=str,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(RUN_COMMAND).upper(),
            help="Specify the command lines to launch each task. The same command lines will be executed under the "
            + f"working directory of each task. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[SCALABLE_PARALLELISM],
            dest=SCALABLE_PARALLELISM,
            default=None,
            type=str,
            choices=["true", "false"],
            help="A software program exhibits scalable parallelism if it can make use of more computing devices "
            + "(e.g., vCPUs and/or GPUs) to parallelize a larger computation task. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[STORAGE_GIB],
            dest=STORAGE_GIB,
            default=None,
            type=int,
            metavar="STORAGE_GIB",
            help="The total size of local SSD storage required to support the execution of each task. "
            + f"Format: Integer. Range: [1, 65536]. {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[IS_SUBJECT_TO_AVAILABLE_RESOURCES],
            dest=IS_SUBJECT_TO_AVAILABLE_RESOURCES,
            default=None,
            type=str,
            choices=["true", "false"],
            help="If true, the cloud strategy optimization will be performed subject to only the cloud resources "
            + "that are currently available for provisioning, so does the optimal time-cost tradeoff resulting from "
            + "the optimization. If false, the cloud strategy optimization will be performed regardless of the "
            + "current availability of cloud resources. If case the optimal virtual HPC infrastructure is "
            + "unavailable at the time, infrastructure provisioning will be attempted until it becomes available. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[ENABLE_HYPERTHREADING],
            dest=ENABLE_HYPERTHREADING,
            default=None,
            type=str,
            choices=["true", "false"],
            help="For the CPUs that support hyperthreading, enabling hyperthreading allows two threads (vCPUs) to run "
            + "concurrently on a single CPU core. For HPC workloads, disabling hyperthreading may potentially result "
            + "in performance benifits with respect to the same CPU cores (e.g., 32 threads - 32 cores with "
            + "hyperthreading disabled v.s. 64 threads - 32 cores with hyperthreading enabled), whereas enabling "
            + "hyperthreading may potentially result in cost benifits with respect to the same parallelism (e.g., 64 "
            + "threads - 32 cores with hyperthreading enabled v.s. 64 threads - 64 cores with hyperthreading disabled)."
            + " "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[SUPPORTED_CPU_ARCHITECTURES],
            dest=SUPPORTED_CPU_ARCHITECTURES,
            default=None,
            type=str,
            nargs="+",
            metavar=FovusCliArgumentParserUtil.camel_to_snake(SUPPORTED_CPU_ARCHITECTURES)[:-1].upper(),
            help="The CPU architecture(s) compatible with your workload. Running your workload on an incompatible "
            + "CPU architecture may result in a failed job. "
            + f"{ANY_NUMBER_OF_EXPRESSIONS} {USED_FOR_OVERRIDING_JOB_CONFIG_VALUES}",
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[TIME_TO_COST_PRIORITY_RATIO],
            dest=TIME_TO_COST_PRIORITY_RATIO,
            default=None,
            type=str,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(TIME_TO_COST_PRIORITY_RATIO).upper(),
            help="Fovus will optimize the cloud strategies for your job execution to minimize the total runtime "
            + "and cost based on the time-to-cost priority ratio (TCPR) specified below. TCPR defines the weights "
            + "(amount of importance) to be placed on time minimization over cost minimization on a relative scale. "
            + "In particular, a ratio of 1/0 or 0/1 will enforce cloud strategies to pursue the minimum achievable "
            + 'runtime or cost without consideration of cost or runtime, respectively. Format must be "num1/num2" '
            + "where num1 + num2 = 1, 0 <= num1 <= 1, and 0 <= num2 <= 1. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )
        self.parser.add_argument(
            *CLI_ARGUMENTS[WALLTIME_HOURS],
            dest=WALLTIME_HOURS,
            default=None,
            type=float,
            metavar=FovusCliArgumentParserUtil.camel_to_snake(WALLTIME_HOURS).upper(),
            help="The maximum time each task is allowed to run. A task will be terminated without a condition "
            + "once the walltime timer expires. Format: Real (e.g., 1.5). Range: >0. "
            + USED_FOR_OVERRIDING_JOB_CONFIG_VALUES,
        )

    def parse_args(self):
        args = self.parser.parse_args()
        self.args_dict = vars(args)
        self._convert_boolean_args_to_bool()
        FovusCliArgumentParserUtil.set_timestamp(self.args_dict)

    def _convert_boolean_args_to_bool(self):
        for key in self.args_dict:
            if key in BOOLEAN_ARGS:
                if self.args_dict[key] == "true":
                    self.args_dict[key] = True
                elif self.args_dict[key] == "false":
                    self.args_dict[key] = False

    def get_args_dict(self):
        return self.args_dict

    def merge_args_with_config(self):
        for config_filepath in self._get_config_list():
            with open(os.path.expanduser(config_filepath), encoding=UTF8) as file:
                config = json.load(file)
                for config_key in config:
                    # Config file JSON keys are expected to be camelCase,
                    # but all internal dictionary keys are snake_case.
                    config_key_snake_case = FovusCliArgumentParserUtil.camel_to_snake(config_key)
                    if FovusCliArgumentParserUtil.key_isnt_password(
                        config_key
                    ) and self._should_add_config_entry_to_args_dict(config_key_snake_case):
                        self.args_dict[config_key_snake_case] = config[config_key]

    def _get_config_list(self):
        config_list = []
        for key in [USER_CONFIG_FILE_PATH]:
            if key in self.args_dict and self.args_dict[key]:
                config_list.append(self.args_dict[key])
        if os.path.exists(os.path.expanduser(DEFAULT_USER_CONFIG_FILE_PATH)):
            config_list.append(DEFAULT_USER_CONFIG_FILE_PATH)
        return config_list

    def _should_add_config_entry_to_args_dict(self, key):
        return not (key in self.args_dict and self.args_dict[key])
