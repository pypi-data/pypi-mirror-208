import re
import ast
import sys
import runpy
import types
import locale
import inspect
import traceback
import importlib
import os.path
from copy import deepcopy

OUT_OF_INPUTS = "Program asked for input but no more input was available"
INPUT_NOT_ALLOWED = "Reading input is not allowed"
OUTPUT_NOT_ALLOWED = "Writing output is not allowed"
CANT_FIND_FUNCTION = "Can't find function {name}"
CANT_FIND_FILE = "Can't find file {path}"
CANT_IMPORT_MODULE_WITH_INPUT = "Can't import {file} as module, because it tried to read input"
FUNCTION_MODIFIED_ARGUMENTS = "Your function modified its argument objects"
FUNCTION_MODIFIED_GLOBALS = "Your function modified global variables or objects"
FUNCTION_PRINTED_INSTEAD_OF_RETURNING = "Function printed correct response but should have returned it"
FUNCTION_RETURNED_WRONG_TYPE = "Function returned a value of type {actual}, but should have returned a value of type {expected}"
FUNCTION_RETURNED_WRONG_VALUE = "Function returned {actual}, but should have returned {expected}"
FUNCTION_READ_STDIN = "Function tried to read input"
FUNCTION_WROTE_STDOUT = "Function printed something but this was not allowed"
FUNCTION_WROTE_STDERR = "Function wrote to error stream but this was not allowed"
CANT_FIND_TARGET = "Can't find the script to test"

ALLOW_DECIMAL_COMMA = False

_target = None
_test_file_prefixes = ["test_"]
_test_file_suffixes = ["_test", "_tests", "_tester"]
TARGET_SCRIPT_ENV_KEY = "TESTABLE_SCRIPT"


def set_target(path):
    """Fixes a file name to be used when checking functions are called without file name argument."""
    global _target
    _target = path


def find_target():
    """If testable script path has been fixed with :func:`set_target` then
    returns this file.

    Otherwise, if there is environment variable TARGET_SCRIPT_ENV_KEY set, then its
    value is returned.

    Otherwise the inference algorithm tries to detect current test file and the testable script
    with matching name. It succeeds if testable script and test file are both in
    current directory and test file name is formed by appending word ``_test``, ``_tests``
    or ``_tester`` to script name, or prepending ``test_`` to script name.

    Example: "exercise1.py" is  found if test file is one of

    * exercise1_test.py
    * exercise1_tests.py
    * exercise1_tester.py
    * test_exercise1.py

    """
    if _target is not None:
        return _target
    else:
        if (TARGET_SCRIPT_ENV_KEY in os.environ
                and os.path.exists(os.environ[TARGET_SCRIPT_ENV_KEY])):
            return os.environ[TARGET_SCRIPT_ENV_KEY]

        # Now try name matching.
        # Go up in stack, check frames with source files in current folder
        # and try to match their names with potential script names
        for frame in inspect.stack():
            path = frame[1]
            # if the file is in current folder
            if (os.path.exists(path)
                    and os.path.samefile(os.path.dirname(path), os.getcwd())
                    and path.endswith(".py")):
                tester_name = os.path.basename(path)[:-3]

                # see if there is a file without test prefix
                for prefix in _test_file_prefixes:
                    if tester_name.startswith(prefix):
                        target_name = tester_name[len(prefix):]
                        if os.path.exists(target_name + ".py"):
                            return os.path.join(os.getcwd(), target_name + ".py")

                # see if there is a file without test suffix
                for suffix in _test_file_suffixes:
                    if tester_name.endswith(suffix):
                        target_name = tester_name[:-len(suffix)]
                        if os.path.exists(target_name + ".py"):
                            return os.path.join(os.getcwd(), target_name + ".py")

        raise AssertionError(CANT_FIND_TARGET)


def _looks_like_test_file(path):
    name = os.path.basename(path)
    if not name.endswith(".py"):
        return False

    name = name[:-3]

    for prefix in _test_file_prefixes:
        if name.startswith(prefix):
            return True

    for suffix in _test_file_suffixes:
        if name.endswith(suffix):
            return True

    return False


