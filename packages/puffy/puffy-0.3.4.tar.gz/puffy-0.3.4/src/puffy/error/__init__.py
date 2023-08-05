# Copyright (c) 2019-2023, Cloudless Consulting Pty Ltd.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from collections.abc import Iterable
import traceback
import inspect


class _WrappedFunction:
    def __init__(self, name="_unknown_function", file="unknown", line=0):
        self.name = name
        self.file = file
        self.line = line
        self.description = f'File "{file}", line {line}, in {name}'


class StackedException(Exception):
    def __init__(self, *errors):
        def __flatten(*errors):
            stack = []
            head, *tails = errors
            _errors = errors
            self.__wrapped_fn = None
            if head and isinstance(head, _WrappedFunction):
                self.__wrapped_fn = head
                _errors = tails

            for error in _errors:
                if isinstance(error, StackedException):
                    stack.extend(error.stack)
                elif isinstance(error, Exception):
                    stack.append(error)
                elif (
                    isinstance(error, str)
                    or isinstance(error, int)
                    or isinstance(error, float)
                ):
                    stack.append(Exception(error))
                elif isinstance(error, Iterable):
                    stack.extend(__flatten(error))
                else:
                    stack.append(Exception(error))
            return stack

        self.stack = [] if len(errors) == 0 else __flatten(*errors)

        ln = len(self.stack)
        head = "Unknown error" if ln == 0 else self.stack[0]
        super().__init__(head)

    def stringify(self):
        if len(self.stack):
            errors = []
            for error in self.stack:
                error_text = str(error)
                error_trace = ""
                error_meta = (
                    f"\n  {self.__wrapped_fn.description}" if self.__wrapped_fn else ""
                )
                if hasattr(error, "__traceback__") and error.__traceback__:
                    error_trace = "".join(traceback.format_tb(error.__traceback__))
                    error_trace = "\n" + error_trace if error_trace else ""

                errors.append(
                    f"error: {error_text}{error_trace if error_trace else error_meta}"
                )
            return "\n".join(errors)
        else:
            return ""


def catch_errors(arg):
    if not arg:
        raise Exception("Missing required argument.")

    isAsyncFunction = inspect.iscoroutinefunction(arg)
    isSyncFunction = callable(arg)
    if isAsyncFunction:
        raise Exception(
            "Invalid argument exception. 'catch_errors' does not accept coroutines (i.e., async/await functions). Use 'async_catch_errors' instead."
        )

    fn = None
    wrappingError = None

    if isSyncFunction:
        fn = arg
    elif isinstance(arg, str):
        wrappingError = Exception(arg)
    else:
        raise Exception(
            f'Wrong argument exception. "catch_errors"\'s argument must be a function or a string. Found {type(arg).__name__} instead.'
        )

    def safe_fn_exec(ffn):
        def safe_exec(*args, **named_args):
            fn_name = fn_file = fn_line = None
            try:
                try:
                    fn_name = ffn.__name__
                    fn_file = inspect.getfile(ffn)
                    try:
                        lines = inspect.getsourcelines(ffn)
                        fn_line = lines[1] if lines and len(lines) >= 2 else 0
                    except:
                        fn_line = ""
                except:
                    fn_name = fn_file = fn_line = ""
                data = ffn(*args, **named_args)
                return [None, data]
            except BaseException as error:
                name = _WrappedFunction(fn_name, fn_file, fn_line)
                return [
                    StackedException(name, wrappingError, error)
                    if wrappingError
                    else StackedException(name, error),
                    None,
                ]

        return safe_exec

    return safe_fn_exec(fn) if fn else safe_fn_exec


def async_catch_errors(arg):
    if not arg:
        raise Exception("Missing required argument.")
    isAsyncFunction = inspect.iscoroutinefunction(arg)
    isSyncFunction = callable(arg) and not isAsyncFunction
    if isSyncFunction:
        raise Exception(
            "Invalid argument exception. 'async_catch_errors' does not accept synchronous functions. Use 'catch_errors' instead."
        )

    afn = None
    wrappingError = None

    if isAsyncFunction:
        afn = arg
    elif isinstance(arg, str):
        wrappingError = Exception(arg)
    else:
        raise Exception(
            f'Wrong argument exception. "catch_errors"\'s argument must be a function or a string. Found {type(arg).__name__} instead.'
        )

    def safe_fn_exec(ffn):
        async def async_safe_exec(*args, **named_args):
            fn_name = fn_file = fn_line = None
            try:
                try:
                    fn_name = ffn.__name__
                    fn_file = inspect.getfile(ffn)
                    try:
                        lines = inspect.getsourcelines(ffn)
                        fn_line = lines[1] if lines and len(lines) >= 2 else 0
                    except:
                        fn_line = ""
                except:
                    fn_name = fn_file = fn_line = ""
                data = await ffn(*args, **named_args)
                return [None, data]
            except BaseException as error:
                name = _WrappedFunction(fn_name, fn_file, fn_line)
                return [
                    StackedException(name, wrappingError, error)
                    if wrappingError
                    else StackedException(name, error),
                    None,
                ]

        return async_safe_exec

    return safe_fn_exec(afn) if afn else safe_fn_exec
