import traceback
from math import ceil, floor
from re import findall
from typing import Any, List

from tiivad.file import File
from tiivad.results import Results
from tiivad.tests import program_imports_module_test, program_calls_function_test, program_contains_keyword_test, \
    program_contains_try_except_test, program_calls_print_test, program_contains_loop_test, program_execution_test, \
    function_execution_test, function_contains_loop_test, function_contains_keyword_test, function_contains_return_test, \
    function_calls_function_test, function_is_recursive_test, function_defines_function_test, \
    function_imports_module_test, function_contains_try_except_test, function_is_pure_test, \
    function_calls_print_test, class_imports_module_test, class_defines_function_test, class_calls_class_test, \
    class_function_calls_function_test, program_defines_class_test, program_defines_subclass_test, \
    program_calls_class_test, program_calls_class_function_test, class_instance_test


def validate_files(files: List[str]) -> bool:
    for file in files:
        f = File(file)

        f_exists, error_msg = f.file_exists()
        if not f_exists:
            Results.pre_evaluate_error = error_msg
            return False

        f_not_empty, error_msg = f.file_not_empty()
        if not f_not_empty:
            Results.pre_evaluate_error = error_msg
            return False

        f_is_python, error_msg = f.file_is_python()
        if not f_is_python:
            Results.pre_evaluate_error = error_msg
            return False

    return True


def execute_test(**kwargs):
    if Results.pre_evaluate_error:
        # print(Results(None).format_result())
        return

    # test = create_and_validate(**kwargs)

    try:
        if kwargs["type"] == "program_imports_module_test":
            Results(program_imports_module_test(**kwargs))
        elif kwargs["type"] == "program_calls_function_test":
            Results(program_calls_function_test(**kwargs))
        elif kwargs["type"] == "program_defines_function_test":
            Results(program_calls_function_test(**kwargs))
        elif kwargs["type"] == "program_contains_keyword_test":
            Results(program_contains_keyword_test(**kwargs))
        elif kwargs["type"] == "program_contains_try_except_test":
            Results(program_contains_try_except_test(**kwargs))
        elif kwargs["type"] == "program_calls_print_test":
            Results(program_calls_print_test(**kwargs))
        elif kwargs["type"] == "program_contains_loop_test":
            Results(program_contains_loop_test(**kwargs))
        elif kwargs["type"] == "program_execution_test":
            Results(program_execution_test(**kwargs))
        elif kwargs["type"] == "function_execution_test":
            Results(function_execution_test(**kwargs))
        elif kwargs["type"] == "function_contains_loop_test":
            Results(function_contains_loop_test(**kwargs))
        elif kwargs["type"] == "function_contains_keyword_test":
            Results(function_contains_keyword_test(**kwargs))
        elif kwargs["type"] == "function_contains_return_test":
            Results(function_contains_return_test(**kwargs))
        elif kwargs["type"] == "function_calls_function_test":
            Results(function_calls_function_test(**kwargs))
        elif kwargs["type"] == "function_is_recursive_test":
            Results(function_is_recursive_test(**kwargs))
        elif kwargs["type"] == "function_defines_function_test":
            Results(function_defines_function_test(**kwargs))
        elif kwargs["type"] == "function_imports_module_test":
            Results(function_imports_module_test(**kwargs))
        elif kwargs["type"] == "function_imports_module_test":
            Results(function_imports_module_test(**kwargs))
        elif kwargs["type"] == "function_contains_try_except_test":
            Results(function_contains_try_except_test(**kwargs))
        elif kwargs["type"] == "function_is_pure_test":
            Results(function_is_pure_test(**kwargs))
        elif kwargs["type"] == "function_calls_print_test":
            Results(function_calls_print_test(**kwargs))
        elif kwargs["type"] == "class_imports_module_test":
            Results(class_imports_module_test(**kwargs))
        elif kwargs["type"] == "class_defines_function_test":
            Results(class_defines_function_test(**kwargs))
        elif kwargs["type"] == "class_calls_class_test":
            Results(class_calls_class_test(**kwargs))
        elif kwargs["type"] == "class_function_calls_function_test":
            Results(class_function_calls_function_test(**kwargs))
        elif kwargs["type"] == "program_defines_class_test":
            Results(program_defines_class_test(**kwargs))
        elif kwargs["type"] == "program_defines_subclass_test":
            Results(program_defines_subclass_test(**kwargs))
        elif kwargs["type"] == "program_calls_class_test":
            Results(program_calls_class_test(**kwargs))
        elif kwargs["type"] == "program_calls_class_function_test":
            Results(program_calls_class_function_test(**kwargs))
        elif kwargs["type"] == "class_instance_test":
            Results(class_instance_test(**kwargs))
        else:
            raise NotImplementedError("The following type of test is not implemented: " + str(kwargs["type"]))

    except Exception:
        Results.error = str(traceback.format_exc())


