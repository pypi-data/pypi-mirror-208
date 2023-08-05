import ast
import importlib.util
import json
import logging
import os
import re
import sys
from datetime import timedelta, datetime, date
from pathlib import Path
from typing import Dict, Any, Pattern, Match, AnyStr, Optional, Union
from urllib.parse import urlparse

import boto3
import pendulum
from airflow.models import Variable

from datamorphairflow.datamorph_constants import DATAMORPH_PROPERTY_WORKFLOW, DATAMORPH_PROPERTY_DATAMORPHCONF, \
    DATAMORPH_PROPERTIES, DATAMORPH_PROPERTY_SUBSTITUTIONS, DATAMORPH_PROPERTY_PARAMETERS, DATAMORPH_PREFIX, \
    DATAMORPH_PROPERTY_NAME, DEFAULT_AWS_REGION


def load_JSON_file(fname):
    """
    load JSON file in the given path
    :param fname:
    :return:
    """
    with open(fname, "r") as f:
        data = json.load(f)
    return data


def remove_key(dictItem, key):
    """
    removes key from the dict object if key is present
    :param dictItem: dictionary object to remove key from
    :param key: string key name
    :return:
    """
    if key in dictItem:
        r = dict(dictItem)
        del r[key]
        return r
    else:
        return dictItem


def remove_keys(dictItem, keys):
    """
    removes key from the dict object if key is present
    :param dictItem: dictionary object to remove key from
    :param keys: list of string key name
    :return:
    """
    for key in keys:
        if key in dictItem:
            del dictItem[key]


def check_dict_key(item_dict: Dict[str, Any], key: str) -> bool:
    """
    Check if the key is included in given dictionary, and has a valid value.
    :param item_dict: a dictionary to test
    :type item_dict: Dict[str, Any]
    :param key: a key to test
    :type key: str
    :return: result to check
    :type: bool
    """
    return bool(key in item_dict and item_dict[key] is not None)


def load_json_config_file(config_file_path: Optional[str] = None, s3bucket: Optional[str] = None,
                          s3key: Optional[str] = None):
    """
    load json config file, example with workflow and variables attribute.
    substitute ${VAR} with its value from the variables key value pair.
    variables may or may not be provided.
    {
        "datamorphConf":{
            "variables":{
               "ENV1":"value1",
               "ENV2":"value2"
                }
        }
        "workflow": [
        "properties": {
            "parm1": 8000,
            "parm2": "${ENV1}",
            "parm3": "${ENV2}"
        }
        ]
    }
    :param config_file_path:
    :return:
    """

    def _substitute_params_in_dict(d, params, var_name):
        for key in d.keys():
            v = d.get(key)
            if isinstance(v, str):
                d[key] = re.sub('\$(\w+)', lambda m: "{{var.json." + var_name + "['" + m.group(1) + "']}}", v)
            elif isinstance(v, list):
                for each in v:
                    if not isinstance(each, str):
                        _substitute_params_in_dict(each, params, var_name)
            elif isinstance(v, dict):
                _substitute_params(v, params, var_name)

    def _substitute_params(d, params, var_name):
        if isinstance(d, list):
            for each in d:
                _substitute_params_in_dict(each, params, var_name)
        else:
            _substitute_params_in_dict(d, params, var_name)

    def _substitute_in_dict(d, variables):
        for key in d.keys():
            v = d.get(key)
            if isinstance(v, str):
                d[key] = re.sub('\${(\w+)}', lambda m: variables.get(m.group(1)), v)
            elif isinstance(v, list):
                for each in v:
                    if not isinstance(each, str):
                        _substitute_in_dict(each, variables)
            elif isinstance(v, dict):
                _substitute_vars(v, variables)

    def _substitute_vars(d, variables):
        if isinstance(d, list):
            for each in d:
                _substitute_in_dict(each, variables)
        else:
            _substitute_in_dict(d, variables)

    def _retrive_config(app_config):
        workflow = app_config[DATAMORPH_PROPERTY_WORKFLOW]
        datamorphConf = app_config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTIES]
        # Substitute variables
        if check_dict_key(datamorphConf, DATAMORPH_PROPERTY_SUBSTITUTIONS):
            variables = datamorphConf[DATAMORPH_PROPERTY_SUBSTITUTIONS]
            _substitute_vars(app_config, variables)
        # Add parameters to airflow variables
        if check_dict_key(datamorphConf, DATAMORPH_PROPERTY_PARAMETERS):
            dag_name = app_config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTY_NAME]
            var_name = DATAMORPH_PREFIX + dag_name
            parameters = app_config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTIES][DATAMORPH_PROPERTY_PARAMETERS]
            obj = Variable.get(var_name, default_var=None, deserialize_json=False)
            if obj is None:
                Variable.set(var_name, json.dumps(parameters), serialize_json=False)
            # check for any parameter substitutions in the workflow
            _substitute_params(workflow, parameters, var_name)

        return app_config

    if config_file_path:
        with open(config_file_path, 'r') as f:
            app_config = json.load(f)
            updated_config = _retrive_config(app_config)
            return updated_config

    elif s3key and s3bucket:
        s3res = boto3.resource('s3',
                               region_name=DEFAULT_AWS_REGION)
        content_object = s3res.Object(s3bucket, s3key)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        app_config = json.loads(file_content)
        updated_config = _retrive_config(app_config)
        return updated_config

    else:
        raise Exception('Configuration file not found: '.format(config_file_path))