def get_function(name, scope=None):
    """Tries to locate given function ..."""
    assert isinstance(name, str)

    if scope is None:
        if "." in name:
            scope, name = name.rsplit(".", maxsplit=1)
        else:
            scope = find_target()

    if isinstance(scope, str):
        scope = import_module(scope)

    if isinstance(scope, types.ModuleType):
        scope = vars(scope)

    assert isinstance(scope, dict)
    assert name in scope, CANT_FIND_FUNCTION.format(name=name)
    return scope[name]


def import_module(name, package=None):
    """Works like :func:`importlib.import_module` but raises :exc:ForbiddenInputError
    instead of blocking when module tries to read from stdin.
    """
    try:
        with ForbiddenInput():
            return importlib.import_module(name, package)
    except ForbiddenInputError:
        raise ImportError(CANT_IMPORT_MODULE_WITH_INPUT)


def check_function(function, arguments, expected_result, keyword_arguments={},
                   inputs=[],
                   allow_remaining_inputs=False,
                   expected_stdout=None,
                   expected_stderr="",
                   may_modify_globals=True,
                   may_modify_arguments=True):
    if isinstance(function, str):
        function = get_function(function)

    # prepare the call
    if not may_modify_globals:
        original_globals = deepcopy(vars(inspect.getmodule(function)))

    if not may_modify_arguments:
        # TODO: repr
        original_arguments = deepcopy(arguments)
        original_keyword_arguments = deepcopy(keyword_arguments)

    # make the call
    with IOCapturing(inputs) as iocap:
        try:
            actual_result = function(*arguments, **keyword_arguments)
        except OutOfInputsError:
            if inputs in ["", [], ()]:
                raise ForbiddenInputError(FUNCTION_READ_STDIN)
            else:
                raise

    stdout = iocap.get_stdout()
    stderr = iocap.get_stderr()

    # check result
    if actual_result != expected_result:

        # Maybe student used print instead of return?
        if (actual_result == None
                and str(expected_result).trim() == stdout.trim()):
            raise AssertionError(FUNCTION_PRINTED_INSTEAD_OF_RETURNING)

        if type(actual_result) != type(expected_result):
            raise AssertionError(FUNCTION_RETURNED_WRONG_TYPE.format(
                expected=type(expected_result).__name__,
                actual=type(actual_result).__name__))

        raise AssertionError(FUNCTION_RETURNED_WRONG_VALUE.format(
            expected=expected_result,
            actual=actual_result))

    if expected_stdout == "" and stdout != "":
        raise AssertionError(FUNCTION_WROTE_STDOUT)

    if expected_stderr == "" and stderr != "":
        raise AssertionError(FUNCTION_WROTE_STDERR)

    check_std_streams(iocap, expected_stdout, expected_stderr, allow_remaining_inputs)

    # check other conditions
    if (not may_modify_arguments
            and (original_arguments != arguments
                 or original_keyword_arguments != keyword_arguments)):
        raise AssertionError(FUNCTION_MODIFIED_ARGUMENTS)

    if not may_modify_globals and original_globals != vars(inspect.getmodule(function)):
        raise AssertionError(FUNCTION_MODIFIED_GLOBALS)


def check_pure_function(function, arguments, expected_result, keyword_arguments={}):
    """Shortcut for :func:`check_function` disallowing IO
    and modifications to globals and arguments. Note that it doesn't actually
    guarantee that function is indeed pure, it only checks for common reasons
    why it can't be pure."""
    return check_function(function, arguments, expected_result, keyword_arguments,
                          inputs=[], expected_output="",
                          may_modify_globals=False,
                          may_modify_arguments=False)


def check_script(script_path=None, inputs=[], arguments=[],
                 provided_files={},
                 text_file_encoding="UTF-8",
                 text_file_universal_newlines=True,
                 allow_remaining_inputs=False,
                 expected_stdout=None,
                 expected_last_stdout=None,
                 expected_stderr="",
                 expected_files={}
                 ):
    try:
        globs, iocap = run_script(script_path, inputs, arguments,
                                  provided_files, text_file_encoding)
        check_std_streams(iocap, expected_stdout, expected_stderr, allow_remaining_inputs)

        for path in expected_files:
            check_file_contains(path, expected_files[path],
                                text_file_encoding, text_file_universal_newlines)

        return globs

    finally:
        # remove temp files
        for path in provided_files.keys().union(expected_files.keys()):
            if os.path.exists(path):
                os.remove(path)


