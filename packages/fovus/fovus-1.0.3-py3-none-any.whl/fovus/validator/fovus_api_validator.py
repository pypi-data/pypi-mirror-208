import json
import os
from http import HTTPStatus

import jsonschema

from fovus.constants.cli_constants import (
    PARALLELISM_OPTIMIZATION,
    SCALABLE_PARALLELISM,
    MIN_VCPU,
    MAX_VCPU,
    MIN_GPU,
    MAX_GPU,
)
from fovus.constants.fovus_api_constants import (
    PAYLOAD_CONSTRAINTS,
    PAYLOAD_JOB_CONSTRAINTS,
    PAYLOAD_TASK_CONSTRAINTS,
    PAYLOAD_TIME_COST_PRIORITY_RATIO,
)
from fovus.constants.util_constants import UTF8
from fovus.exception.user_exception import UserException
from fovus.root_config import ROOT_DIR

SCHEMA_PATH_PREFIX = "schema/"
SCHEMA_PATH_SUFFIX = "_schema.json"


class FovusApiValidator:  # pylint: disable=too-few-public-methods
    @staticmethod
    def validate(payload, api_method):
        schema_path = os.path.abspath(
            os.path.join(ROOT_DIR, SCHEMA_PATH_PREFIX, "".join((api_method.lower(), SCHEMA_PATH_SUFFIX)))
        )
        with open(schema_path, encoding=UTF8) as schema_file:
            schema = json.load(schema_file)
            try:
                jsonschema.validate(payload, schema)
            except jsonschema.exceptions.ValidationError as exception:
                raise UserException(
                    HTTPStatus.BAD_REQUEST.value, FovusApiValidator.__name__, exception.message
                ) from exception

    @staticmethod
    def validate_additional_create_job_fields(payload):
        FovusApiValidator._validate_time_cost_to_priority_ratio(
            payload[PAYLOAD_CONSTRAINTS][PAYLOAD_JOB_CONSTRAINTS][PAYLOAD_TIME_COST_PRIORITY_RATIO]
        )
        FovusApiValidator._validate_parallelism_optimization_allowed_value(
            payload[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][PARALLELISM_OPTIMIZATION],
            payload[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][SCALABLE_PARALLELISM],
        )
        FovusApiValidator._validate_min_max_vcpu(
            payload[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MIN_VCPU],
            payload[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MAX_VCPU],
        )
        FovusApiValidator._validate_min_max_gpu(
            payload[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MIN_GPU],
            payload[PAYLOAD_CONSTRAINTS][PAYLOAD_TASK_CONSTRAINTS][MAX_GPU],
        )

    @staticmethod
    def _validate_time_cost_to_priority_ratio(time_cost_to_priority_ratio):
        time_cost_to_priority_ratio_exception = UserException(
            HTTPStatus.BAD_REQUEST,
            FovusApiValidator.__name__,
            'timeToCostPriorityRatio must be of the form "time/cost" where 0 <= time <= 1, '
            + "0 <= cost <= 1, and time + cost = 1",
        )

        time, cost = time_cost_to_priority_ratio.split("/")
        time, cost = float(time), float(cost)
        for value in (time, cost):
            if value < 0 or value > 1:
                raise time_cost_to_priority_ratio_exception
        if time + cost != 1:
            raise time_cost_to_priority_ratio_exception

    @staticmethod
    def _validate_parallelism_optimization_allowed_value(parallelism_optimization, scalable_parallelism):
        if parallelism_optimization and not scalable_parallelism:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                FovusApiValidator.__name__,
                "parallelismOptimization is only allowed to be set to true when scalableParallelism is set to true",
            )

    @staticmethod
    def _validate_min_max_vcpu(min_vcpu, max_vcpu):
        if min_vcpu > max_vcpu:
            raise UserException(
                HTTPStatus.BAD_REQUEST, FovusApiValidator.__name__, "minvCpu must be less than or equal to maxvCpu"
            )

    @staticmethod
    def _validate_min_max_gpu(min_gpu, max_gpu):
        if min_gpu > max_gpu:
            raise UserException(
                HTTPStatus.BAD_REQUEST, FovusApiValidator.__name__, "minGpu must be less than or equal to maxGpu"
            )