def get_python_callable_from_S3(python_callable_name, python_callable_file):
    """
    Uses python filepath and callable name to import a valid callable for use in PythonOperator
    :param python_callable_name:
    :param python_callable_file:
    :return:
    """

    # parse s3 url
    s3url = python_callable_file
    s3urlparse = urlparse(s3url, allow_fragments=False)
    bucketname = s3urlparse.netloc
    file_to_read = s3urlparse.path.lstrip('/')

    # create a local copy of the python script in the current working directory and delete after the callable  is created
    filetowrite = file_to_read.split(sep="/")[-1]
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    here = os.path.join(curr_dir, filetowrite)

    # get s3 file object
    s3 = boto3.client("s3", region_name=DEFAULT_AWS_REGION)

    # download file from s3 and create a local copy
    try:
        s3.download_file(bucketname, file_to_read, here)
    except:
        raise Exception("Unable to read from S3 path:", bucketname + "/" + file_to_read)

    # create callable
    python_callable = get_python_callable_from_local_filesystem(python_callable_name, here)

    # delete local copy of the python file
    if os.path.isfile(here):
        os.remove(here)
    else:
        logging.error("Error: %s file not found" % here)
    return python_callable


def get_python_callable_from_local_filesystem(python_callable_name, python_callable_file):
    """
    Uses python filepath and callable name to import a valid callable for use in PythonOperator
    :param python_callable_name:
    :param python_callable_file:
    :return:
    """
    python_callable_file = os.path.expandvars(python_callable_file)
    if not os.path.isabs(python_callable_file):
        raise Exception("`python_callable_file` must be absolute path: ", python_callable_file)
    python_file_path = Path(python_callable_file).resolve()
    module_name = python_file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, python_callable_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    python_callable = getattr(module, python_callable_name)

    return python_callable


def get_python_callable(python_callable_name, python_callable_file):
    """
    Uses python filepath and callable name to import a valid callable for use in PythonOperator
    :param python_callable_name:
    :param python_callable_file:
    :return:
    """
    if python_callable_file.startswith("s3:"):
        return get_python_callable_from_S3(python_callable_name, python_callable_file)
    else:
        return get_python_callable_from_local_filesystem(python_callable_name, python_callable_file)


def get_datetime(
        date_value: Union[str, datetime, date], timezone: str = "UTC"
) -> datetime:
    """
    Takes value from DAG config and generates valid datetime. Defaults to
    today, if not a valid date or relative time (1 hours, 1 days, etc.)
    :param date_value: either a datetime (or date), a date string or a relative time as string
    :type date_value: Uniont[datetime, date, str]
    :param timezone: string value representing timezone for the DAG
    :type timezone: str
    :returns: datetime for date_value
    :type: datetime.datetime
    """
    try:
        local_tz: pendulum.timezone = pendulum.timezone(timezone)
    except Exception as err:
        raise Exception("Failed to create timezone") from err
    if isinstance(date_value, datetime):
        return date_value.replace(tzinfo=local_tz)
    if isinstance(date_value, date):
        return datetime.combine(date=date_value, time=datetime.min.time()).replace(
            tzinfo=local_tz
        )
    # Try parsing as date string
    try:
        return pendulum.parse(date_value).replace(tzinfo=local_tz)
    except pendulum.parsing.exceptions.ParserError:
        # Try parsing as relative time string
        rel_delta: timedelta = get_time_delta(date_value)
        now: datetime = (
            datetime.today()
                .replace(hour=0, minute=0, second=0, microsecond=0)
                .replace(tzinfo=local_tz)
        )
        if not rel_delta:
            return now
        return now - rel_delta


def get_time_delta(time_string: str) -> timedelta:
    """
    Takes a time string (1 hours, 10 days, etc.) and returns
    a python timedelta object
    :param time_string: the time value to convert to a timedelta
    :type time_string: str
    :returns: datetime.timedelta for relative time
    :type datetime.timedelta
    """
    # pylint: disable=line-too-long
    rel_time: Pattern = re.compile(
        pattern=r"((?P<hours>\d+?)\s+hour)?((?P<minutes>\d+?)\s+minute)?((?P<seconds>\d+?)\s+second)?((?P<days>\d+?)\s+day)?",
        # noqa
        flags=re.IGNORECASE,
    )
    parts: Optional[Match[AnyStr]] = rel_time.match(string=time_string)
    if not parts:
        raise Exception(f"Invalid relative time: {time_string}")
    # https://docs.python.org/3/library/re.html#re.Match.groupdict
    parts: Dict[str, str] = parts.groupdict()
    time_params = {}
    if all(value is None for value in parts.values()):
        raise Exception(f"Invalid relative time: {time_string}")
    for time_unit, magnitude in parts.items():
        if magnitude:
            time_params[time_unit]: int = int(magnitude)
    return timedelta(**time_params)


def remove_node_suffix(node: str) -> str:
    if node.endswith('_Success'):
        return node[:-8]
    elif node.endswith('_Failure'):
        return node[:-8]
    else:
        return node.rsplit(":")[0]



def is_s3_file(filepath: str) -> bool:
    return filepath.startswith("s3://")