def check_file_contains(path, expected_content, text_file_encoding="UTF-8",
                        universal_newlines=True):
    assert os.path.exists(path), CANT_FIND_FILE.format(path=path)

    if isinstance(expected_content, str):
        expected_content = expected_content
        with open(path, encoding=text_file_encoding) as fp:
            actual_content = fp.read()

        if universal_newlines:
            expected_content = expected_content.replace("\r\n", "\n")
            actual_content = actual_content.replace("\r\n", "\n")

        if actual_content != expected_content:
            raise AssertionError("TODO: file content doesn't match")

    elif isinstance(expected_content, bytes):
        with open(path, mode="b") as fp:
            actual_content = fp.read()

        if actual_content != expected_content:
            raise AssertionError("TODO: file content doesn't match")

    elif expected_content is None:
        pass
    else:
        raise TypeError("Unsupported expected_content")


def check_std_streams(iocap, expected_stdout, expected_stderr, allow_remaining_inputs=False):
    "TODO:"


def check_code(obj,
               disallow_keywords=[],
               disallow_names=[]):
    pass


def run_script(script_path=None, inputs=[], arguments=[],
               provided_files={}, text_file_encoding="UTF-8"):
    """
    Returns pair with global variables and :class:IOCapturing object
    """
    if script_path is None:
        script_path = find_target()

    # preparations
    for path in provided_files:
        create_file(path, provided_files[path], text_file_encoding)

    original_argv = sys.argv
    sys.argv = [script_path] + arguments

    with IOCapturing(inputs) as iocap:
        try:
            # Execute code located at the specified filesystem location
            # Returns the resulting top level namespace dictionary
            globs = runpy.run_path(script_path, run_name="__main__")
        finally:
            sys.argv = original_argv

    return globs, iocap


def generate_function_test(function, arguments, expected_result):
    fun = get_function(function)

    title_text = fun.__name__ + "(" + ", ".join(map(repr, arguments)) + ")"

    @title(title_text)
    def test():
        check_function(fun, arguments, expected_result)

    # Assuming the caller of generate_function_test is in test module.
    # Attach test to this module.
    caller_frame = inspect.currentframe().f_back
    test_module = inspect.getmodule(caller_frame)
    setattr(test_module, title_text, test)


class Plan:
    """Context manager which adds plan description to exception messages"""

    def __init__(self, description):
        self._description = description

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            # TODO: show part of stacktrace
            # TODO: detect errors in the test
            if exc_type is AssertionError:
                msg = str(exc_value)
            else:
                msg = str(exc_type.__name__) + ": " + str(exc_value)

            raise AssertionError(self._description + "\n\n" + msg)


class ForbiddenIO():
    """Context manager which causes access to given standard streams
    to raise :exc:`ForbiddenOutputError` or :exc:`ForbiddenInputError`


    Example ::

        with ForbiddenIO({"stdin", "stderr"}):
            print("Blah 2")                         # OK, stdout is not forbidden
            something = input("input something: ")  # raises ForbiddenInputError

    """

    def __init__(self, forbidden_streams={"stdin", "stdout", "stderr"}):
        self._forbidden_streams = forbidden_streams
        self._original_streams = {}

    def __enter__(self):
        for name in self._forbidden_streams:
            self._original_streams[name] = getattr(sys, name)
            setattr(sys, name, _ForbiddenStream())

    def __exit__(self, exc_type, exc_value, traceback):
        for name in self._forbidden_streams:
            setattr(sys, name, self._original_streams[name])


class ForbiddenInput(ForbiddenIO):
    def __init__(self):
        ForbiddenIO.__init__(self, {"stdin"})


