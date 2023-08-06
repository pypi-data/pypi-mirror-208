from typing import Callable, Tuple, List

from tiivad.edutest import IOCapturing, OutOfInputsError
from tiivad.program import Program, ValidationType
from tiivad.program_execution import ProgramExecution


def contains_number(nums, x, allowed_error=0.001):
    for num in nums:
        if abs(num - x) <= allowed_error:
            return True

    return False


class FunctionExecution:
    def __init__(self, function_object: Callable, function_arguments: list, user_inputs: list, expected_result):
        self.execution_result = None
        self.nr_of_user_inputs: int = None
        self.function_executed: bool = False
        self.function_object: Callable = function_object
        self.user_inputs: list = [] if user_inputs is None else user_inputs
        self.function_threw_error: bool = None
        self.function_arguments: list = function_arguments
        self.io_cap: IOCapturing = None
        self.expected_result = expected_result if expected_result is not None else expected_result
        self.function_error_message: str = None

    def function_execution_and_input_count(self, failed_message: str = "", re_throw_exception: bool = True):
        """
        Execute function with the provided arguments and checks if number of user inputs matches expected.
        :param re_throw_exception: Boolean deciding whether to re-throw the error after catching.
        :return: Tuple consisting of execution result, IOCap and the actual number of user inputs.
        """
        self.function_executed = True
        self.function_threw_error = False
        try:
            if self.function_object is None:
                self.function_threw_error = True
                self.function_error_message = "Antud nimega funktsiooni ei ole defineeritud."
                return False, self.function_error_message
            with IOCapturing(self.user_inputs) as cap:
                self.execution_result = self.function_object(*self.function_arguments)
            self.io_cap = cap
        except OutOfInputsError:
            self.nr_of_user_inputs = float('Inf')
            return True, failed_message
        except Exception as e:
            self.function_threw_error = True
            self.function_error_message = e
            if re_throw_exception:
                raise e
            return False, failed_message
        else:
            self.nr_of_user_inputs = len(self.user_inputs) - len(cap.get_remaining_inputs())
            return True, failed_message

    def function_input_count_correct(self) -> bool:
        """
        Checks if the number of user inputs asked by the function is correct.
        :return: True if expected nr of user inputs matches actual count of user inputs, False if not.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return self.nr_of_user_inputs == len(self.user_inputs)

    def function_input_count_more_than_expected(self) -> bool:
        """
        Checks if the number of user inputs asked by the function is more than provided (can be infinite).
        :return: True if actual number of user inputs asked is bigger than expected, False if not.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return self.nr_of_user_inputs == float('Inf')

    def function_modified_param_type_correct(self, actual_solution, example_solution) -> bool:
        """
        # TODO: Rename input parameters.
        Checks if the parameter type is correct after being modified by the function.
        :param actual_solution: TODO:
        :param example_solution: TODO
        :return: True if the type is correct, False if not.
        """
        # * funktsiooni parameetri muudetud väärtuse tüübistruktuur on õige
        # - nt tuleb etteantud parameetrit muuta (nt järjend), aga funktsioon ise ei tagasta midagi
        # - lõppväärtuse juures tuleb kontrollida, et kas muudetud parameeter on õigete tüüpidega
        # - Kas lihtsalt "jooksutan" funktsiooni ja seejärel vaatan muutuja tüüpi?
        if self.function_threw_error:
            return False, self.function_error_message
        if isinstance(actual_solution, (list, tuple)):
            if len(actual_solution) != len(example_solution):
                return False
            for i in range(len(actual_solution)):
                if not self.function_modified_param_type_correct(actual_solution[i], example_solution[i]):
                    return False
            return True
        else:
            return type(actual_solution) == type(example_solution)

    def function_modified_param_value_correct(self, actual_solution, example_solution) -> bool:
        # TODO: Rename input parameters.
        """
        Checks if the parameter value is correct after being modified by the function.
        :param actual_solution: # TODO
        :param example_solution: # TODO
        :return:
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return actual_solution == example_solution

    def function_returned(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if the function got executed and if it actually returned anything.
        :return: True if function executed and returned something, False if function not executed or didn't return.
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return self.function_executed and self.execution_result is not None, failed_message

    def function_return_type_correct(self, expected_value: str, failed_message: str = "") -> Tuple[bool, str]:
        """
        # TODO: See on utils?
        :param expected_value:
        :return:
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return type(self.execution_result) == eval(expected_value), failed_message

    def function_return_value_correct(self, failed_message: str = "Funktsiooni eeldatav väljund pidi olema "
                                                                  "{expected_value}, kuid tulemus oli {output}") \
            -> Tuple[bool, str]:
        """

        :param failed_message:
        :return:
        """
        if self.function_threw_error:
            return False, self.function_error_message
        return self.execution_result == self.expected_result, failed_message.format(
            expected_value=str(self.expected_result), output=str(self.execution_result))

    def function_raised_exception(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks whether the function threw an exception or not.
        :return: True if threw, False if not.
        """
        return self.function_threw_error, failed_message

    @staticmethod
    def function_output_contains_keyword(function_output_str: str, keyword: str, failed_message: str = "") \
            -> Tuple[bool, str]:
        """

        :param function_output_str:
        :param keyword:
        :param failed_message:
        :return:
        """
        if keyword in function_output_str:
            return True, ""
        else:
            return False, failed_message

    def function_output_correct2(self, validation_type: str, outputs: List[str], nothing_else: bool, actual_output: str,
                                 failed_message: str = "") -> Tuple[bool, str]:
        """

        :param actual_output:
        :param validation_type:
        :param outputs:
        :param nothing_else:
        :param failed_message:
        :return:
        """
        if self.function_threw_error:
            return False, self.function_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for func in outputs:
                if not self.function_output_contains_keyword(actual_output, func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for func in outputs:
                if self.function_output_contains_keyword(actual_output, func, failed_message)[0]:
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for func in outputs:
                if self.function_output_contains_keyword(actual_output, func, failed_message)[0]:
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for func in outputs:
                if not self.function_output_contains_keyword(actual_output, func, failed_message)[0]:
                    return True, failed_message
            return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_function_test: {validation_type}")

        return True, ""

    def function_output_numbers_correct2(self, validation_type: str, outputs: List[str], nothing_else: bool,
                                         actual_output: str, failed_message: str = "") -> Tuple[bool, str]:
        """

        :param actual_output:
        :param validation_type:
        :param outputs:
        :param nothing_else:
        :param failed_message:
        :param is_numeric
        :return:
        """
        if self.function_threw_error:
            return False, self.function_error_message

        if validation_type == ValidationType.ALL_OF_THESE.name:
            for func in outputs:
                if not contains_number(actual_output, func):
                    return False, failed_message

        elif validation_type == ValidationType.ANY_OF_THESE.name:
            for func in outputs:
                if contains_number(actual_output, func):
                    return True, ""
            return False, failed_message

        elif validation_type == ValidationType.NONE_OF_THESE.name:
            for func in outputs:
                if contains_number(actual_output, func):
                    return False, failed_message

        elif validation_type == ValidationType.MISSING_AT_LEAST_ONE_OF_THESE.name:
            for func in outputs:
                if not contains_number(actual_output, func):
                    return True, failed_message
            return False, failed_message

        else:
            raise NotImplementedError(
                f"The following type is not implemented for the program_calls_function_test: {validation_type}")

        return True, ""


if __name__ == '__main__':
    prog = Program("../test/samples/solution.py")
    user_inputs_prog = [5, 3] * 3
    p = ProgramExecution(prog, user_inputs_prog)
    f_name = "test"
    p.program_execution_and_input_count()
    f_obj = p.globals_dict[f_name]
    user_inputs_fun = [5, 3] * 2
    fe = FunctionExecution(f_obj, [1], user_inputs_fun)
    execution_result, nr_of_user_inputs = fe.function_execution_and_input_count()
    print(fe.function_returned())
    print(fe.function_input_count_correct())
    print(fe.function_input_count_more_than_expected())
    print(fe.function_return_type_correct(int))
    print(fe.function_return_value_correct(2))
    print(fe.function_raised_exception())
    print("IOCap output:")
    print(fe.io_cap.get_stdout())
