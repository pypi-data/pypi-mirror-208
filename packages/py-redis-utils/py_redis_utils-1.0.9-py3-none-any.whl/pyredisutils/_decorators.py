import logging
from functools import wraps
from typing import List, Tuple, Any

import redis

from pyredisutils._settings import Settings


def jwt_redis_auth(
    redis_instance: redis = None,
    channel_name: str = "",
    publish_template: dict = None,
    response_template: dict = None,
    publish_changes: List[List] = None,
    response_changes: List[List] = None,
) -> Any | Tuple[Any, int]:
    """
    Decorator to check via Redis if user has valid JWT token to access services.
    In this decorator you pass all the necessary data to check via Redis if user has required access.
    :param redis_instance: Instance of the Redis. This instance is used to connect to redis, publish messages, and retrieve a response.
    :param channel_name: The name of the Redis channel where message should be published.
    :param publish_template: The template of the *publish* message. It should be dictionary that contains all necessary data to publish message.
    You can specify some fields in values that will be replaced in the decorator. Currently, by default are replacing *_ID* value to UUID,
    *_USER_ID* value to the *id* value from the Bearer token, *_ROLES* to the *roles* from Bearer token and *_TOKEN* to the JWT token value.
    Those field will be skipped if they do not exist. Also, you can add custom replaceable fields to the *publish_changes* field.
    :param response_template: The template of the *response* message that will come from Redis. This template should be as Dictionary and should contain
    All the values that Redis will return in Successful case. There are can be replaceable fields. By default, decorator changes only *_ID* to the UUID like in
    *publish_message*. Also, you can specify your own custom changeable fields in *response_changes* key parameter.
    :param publish_changes: Field that contains custom replaceable values for publish message. It should be List of Lists *List[List]*.
    For example, you should pass this kind of list -  [["FIRST", "SECOND"], ["ABC", "QWE"]], and the decorator will look for value "FIRST" and change it to the
    "SECOND", as well as will look for value "ABC" and will change it to the "QWE". In that way, your list should contain lists with two parameters, where first
    is the old value that should be changed, and the second is the value to which it will be changed.
    :param response_changes: Field that contains custom replaceable values for response message. It should be List of Lists *List[List]*.
    For example, you should pass this kind of list -  [["FIRST", "SECOND"], ["ABC", "QWE"]], and the decorator will look for value "FIRST" and change it to the
    "SECOND", as well as will look for value "ABC" and will change it to the "QWE". In that way, your list should contain lists with two parameters, where first
    is the old value that should be changed, and the second is the value to which it will be changed.
    :return: Returns nothing if Redis returned Successful message, and will return Flask Response *Any | Tuple[Any, int]* if Any error occurred.
    """
    settings = Settings(
        redis_instance,
        channel_name,
        publish_template,
        response_template,
        publish_changes,
        response_changes,
    )

    def funct_decorator(org_function):
        @wraps(org_function)
        def authorize(*args, **kwargs):
            # Applies all necessary settings
            settings.get_token()
            settings.generate_id()
            settings.update_publish_replaces()
            settings.update_response_replaces()
            settings.transform_publish_template()
            settings.transform_response_template()

            # Publishes message to Redis
            if settings.publish_message_to_redis():
                return org_function(*args, **kwargs)
            logging.info("Redis response - Token is not valid")
            return settings.make_response("Unauthorized", 401)

        return authorize

    return funct_decorator


def check_user_permissions(
    redis_instance: redis = None,
    channel_name: str = "",
    publish_template: dict = None,
    response_template: dict = None,
    publish_changes: List[List] = None,
    response_changes: List[List] = None,
) -> Any | Tuple[Any, int]:
    """
    Decorator to check via Redis if user has permissions to access certain data.
    In this decorator you pass all the necessary data to check via Redis if user has required access.
    :param redis_instance: Instance of the Redis. This instance is used to connect to redis, publish messages, and retrieve a response.
    :param channel_name: The name of the Redis channel where message should be published.
    :param publish_template: The template of the *publish* message. It should be dictionary that contains all necessary data to publish message.
    You can specify some fields in values that will be replaced in the decorator. Currently, by default are replacing *_ID* value to UUID,
    *_USER_ID* value to the *id* value from the Bearer token, *_ROLES* to the *roles* from Bearer token and *_TOKEN* to the JWT token value.
    Those field will be skipped if they do not exist. Also, you can add custom replaceable fields to the *publish_changes* field.
    :param response_template: The template of the *response* message that will come from Redis. This template should be as Dictionary and should contain
    All the values that Redis will return in Successful case. There are can be replaceable fields. By default, decorator changes only *_ID* to the UUID like in
    *publish_message*. Also, you can specify your own custom changeable fields in *response_changes* key parameter.
    :param publish_changes: Field that contains custom replaceable values for publish message. It should be List of Lists *List[List]*.
    For example, you should pass this kind of list -  [["FIRST", "SECOND"], ["ABC", "QWE"]], and the decorator will look for value "FIRST" and change it to the
    "SECOND", as well as will look for value "ABC" and will change it to the "QWE". In that way, your list should contain lists with two parameters, where first
    is the old value that should be changed, and the second is the value to which it will be changed.
    :param response_changes: Field that contains custom replaceable values for response message. It should be List of Lists *List[List]*.
    For example, you should pass this kind of list -  [["FIRST", "SECOND"], ["ABC", "QWE"]], and the decorator will look for value "FIRST" and change it to the
    "SECOND", as well as will look for value "ABC" and will change it to the "QWE". In that way, your list should contain lists with two parameters, where first
    is the old value that should be changed, and the second is the value to which it will be changed.
    :return: Returns nothing if Redis returned Successful message, and will return Flask Response *Any | Tuple[Any, int]* if Any error occurred.
    """
    settings = Settings(
        redis_instance,
        channel_name,
        publish_template,
        response_template,
        publish_changes,
        response_changes,
    )

    def wrapper(org_function):
        @wraps(org_function)
        def check(*args, **kwargs):
            # Applies all necessary settings
            settings.get_token()
            settings.get_user_id_from_token()
            settings.get_roles_from_token()
            settings.generate_id()
            settings.update_publish_replaces()
            settings.update_response_replaces()
            settings.transform_publish_template()
            settings.transform_response_template()

            # Publishes message to Redis
            if settings.publish_message_to_redis():
                return org_function(*args, **kwargs)
            logging.info("Redis response - User does not has access")
            return settings.make_response("Forbidden", 403)

        return check

    return wrapper