class IOCapturing:
    def __init__(self, inputs=[]):
        self._inputs = inputs

    def __enter__(self):
        self._inputs_iterator = self._create_inputs_iterator(self._inputs)
        self._stream_events = []
        self._original_streams = {}
        self._remaining_inputs = []

        # Remember original streams
        for stream_name in {"stdout", "stderr", "stdin"}:
            self._original_streams[stream_name] = getattr(sys, stream_name)

        # Install fake streams
        sys.stdout = _OutputListenerStream(self._record_stdout_data)
        sys.stderr = _OutputListenerStream(self._record_stderr_data)
        sys.stdin = _InputListenerStream(self._record_stdin_data, self._inputs_iterator)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._remaining_inputs = sys.stdin.fetch_remaining_inputs()

        # restore original streams
        for stream_name in {"stdout", "stderr", "stdin"}:
            setattr(sys, stream_name, self._original_streams[stream_name])

    def get_remaining_inputs(self):
        return self._remaining_inputs

    def get_io(self):
        return self._get_stream_data({"stdout", "stderr", "stdin"}, False)

    def get_stdout(self):
        return self._get_stream_data({"stdout"}, False)

    def get_last_stdout(self):
        return self._get_stream_data({"stdout"}, True)

    def get_stderr(self):
        return self._get_stream_data({"stderr"}, False)

    def debug(self, *args, sep=' ', end='\n', stream_name="stdout", flush=False):
        """Meant for printing debug information from input generator."""
        print(*args, sep=sep, end=end,
              file=self._original_streams[stream_name], flush=flush)

    def _record_stdout_data(self, data):
        self._stream_events.append(("stdout", data))

    def _record_stderr_data(self, data):
        self._stream_events.append(("stderr", data))

    def _record_stdin_data(self, data):
        self._stream_events.append(("stdin", data))

    def _get_stream_data(self, stream_names, only_since_last_input):
        result = ""
        i = len(self._stream_events) - 1
        while i >= 0:
            event_stream_name, event_data = self._stream_events[i]

            if only_since_last_input and event_stream_name == "stdin":
                break

            if event_stream_name in stream_names:
                result = event_data + result

            i -= 1

        return result

    def _create_inputs_iterator(self, inputs):
        if isinstance(inputs, str):
            return iter(inputs.splitlines())

        try:
            return iter(inputs)
        except TypeError:
            try:
                result = inputs(self)
                assert isinstance(result, types.GeneratorType)
                return result

            except BaseException as e:
                e.message = "Could not create iterator for inputs.\n" + e.message
                raise


class _ListenerStream:
    def __init__(self, data_listener):
        self._data_listener = data_listener


class _OutputListenerStream(_ListenerStream):
    def __init__(self, data_listener):
        _ListenerStream.__init__(self, data_listener)

    def write(self, data):
        self._data_listener(data)

    def writelines(self, lines):
        self._data_listener(lines)


class _InputListenerStream(_ListenerStream):

    def __init__(self, data_listener, inputs_iterator):
        _ListenerStream.__init__(self, data_listener)
        self._inputs_iterator = inputs_iterator

    def fetch_remaining_inputs(self):
        result = []
        while True:
            try:
                result.append(next(self._inputs_iterator))
            except StopIteration:
                break

        return result

    def read(self, limit=-1):
        raise NotImplementedError("Method 'read' on stdin is not supported in testable programs")

    def readline(self, limit=-1):
        if limit > 0:
            raise NotImplementedError("Positive limit/size for stdin.readline is not supported in testable programs")

        try:
            data = str(next(self._inputs_iterator)) + "\n"
            self._data_listener(data)
            return data
        except StopIteration:
            raise OutOfInputsError(OUT_OF_INPUTS)

    def readlines(self, limit=-1):
        raise NotImplementedError("Method 'readlines' on stdin is not supported in testable programs")


class ForbiddenStreamError(AssertionError):
    pass


class OutOfInputsError(RuntimeError):
    pass


class ForbiddenInputError(ForbiddenStreamError):
    pass


class ForbiddenOutputError(ForbiddenStreamError):
    pass


class _ForbiddenStream:
    def write(self, data):
        raise ForbiddenOutputError(OUTPUT_NOT_ALLOWED)

    def writelines(self, lines):
        raise ForbiddenOutputError(OUTPUT_NOT_ALLOWED)

    def read(self, limit=-1):
        raise ForbiddenInputError(INPUT_NOT_ALLOWED)

    def readline(self, limit=-1):
        raise ForbiddenInputError(INPUT_NOT_ALLOWED)

    def readlines(self, limit=-1):
        raise ForbiddenInputError(INPUT_NOT_ALLOWED)


