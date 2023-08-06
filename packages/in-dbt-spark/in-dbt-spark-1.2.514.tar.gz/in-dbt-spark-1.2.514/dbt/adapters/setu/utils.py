import os

import pandas
import uuid
from typing import Iterable, Iterator, Dict, Any, cast, Tuple, Optional

from dbt.events import AdapterLogger

from dbt.adapters.setu.constants import (
    DEFAULT_EXECUTION_TAGS,
    DEFAULT_PERSISTED_SESSION_DETAILS_NAME,
    DEFAULT_SPARK_CONF,
    DATAVAULT_TOKEN_PATH_KEY,
    GRESTIN_DIR_PATH_KEY,
    PERSISTED_SESSION_DETAILS_PATH_KEY,
    Platform,
    SPARK_CONF_APPEND_KEYS,
)

from dbt.adapters.setu.models import StatementState

logger = AdapterLogger("Spark")


def get_dataframe_from_json_output(json_output: dict) -> pandas.DataFrame:
    """return the pandas dataframe from json output"""
    try:
        fields = json_output["schema"]["fields"]
        columns = [field["name"] for field in fields]
        data = json_output["data"]
    except KeyError:
        raise ValueError("json output does not match expected structure")
    return pandas.DataFrame(data, columns=columns)


def get_data_from_json_output(json_output: dict) -> dict:
    """return the data from json output"""
    try:
        data = json_output["data"]
    except KeyError:
        raise ValueError("json output does not match expected structure")
    return data


def get_platform() -> Optional[Platform]:
    # this function return enum type of Platform is set

    platform_value = os.environ.get(Platform.platform_key(), None)

    if not platform_value:
        return None

    # return enum of platform
    return Platform(platform_value)


def get_grestin_certs() -> Optional[Tuple[str, str]]:
    certs = None
    if get_platform() == Platform.DARWIN_PLATFORM:
        grestin_certs_dir = os.getenv(GRESTIN_DIR_PATH_KEY, None)
        logger.info("PLATFORM : {platform}".format(platform=Platform.DARWIN_PLATFORM))
        logger.info(
            "grestin_certs_dir : {grestin_certs_dir}".format(grestin_certs_dir=grestin_certs_dir)
        )
        if grestin_certs_dir:
            certs = (
                grestin_certs_dir + "notebook.cert",
                grestin_certs_dir + "notebook.key",
            )
            # Check if certs exist
            for cert in certs:
                if not os.path.exists(cert):
                    raise Exception(f"Cert not found at path: {cert}".format(cert=cert))
        else:
            raise Exception(
                "Please set path for grestin certs directory using env var : {env_var} for platform "
                "{platform}".format(
                    env_var=GRESTIN_DIR_PATH_KEY, platform=Platform.DARWIN_PLATFORM
                )
            )
    return certs


def get_datavault_token() -> Optional[str]:
    datavault_token = None
    if get_platform() == Platform.DARWIN_PLATFORM:
        datavault_token_path = os.getenv(DATAVAULT_TOKEN_PATH_KEY, None)
        logger.info("PLATFORM : {platform}".format(platform=Platform.DARWIN_PLATFORM))
        logger.info(
            "DATAVAULT TOKEN PATH : {datavault_token_path}".format(
                datavault_token_path=datavault_token_path
            )
        )
        if datavault_token_path:
            # Check if dv exist
            if os.path.exists(datavault_token_path):
                f = open(datavault_token_path, "r")
                datavault_token = f.read()
                f.close()
            else:
                raise Exception(
                    f"Datavault token not found at path: {datavault_token_path}".format(
                        datavault_token_path=datavault_token_path
                    )
                )
        else:
            raise Exception(
                "Please set path for datavault using env var : {env_var} for platform {platform}".format(
                    env_var=DATAVAULT_TOKEN_PATH_KEY, platform=Platform.DARWIN_PLATFORM
                )
            )
    return datavault_token


def set_execution_tags_with_defaults(execution_tags: Dict[str, Any]) -> Dict[str, Any]:
    """Add defaults to user missed execution tags"""
    for key in DEFAULT_EXECUTION_TAGS.keys():
        execution_tags.setdefault(key, DEFAULT_EXECUTION_TAGS[key])
    return execution_tags


def get_session_details_file_path() -> str:
    """
    Get session details file path
    """
    session_details_file_path = os.getenv(
        PERSISTED_SESSION_DETAILS_PATH_KEY,
        os.getcwd() + "/" + DEFAULT_PERSISTED_SESSION_DETAILS_NAME,
    )
    return session_details_file_path


def set_session_runtime_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Add oklahoma runtime configurations as high-level tracking metadata
    to provide contextual information about the application"""
    if os.environ.get("oklahoma_run_id") is not None:
        metadata["oklahoma_run_id"] = os.environ.get("oklahoma_run_id")
    if os.environ.get("oklahoma_dag_name") is not None:
        metadata["oklahoma_dag_name"] = os.environ.get("oklahoma_dag_name")
    if os.environ.get("oklahoma_logical_date") is not None:
        metadata["oklahoma_logical_date"] = os.environ.get("oklahoma_logical_date")
    return metadata


def set_spark_conf_with_defaults(spark_conf: Dict[str, Any]) -> Dict[str, Any]:
    """Add defaults to user missed spark configs"""
    # To support conf.spark as prefix for passing spark configs
    for key in list(spark_conf):
        if key.startswith("conf."):
            new_key = key.replace("conf.", "", 1)
            spark_conf[new_key] = spark_conf.pop(key)

    for key in DEFAULT_SPARK_CONF.keys():
        if key in SPARK_CONF_APPEND_KEYS and key in spark_conf:
            user_config = spark_conf[key].split(",")
            default_config = DEFAULT_SPARK_CONF[key].split(",")
            user_config.extend(default_config)
            spark_conf[key] = ",".join(user_config)
        else:
            spark_conf.setdefault(key, DEFAULT_SPARK_CONF[key])
    return spark_conf


def generate_unique_session_name(session_name: str) -> str:
    """
    Append oklahoma run ids to user provided session name for oklahoma runs
    Append UUID4 to user provided session name for local runs
    """
    if os.environ.get("oklahoma_run_id") is not None:
        return "_".join([session_name, cast(str, os.environ.get("oklahoma_run_id"))])
    else:
        return "_".join([session_name, uuid.uuid4().hex])


def platform_supports_setu_session_reuse() -> bool:
    # return True if platforms supports session reuse
    # return False otherwise
    platform = get_platform()
    if not platform:
        return False
    if platform not in Platform.get_platforms_supporting_session_reuse():
        return False
    return True


def polling_intervals(
    start: Iterable[float], rest: float, max_duration: float = None
) -> Iterator[float]:
    def _intervals():
        yield from start
        while True:
            yield rest

    cumulative = 0.0
    for interval in _intervals():
        cumulative += interval
        if max_duration is not None and cumulative > max_duration:
            break
        yield interval


def waiting_for_output(statement):
    not_finished = statement.state in {
        StatementState.WAITING,
        StatementState.RUNNING,
    }
    available = statement.state == StatementState.AVAILABLE
    return not_finished or (available and statement.output is None)