def execute_test_old(func, points, before_message, failed_message: str, passed_message, test_name, user_inputs, *args):
    if failed_message is None:
        failed_message = ""
    result = {}
    try:
        test_result, failed_message = func(*args, failed_message=failed_message)
    except Exception as e:  # TODO: Refactor me, too much duplication
        result['test_name_code'] = func.__name__
        result['points'] = 0.0
        result['exception_message'] = str(traceback.format_exc())
        result['before_message'] = before_message
        result['failed_message'] = str(e)
        result['passed_message'] = passed_message
        result['test_name'] = test_name
        result['user_inputs'] = user_inputs
        result['test_status'] = "Exception"
    else:
        if test_result:
            result['test_name_code'] = func.__name__
            result['points'] = points
            result['before_message'] = before_message
            result['failed_message'] = failed_message
            result['passed_message'] = passed_message
            result['test_name'] = test_name
            result['user_inputs'] = user_inputs
            result['test_status'] = "TestPass"
        else:
            result['test_name_code'] = func.__name__
            result['points'] = 0.0
            result['before_message'] = before_message
            result['failed_message'] = failed_message
            result['passed_message'] = passed_message
            result['test_name'] = test_name
            result['user_inputs'] = user_inputs
            result['test_status'] = "TestFail"
    Results(result)
    # print(result)
    return result


def create_input_file(file_name: str, file_content: str):
    f = open(file_name, "w", encoding="utf-8")
    f.write(file_content)
    f.close()


def get_file_text(file_name: str) -> str:
    with open(file_name, encoding='utf-8') as f:
        return f.read()


def value_not_empty(value: Any) -> bool:
    if value is None:
        return False
    if type(value) == str and value.strip() == "":
        return False
    return True


def string_not_empty(string: str) -> bool:
    return string is not None and string.strip() != ""


def unified_value_correct(value: Any, expected_value: Any, value_type: str = 'str') -> bool:
    # TODO lisa mõned testid
    # TODO: See on utils?
    """
    # * mida tagastatud väärtusele rakendatakse
    # * enne kui väärtuse õigsust kontrollitakse
    # - probleemid siis, kui programm tagastab ujukomaarve, seetõttu võiks vastust kontrollida hoopis vahemikku sobivusega
    # - funktsioon tagastab sõne, aga pole tegelikult oluline, et kas tegemist on suur- või väiketähtedega
    # - ehk me rakendame tudengi kirjutatud funktsiooni poolt tagastatud väärtusele mingi funktsiooni (nt .lower()) ja alles siis võrdleme etteantud tulemusega
    :param expected_value:
    :param result_value:
    :return:
    """
    if value_type == 'str':
        return value.strip().lower() == expected_value
    elif value_type == 'number':
        return floor(float(expected_value)) <= value <= ceil(float(expected_value))
    # TODO: Kas veel mõni tüüp?


def list_contains_items_ordered(lst: list, items: list) -> bool:
    """
    Abifunktsioon järgnevate jaoks
    """
    j = 0
    for item in items:
        while j < len(lst) and lst[j] != item:
            j += 1
        if j == len(lst):
            return False
        else:
            j += 1
    return True


# -- Numbers

def list_of_numbers(string: str) -> list[float]:
    if string is None:
        return []
    exp = r"([-]?[0-9]+(?:[.][0-9]+)?)"
    return list(map(float, findall(exp, string)))


def number_of_numbers(string: str) -> int:
    return len(list_of_numbers(string))


def number_of_numbers_exactly(string: str, n: int) -> bool:
    return number_of_numbers(string) == n


def number_of_numbers_at_least(string: str, n: int) -> bool:
    return number_of_numbers(string) >= n


def number_of_numbers_at_most(string: str, n: int) -> bool:
    return number_of_numbers(string) <= n


def string_contains_any_number(string: str) -> bool:
    return number_of_numbers_at_least(string, 1)


def string_contains_number(string: str, item: float) -> bool:
    return item in list_of_numbers(string)


def string_contains_numbers(string: str, items: list[float]) -> bool:
    sorted_numbers = sorted(list_of_numbers(string))
    sorted_items = sorted(items)
    return list_contains_items_ordered(sorted_numbers, sorted_items)


