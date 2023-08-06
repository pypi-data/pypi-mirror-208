import os
import traceback
from typing import Tuple

from tiivad.edutest import run_script, OutOfInputsError, IOCapturing
from tiivad.program import Program
from tiivad.t import format_error


class ProgramExecution:
    def __init__(self, program: Program, user_inputs: list = [], expected_output: str = ""):
        self.program = program
        self.user_inputs: list = user_inputs
        self.globals_dict: dict = None
        self.nr_of_user_inputs: int = None
        self.program_threw_error: bool = None
        self.io_cap: IOCapturing = None
        self.expected_output: str = expected_output
        self.program_exists: bool = None
        self.is_python_file: bool = None  # TODO: Fill me in - samas kohas kus kontrollitakse, et kas fail on tühi.
        self.program_error_message: str = None

    def program_execution_and_input_count(self, re_throw_exception: bool = True, failed_message: str = ""):
        """
        # TODO: What to do with failed_message here?
        :return:
        """
        self.program_threw_error = False
        self.globals_dict = {}
        try:
            if self.user_inputs is None:
                self.user_inputs = []
            if not self.program.file.file_exists()[0]:
                self.program_exists = False  # TODO: Think if we need this variable at all.
                return False, ""
            globs, cap = run_script(self.program.file.file_name, self.user_inputs)
            self.io_cap = cap
            self.globals_dict = globs
        except OutOfInputsError:
            self.nr_of_user_inputs = float('Inf')
            self.program_threw_error = True
            self.program_error_message = "Programm küsib rohkem sisendeid kui oli ette antud."
            return False, self.program_error_message
        except Exception as e:
            self.program_threw_error = True
            if re_throw_exception:
                self.program_error_message = str(traceback.format_exc())
                raise e
            return True, ""
        else:
            self.nr_of_user_inputs = len(self.user_inputs) - len(cap.get_remaining_inputs())
            return True, ""

    def program_input_count_correct(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if the number of user inputs asked by the program is correct.
        :return: True if expected nr of user inputs matches actual count of user inputs, False if not.
        """
        if self.program_threw_error:
            return False, self.program_error_message
        if self.nr_of_user_inputs is None:
            self.program_execution_and_input_count()
        return self.nr_of_user_inputs == len(self.user_inputs), format_error(failed_message, {
            "nr_of_user_inputs": self.nr_of_user_inputs, "user_inputs": self.user_inputs})

    def program_input_count_more_than_expected(self):
        """
        Checks if the number of user inputs asked by the program is more than provided (can be infinite).
        :return: True if actual number of user inputs asked is bigger than expected, False if not.
        """
        if self.program_threw_error:
            return False, self.program_error_message
        if self.nr_of_user_inputs is None:
            self.program_execution_and_input_count()
        return self.nr_of_user_inputs == float('Inf')

    def program_raised_exception(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks whether the program threw an exception or not.
        :return: True if threw, False if not.
        """
        if self.program_threw_error is None:
            self.program_execution_and_input_count()
        return self.program_threw_error, failed_message

    def program_output_correct(self, failed_message: str = "") -> Tuple[bool, str]:
        """
        Checks if the program output is correct.
        :return: True if program output is correct, False if not.
        """
        if self.program_threw_error:
            return False, self.program_error_message
        if not self.io_cap:
            return False, failed_message
        return str(self.expected_output) in self.io_cap.get_stdout(), failed_message

    def program_output_file_correct(self, file_name: str, file_content: str, failed_message: str = "") -> Tuple[
        bool, str]:
        """
        Checks if the output file is correct.
        :return: True if program output file is correct, False if not.
        """
        if self.program_threw_error:
            return False, self.program_error_message
        if os.path.isfile(file_name):
            with open(file_name) as f:
                lines = f.read()
                return str(lines) in file_content, failed_message
        else:
            return False, failed_message


if __name__ == '__main__':
    prog = Program("../test/samples/solution.py")
    user_inputs = [5, 3] * 3
    pe = ProgramExecution(prog, user_inputs)
    pe.program_execution_and_input_count()
    print(pe.nr_of_user_inputs)
    print(pe.program_input_count_correct())
    print(pe.program_input_count_more_than_expected())
    print(pe.program_raised_exception())
    print("IOCap output:")
    print(pe.io_cap.get_stdout())
    print("Last output:")
    print(pe.io_cap.get_last_stdout())
    print(pe.program_output_correct("user input 1"))
