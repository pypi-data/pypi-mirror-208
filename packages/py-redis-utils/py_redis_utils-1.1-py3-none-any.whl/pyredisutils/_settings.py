import copy
import json
import logging
import time
import uuid
from dataclasses import dataclass
from json import JSONDecodeError
from typing import List, Dict, Tuple, Any

import deepdiff
import redis
from flask import make_response, jsonify, request, Response
from jwt import decode


@dataclass
class Settings:
    """
    Dataclass to store all necessary settings to communicate with Redis.
    Class is storing publish message that will be published to Redis.
    After what Redis will retrieve a response that will be checked with the response_template.
    If the response is the same as template then it means Redis approved published message.
    If response is not the same then you will receive Flask Response with Error.
    Initially, you must pass *redis_instance*, *channel_name* *publish_template* and *response_template*.
    All others parameters are not mandatory.
    """

    _redis_instance: redis = None
    _channel_name: str = ""
    _publish_template: Dict = None
    _response_template: Dict = None
    _publish_changes: List[List] = None
    _response_changes: List[List] = None
    _publish_replace: List[List] = None
    _response_replace: List[List] = None
    _request_id: str = ""
    _token: str = ""
    _user_id: str = ""
    _roles: List[str] = None

    @property
    def redis_instance(self) -> redis:
        """
        Return Redis instance.
        :return: Redis instance
        """
        return self._redis_instance

    @redis_instance.setter
    def redis_instance(self, v: redis) -> None:
        """
        Set Redis instance.
        :param v: Redis instance.
        :return: None
        """
        self._redis_instance = v

    @property
    def channel_name(self) -> str:
        """
        Return Redis channel name.
        :return: Redis channel name as str
        """
        return self._channel_name

    @channel_name.setter
    def channel_name(self, v: str) -> None:
        """
        Set Redis channel name.
        :param v: Redis channel name as a str.
        :return: None
        """
        self._channel_name = v

    @property
    def publish_template(self) -> Dict:
        """
        Get publish template.
        :return: Dict
        """
        return self._publish_template

    @publish_template.setter
    def publish_template(self, v: Dict) -> None:
        """
        Set publish template.
        :param v: Publish Template as a dictionary.
        :return: None
        """
        self._publish_template = copy.deepcopy(v)

    @property
    def response_template(self) -> Dict:
        """
        Get response template.
        :return: Dict
        """
        return self._response_template

    @response_template.setter
    def response_template(self, v: Dict) -> None:
        """
        Set response template.
        :param v: Response Template as a dictionary.
        :return: None
        """
        self._response_template = copy.deepcopy(v)

    @property
    def publish_replace(self) -> List[List]:
        """
        Get publish replace.
        :return: List[List]
        """
        return self._publish_replace

    @publish_replace.setter
    def publish_replace(self, v: List[List]) -> None:
        """
        Set publish replace.
        :param v: List of replaces that should be applied to publish message.
        :return: None
        """
        self._publish_replace = v

    @property
    def response_replace(self) -> List[List]:
        """
        Get response replace.
        :return: List[List]
        """
        return self._response_replace

    @response_replace.setter
    def response_replace(self, v: List[List]) -> None:
        """
        Set response replace.
        :param v: List of replaces that should be applied to response message.
        :return: None
        """
        self._response_replace = v

    @property
    def publish_changes(self) -> List[List]:
        """
        Get publish changes.
        :return: List[List]
        """
        return self._publish_changes

    @publish_changes.setter
    def publish_changes(self, v: List[List]) -> None:
        """
        Set publish changes.
        :param v: List of custom changes that should be applied to publish message.
        :return: None
        """
        self._publish_changes = v

    @property
    def response_changes(self) -> List[List]:
        """
        Get response changes.
        :return: List[List]
        """
        return self._response_changes

    @response_changes.setter
    def response_changes(self, v: List[List]) -> None:
        """
        Set response changes.
        :param v: List of custom changes that should be applied to response message.
        :return: None
        """
        self._response_changes = v

    @property
    def request_id(self) -> str:
        """
        Get request ID.
        :return: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, v: str) -> None:
        """
        Set request ID.
        :param v: Request ID.
        :return: None
        """
        self._request_id = v

    @property
    def token(self) -> str:
        """
        Get token.
        :return: str
        """
        return self._token

    @token.setter
    def token(self, v: str) -> None:
        """
        Set token.
        :param v: JWT Token.
        :return: None
        """
        self._token = v

    @property
    def user_id(self) -> str:
        """
        Get User ID.
        :return: str
        """
        return self._user_id

    @user_id.setter
    def user_id(self, v: str) -> None:
        """
        Set User ID.
        :param v: User ID.
        :return: None
        """
        self._user_id = v

    @property
    def roles(self) -> List[str]:
        """
        Get User roles.
        :return: List[str]
        """
        return self._roles

    @roles.setter
    def roles(self, v: List[str]) -> None:
        """
        Set User roles.
        :param v: List of User roles.
        :return: List[str]
        """
        self._roles = v

    def update_publish_replaces(self) -> None:
        """
        Updates Publish Replaces with custom changes.
        :return: None
        """
        if self.publish_changes:
            self.publish_replace = [
                ["_USER_ID", self.user_id],
                ["_ROLES", self.roles],
                ["_ID", self.request_id],
                ["_TOKEN", self.token],
                *self.publish_changes,
            ]
        else:
            self.publish_replace = [
                ["_USER_ID", self.user_id],
                ["_ROLES", self.roles],
                ["_ID", self.request_id],
                ["_TOKEN", self.token],
            ]

    def update_response_replaces(self) -> None:
        """
        Updates Response Replaces with custom changes.
        :return:
        """
        if self.response_changes:
            self.response_replace = [["_ID", self.request_id], *self.response_changes]
        else:
            self.response_replace = [["_ID", self.request_id]]

    def get_token(self) -> None | Tuple[Response, int]:
        """
        Method to get token from the request header.
        :return: None
        """
        if token := request.headers.get("Authorization"):
            self.token = token.replace("Bearer ", "")
        else:
            logging.error("Bearer Token was not found.")
            return self.make_response("Token is missing", 401)

    def decode_token(self) -> Dict[str, Any]:
        """
        Method to decode JWT token.
        :return: Dict of decoded token
        """
        return decode(
            self.token.replace("Bearer", ""),
            algorithms=["HS256"],
            options={"verify_signature": False},
        )

    def generate_id(self) -> None:
        """
        Method to generate request ID.
        :return: None
        """
        self.request_id = str(uuid.uuid4())

    def get_user_id_from_token(self) -> None:
        """
        Method to get User ID from the token.
        :return: None
        """
        self.user_id = self.decode_token().get("id")

    def get_roles_from_token(self) -> None:
        """
        Method to get all roles from the token.
        :return: None
        """
        self.roles = self.decode_token().get("roles")

    def transform_publish_template(self) -> None:
        """
        Method to transform Publish message. Replaceable values will be applied.
        :return: None
        """
        self._transform_dict(self.publish_template, self.publish_replace)

    def transform_response_template(self) -> None:
        """
        Method to transform Response message. Replaceable values will be applied.
        :return: None
        """
        self._transform_dict(self.response_template, self.response_replace)

    def publish_message_to_redis(self) -> bool | Tuple[Response, int]:
        """
        Method that connects with redis and publishes message.
        Then waits for 5 seconds to get Redis response.
        This response then is being validated using diff.
        If response is successful then returns True.
        If Redis returned unsuccessful response then function returns False.
        If any other error occurred then function returns Flask Response with error.
        :return: bool | Tuple[Response, int]
        """
        try:
            redis_client = self.redis_instance.client()
            pubsub = redis_client.pubsub()
            pubsub.subscribe(f"{self.channel_name}.reply")
            redis_client.publish(
                self.channel_name,
                json.dumps(self.publish_template),
            )
            try:
                timeout = 5.0
                live_timeout = time.time() + 5
                logging.info("Waiting for Redis response.")
                pubsub.get_message()
                while True:
                    if time.time() > live_timeout:
                        raise TimeoutError
                    if not (message := pubsub.get_message(timeout=timeout)):
                        raise TimeoutError
                    redis_response = {
                        key: self._transform_redis_response(value)
                        for key, value in message.items()
                    }
                    diff = deepdiff.DeepDiff(self.response_template, redis_response)
                    if diff == {}:
                        pubsub.unsubscribe(f"{self.channel_name}.reply")
                        redis_client.close()
                        return True
                    values = diff.get("values_changed", {})
                    for change in values.values():
                        if change["old_value"] == self.request_id:
                            continue
                    redis_client.close()
                    return False
            except TimeoutError:
                logging.error("Haven't received any answer from Redis for 5 seconds.")
                redis_client.close()
                return self.make_response("Gateway Timeout", 504)
        except redis.exceptions.ConnectionError:
            return self.make_response("Bad Gateway", 502)

    @classmethod
    def _transform_dict(cls, data: Dict, change_fields: List[List]) -> Dict:
        """
        Method to dynamically transform dictionary.
        Method finds value that should be replaced, and replaces them.
        :param data: Initial dictionary that should be transformed.
        :param change_fields: List of lists, where contains data that should be changed.
        For example, you should pass this kind of list -  [["FIRST", "SECOND"], ["ABC", "QWE"]],
        and the decorator will look for value "FIRST" and change it to the
        "SECOND", as well as will look for value "ABC" and will change it to the "QWE".
        In that way, your list should contain lists with two parameters, where first
        is the old value that should be changed, and the second is the value to which it will be changed.
        :return: Transformed dictionary
        """
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = cls._transform_dict(value, change_fields)
            for change_field in change_fields:
                if change_field[0] == value:
                    data[key] = change_field[1]
        return data

    @classmethod
    def _transform_redis_response(cls, data) -> Dict:
        """
        Method to transform response from Redis message broker to Python Dictionary.
        :param data: Redis response values
        :return: Returns transformed redis value as a Dict
        """
        try:
            loaded_d = data if isinstance(data, dict) else json.loads(data)
            if not isinstance(loaded_d, dict):
                return loaded_d
            for key, value in loaded_d.items():
                loaded_d[key] = cls._transform_redis_response(value)
        except (JSONDecodeError, TypeError):
            return data.decode("utf-8") if isinstance(data, bytes) else data
        return loaded_d

    @classmethod
    def make_response(cls, message: str, status_code: int) -> Response:
        """
        Method to make a Flask response and return it back.
        This response will contain JSON body with 2 parameters - `message`
        (response message, answer) and `status_code` (integer value of HTTP response code).
        :param message: Message on the response
        :param status_code:
        :return: Flask Response
        """
        return (
            make_response(
                jsonify(
                    {
                        "message": message,
                        "statusCode": status_code,
                    }
                )
            ),
            status_code,
        )
