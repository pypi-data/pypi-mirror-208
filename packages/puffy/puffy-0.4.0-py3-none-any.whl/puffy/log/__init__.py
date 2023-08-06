# Copyright (c) 2019-2023, Cloudless Consulting Pty Ltd.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import os
import copy
import json
import secrets
import traceback
from ..error import StackedException

LEVELS = ["INFO", "WARN", "ERROR", "CRITICAL"]


def _getGlobalMeta():
    log_meta = os.getenv("LOG_META")
    if log_meta and (log_meta is not None):
        try:
            meta = json.loads(log_meta)
            if meta and type(meta) == dict:
                return meta
        except:
            pass

    return {}


def _get_id():
    return secrets.token_hex(10)


def _stringify_error(error):
    if (not error) or (error is None):
        return ""
    elif isinstance(error, StackedException):
        try:
            err_str = error.stringify()
            return err_str
        except:
            pass
        return ""
    elif isinstance(error, Exception):
        try:
            error_text = str(error)
            error_trace = ""
            try:
                if hasattr(error, "__traceback__") and error.__traceback__:
                    error_trace = "".join(traceback.format_tb(error.__traceback__))
                    error_trace = "\n" + error_trace if error_trace else ""
            except:
                pass
            return f"{error_text}{error_trace}"
        except:
            pass
        return ""
    else:
        try:
            err_str = str(error)
            return err_str
        except:
            pass
        return ""


global_context = {}


def set_context(**args):
    global global_context
    try:
        for key in args:
            global_context[key] = args[key]
    except:
        pass


def reset_context():
    global global_context
    global_context = {}


def get_context():
    clone = {}
    try:
        clone = copy.deepcopy(global_context)
    except:
        pass
    return clone


def log(
    level="INFO",
    message=None,
    code=None,
    time=None,
    op_id=None,
    test=None,
    metric=None,
    unit=None,
    data=None,
    errors=None,
    print_mock=None,
    **args,
):
    try:
        level = str.upper(f"{level}").strip()
        if level == "WARNING":
            level = "WARN"
        if level not in LEVELS:
            level = "INFO"

        log_data = _getGlobalMeta()

        try:
            for key in global_context:
                log_data[key] = global_context[key]
        except:
            pass

        log_data["level"] = level
        try:
            for key in args:
                try:
                    log_data[key] = args[key]
                except:
                    pass
        except:
            pass

        if message and type(message) == str:
            log_data["message"] = message

        if code and code is not None:
            log_data["code"] = code

        if type(test) == bool:
            log_data["test"] = test

        if type(time) == int or type(time) == float:
            log_data["metric"] = time
            log_data["unit"] = "ms"
        elif type(metric) == int or type(metric) == float:
            log_data["metric"] = metric
            if unit and unit is not None:
                log_data["unit"] = unit

        if op_id and op_id is not None:
            log_data["op_id"] = op_id

        if data and data is not None:
            log_data["data"] = data

        if errors and errors is not None:
            try:
                if isinstance(errors, StackedException):
                    log_data["errors"] = errors.stringify()
                elif isinstance(errors, list) or isinstance(errors, tuple):
                    if len(errors) > 0:
                        log_data["errors"] = "\n".join(
                            [_stringify_error(x) for x in errors]
                        )
                else:
                    log_data["errors"] = str(errors)
            except:
                pass

        log_str = json.dumps(log_data, default=str)

        if print_mock and print_mock is not None:
            print_mock(log_str)
        else:
            print(log_str)
    except Exception as e:
        try:
            log_str = json.dumps(
                {
                    "level": "ERROR",
                    "message": "puffy.log failed",
                    "data": {
                        "message": f"{message}",
                        "message_type": str(type(message)),
                        "code": f"{code}",
                        "code_type": str(type(code)),
                    },
                    "errors": str(e),
                },
                default=str,
            )
            if print_mock and print_mock is not None:
                print_mock(log_str)
            else:
                print(log_str)
        except:
            pass
        pass