def string_contains_numbers_ordered(string: str, items: list[float]) -> bool:
    numbers = list_of_numbers(string)
    return list_contains_items_ordered(numbers, items)


def string_contains_only_these_numbers(string: str, items: list[float]) -> bool:
    sorted_numbers = sorted(list_of_numbers(string))
    sorted_items = sorted(items)
    return list_contains_items_ordered(sorted_numbers, sorted_items) and \
           len(sorted_numbers) == len(sorted_items)


def string_contains_only_these_numbers_ordered(string: str, items: list[float]) -> bool:
    numbers = list_of_numbers(string)
    return list_contains_items_ordered(numbers, items) and len(numbers) == len(items)


# -- Strings

def list_of_strings(string: str) -> list[str]:
    if string is None:
        return []
    s = string.replace(".", " ").replace(",", " ").replace(":", " ").replace(";", " ")
    s = s.replace("?", " ").replace("!", " ").replace('"', " ")
    return s.split()


def number_of_strings(string: str) -> int:
    return len(list_of_strings(string))


def number_of_strings_exactly(string: str, n: int) -> bool:
    return number_of_strings(string) == n


def number_of_strings_at_least(string: str, n: int) -> bool:
    return number_of_strings(string) >= n


def number_of_strings_at_most(string: str, n: int) -> bool:
    return number_of_strings(string) <= n


def string_contains_any_string(string: str) -> bool:
    return number_of_strings_at_least(string, 1)


def string_equals_string(string: str, item: str) -> bool:
    return string is not None and item == string


def string_contains_string(string: str, item: str) -> bool:
    return string is not None and item in string


def string_contains_strings(string: str, items: list[float]) -> bool:
    sorted_strings = sorted(list_of_strings(string))
    sorted_items = sorted(items)
    return list_contains_items_ordered(sorted_strings, sorted_items)


def string_contains_strings_ordered(string: str, items: list[float]) -> bool:
    strings = list_of_strings(string)
    return list_contains_items_ordered(strings, items)


def string_contains_only_these_strings(string: str, items: list[float]) -> bool:
    sorted_strings = sorted(list_of_strings(string))
    sorted_items = sorted(items)
    return list_contains_items_ordered(sorted_strings, sorted_items) and \
           len(sorted_strings) == len(sorted_items)


def string_contains_only_these_strings_ordered(string: str, items: list[float]) -> bool:
    strings = list_of_strings(string)
    return list_contains_items_ordered(strings, items) and len(strings) == len(items)


# -- Lines

def list_of_lines(string: str):
    if string is None:
        return []
    lines = []
    for s in string.strip().split("\n"):
        if s.strip() != "":
            lines.append(s)
    return lines


def number_of_lines(string: str) -> int:
    return len(list_of_lines(string))


def number_of_lines_exactly(string: str, n: int) -> bool:
    return number_of_lines(string) == n


def number_of_lines_at_least(string: str, n: int) -> bool:
    return number_of_lines(string) >= n


def number_of_lines_at_most(string: str, n: int) -> bool:
    return number_of_lines(string) <= n


def string_line_contains_string(string: str, line_nr: int, item: str) -> bool:
    lines = list_of_lines(string)
    if 1 <= line_nr <= len(lines):
        if item in lines[line_nr - 1]:
            return True
    return False


def string_line_equals(string: str, line_nr: int, item: str) -> bool:
    lines = list_of_lines(string)
    if 1 <= line_nr <= len(lines):
        if item == lines[line_nr - 1]:
            return True
    return False


def string_contains_lines(string: str, items: list[float]) -> bool:
    sorted_lines = sorted(list_of_lines(string))
    sorted_items = sorted(items)
    return list_contains_items_ordered(sorted_lines, sorted_items)


def string_contains_lines_ordered(string: str, items: list[float]) -> bool:
    lines = list_of_lines(string)
    return list_contains_items_ordered(lines, items)


def string_contains_only_these_lines(string: str, items: list[float]) -> bool:
    sorted_lines = sorted(list_of_lines(string))
    sorted_items = sorted(items)
    return list_contains_items_ordered(sorted_lines, sorted_items) and \
           len(sorted_lines) == len(sorted_items)


def string_contains_only_these_lines_ordered(string: str, items: list[float]) -> bool:
    lines = list_of_lines(string)
    return list_contains_items_ordered(lines, items) and len(lines) == len(items)
