import time
from enum import Enum
from http import HTTPStatus

import boto3
from botocore.exceptions import ClientError
from pycognito.aws_srp import AWSSRP

from fovus.constants.fovus_api_constants import COGNITO_REGION
from fovus.exception.user_exception import UserException
from fovus.util.aws_util import AwsUtil
from fovus.util.fovus_cli_argument_parser_util import FovusCliArgumentParserUtil


class AwsCognitoAuthType(Enum):
    USER_SRP_AUTH = "USER_SRP_AUTH"  # nosec


class UserAttribute(Enum):
    USER_ID = "custom:userId"


class AwsCognitoAdapter:
    def __init__(self):
        self.cognito_client = boto3.client("cognito-idp", region_name=COGNITO_REGION)
        self.access_token = None
        self.access_token_expiration_epoch_time = None
        self.refresh_token = None
        self.id_token = None
        self.device_key = None
        self.user_attributes = None

    def authenticate(self, auth_type, auth_parameters, client_id):
        FovusCliArgumentParserUtil.validate_password_exists()
        try:
            if auth_type.value == AwsCognitoAuthType.USER_SRP_AUTH.value:
                aws = AWSSRP(
                    **auth_parameters,
                    password=FovusCliArgumentParserUtil.get_password(),
                    client_id=client_id,
                    client=self.cognito_client,
                )
                tokens = aws.authenticate_user()
            AwsUtil.confirm_successful_response(tokens, self.__class__.__name__)
            (
                self.access_token,
                self.access_token_expiration_epoch_time,
                self.refresh_token,
                self.id_token,
            ) = self._extract_tokens_from_response(tokens)
            self.user_attributes = self.cognito_client.get_user(AccessToken=self.access_token)["UserAttributes"]
        except ClientError as error:
            AwsUtil.handle_client_error(error, self.__class__.__name__)

    def _extract_tokens_from_response(self, response):
        authentication_result = response["AuthenticationResult"]
        return (
            authentication_result["AccessToken"],
            time.time() + authentication_result["ExpiresIn"],
            authentication_result["RefreshToken"],
            authentication_result["IdToken"],
        )

    def get_access_token(self):
        return self.access_token

    def get_access_token_expiration_epoch_time(self):
        return self.access_token_expiration_epoch_time

    def get_refresh_token(self):
        return self.refresh_token

    def get_id_token(self):
        return self.id_token

    def get_device_key(self):
        return self.device_key

    def get_user_attribute(self, attribute: UserAttribute):
        for user_attribute in self.user_attributes:
            if user_attribute["Name"] == attribute.value:
                return user_attribute["Value"]
        raise UserException(
            HTTPStatus.NOT_FOUND, self.__class__.__name__, f"User attribute {attribute.value} not found"
        )

    @staticmethod
    def get_user_srp_auth_parameters(username, user_pool_id):
        return {"username": username, "pool_id": user_pool_id}

    @staticmethod
    def get_refresh_token_auth_parameters(refresh_token, device_key):
        return {"REFRESH_TOKEN": refresh_token, "DEVICE_KEY": device_key}
