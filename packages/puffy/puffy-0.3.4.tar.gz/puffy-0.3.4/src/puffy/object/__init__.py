# Copyright (c) 2019-2023, Cloudless Consulting Pty Ltd.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.


def dotProps(obj, keys, set_value=None, set_mode=False):
    if not keys or not obj or not isinstance(obj, dict) or not isinstance(keys, str):
        return None

    value = obj
    _keys = keys.split(".")
    keys_last_index = len(_keys) - 1
    for idx, key in enumerate(_keys):
        last_key = idx == keys_last_index
        if key in value:
            if last_key:
                if set_mode:
                    value[key] = set_value
            elif not isinstance(value[key], dict):
                value[key] = {}

            value = value[key]
        else:
            if last_key:
                value[key] = set_value if set_mode else None
            else:
                value[key] = {}
            value = value[key]

    return value


class JSON(dict):
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

    def g(self, keys):
        return dotProps(self, keys)

    def s(self, keys, value):
        return dotProps(self, keys, value, True)