def load_locale(locale):
    """Example: if argument is "et", then all global variables defined
    in edutest_locale_et.py are copied to edutest, overriding existing values"""
    try:
        this_module = sys.modules[__name__]
        that_module = importlib.import_module("edutest_locale_" + locale)

        for name in vars(that_module):
            if not name.startswith("_"):
                setattr(this_module, name, getattr(that_module, name))
    except:
        pass


def title(title_text):
    """Creates decorator for setting test title. Works only for Nose.
    Usage example:

    @title("First test with x=3 and y=4")
    def test1():
        assert fun(x=3, y=4) == 7

    """

    def decorator(f):
        f.__name__ = title_text
        f.__test__ = True
        return f

    return decorator


def get_source(path):
    import tokenize
    # encoding-safe open
    with tokenize.open(path) as sourceFile:
        contents = sourceFile.read()
    return contents


def is_function(value):
    try:
        return hasattr(value, '__call__')
    except:
        return False


def get_error_message(exception=None):
    if exception:
        type_ = type(exception)
        msg = str(exception)
    else:
        type_, msg, _ = sys.exc_info()

    return "{}: {}".format(type_.__name__, msg)


def get_traceback(exception):
    type_, value, tb = type(exception), exception, exception.__traceback__
    return "".join(traceback.format_exception(type_, value, tb))


def quote_text_block(text):
    return ("\n>" + text.replace("\n", "\n>")
            + ("" if text.endswith("\n") else "\n"))


def extract_numbers(s, allow_decimal_comma=False):
    result = []

    if allow_decimal_comma:
        rexp = """((?:\+|\-)?\d+(?:(?:\.|,)\d+)?)"""
    else:
        rexp = """((?:\+|\-)?\d+(?:\.\d+)?)"""

    for item in re.findall(rexp, s):
        try:
            result.append(int(item))
        except:
            try:
                result.append(float(item.replace(",", ".")))
            except:
                pass
    return result


def contains_number(num_list_or_str, x, allowed_error=0, allow_decimal_comma=False):
    if isinstance(num_list_or_str, str):
        nums = extract_numbers(num_list_or_str, allow_decimal_comma)
    else:
        nums = num_list_or_str

    for num in nums:
        if abs(num - x) <= allowed_error:
            return True

    return False


def ast_contains_name(node, name):
    if isinstance(node, ast.Name) and node.id == name:
        return True

    for child in ast.iter_child_nodes(node):
        if ast_contains_name(child, name):
            return True

    return False


def ast_contains(node, node_type):
    if isinstance(node, node_type):
        return True

    for child in ast.iter_child_nodes(node):
        if ast_contains(child, node_type):
            return True

    return False


def create_file(path, content, text_file_encoding=None):
    if text_file_encoding is None:
        text_file_encoding = locale.getpreferredencoding(False)

    if isinstance(content, str):
        content = content.encode(text_file_encoding)

    with open(path, mode="wb") as fp:
        fp.write(content)


def delete_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


def check_file_exists(name):
    assert os.path.isfile(name), "Ei leia faili nimega %s" % name  # TODO: translate


def _hide_from_nose():
    # hide all functions from nose (there are several with "test" in name)
    for name in vars(sys.modules[__name__]).copy():
        if "test" in name.lower():
            try:
                setattr(getattr(sys.modules[__name__], name), "__test__", False)
            except:
                pass


def _load_preferred_locale():
    def get_language_code_from_locale_string(s):
        return s.split(".")[0].split("_")[0]

    if "VPL_LANG" in os.environ:  # locale set by VPL server (http://vpl.dis.ulpgc.es/)
        load_locale(get_language_code_from_locale_string(os.environ["VPL_LANG"]))
    else:
        try:
            load_locale(get_language_code_from_locale_string(locale.getdefaultlocale()[0]))
        except Exception as e:
            print(e)
            return


def description(desc):
    """Can be used for changing test function name"""

    def decorator(f):
        f.__name__ = desc
        return f

    return decorator


_load_preferred_locale()
_hide_from_nose()
