import os
import py_compile
from typing import Tuple

FILE_DOES_NOT_EXIST_MSG = "Faili nimega {file_name} ei eksisteeri."
FILE_IS_EMPTY_MSG = "Fail nimega {file_name} on tühi."
FILE_IS_NOT_VALID_PYTHON_MSG = "Fail nimega {file_name} ei ole korrektne Pythoni fail."


class File:
    def __init__(self, file_name: str):
        self.file_name: str = file_name
        self.content: str = None
        self.exists: bool = None
        self.not_empty: bool = None
        self.is_python: bool = None

    def file_exists(self, failed_message: str = FILE_DOES_NOT_EXIST_MSG) -> Tuple[bool, str]:
        """
        Checks if the file exists in the current working directory.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if file found, False if file not found.
        """
        if self.exists is None:
            self.exists = os.path.isfile(self.file_name)

        if not self.exists:
            failed_message = failed_message.format(file_name=self.file_name)

        return self.exists, failed_message

    def file_not_empty(self, failed_message: str = FILE_IS_EMPTY_MSG) -> Tuple[bool, str]:
        """
        Checks if the file is empty or not.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if file NOT empty, False if file is empty.
        """
        if not self.exists:
            return False, failed_message

        if self.not_empty is None:
            self.not_empty = os.stat(self.file_name).st_size > 0

        if not self.not_empty:
            failed_message = failed_message.format(file_name=self.file_name)

        return self.not_empty, failed_message

    def file_is_python(self, failed_message: str = FILE_IS_NOT_VALID_PYTHON_MSG) -> Tuple[bool, str]:
        """
        Checks if file is syntactically valid Python file.
        :param failed_message: The message that will be displayed in case of failing the test.
        :return: True if valid Python file, False if not.
        """
        if not self.exists:
            return False, failed_message

        if self.is_python is None:
            is_valid = True
            try:
                if not self.file_name.endswith(".py"):
                    is_valid = False
                py_compile.compile(self.file_name, doraise=True)
            except (SyntaxError, py_compile.PyCompileError) as e:
                is_valid = False
                failed_message = str(e)
            self.is_python = is_valid

        if not self.is_python:
            failed_message = failed_message.format(file_name=self.file_name)

        return self.is_python, failed_message

    def get_file_text(self) -> str:
        """
        Read in the content of the file.
        :return: str: Content of the file.
        """
        if not self.file_exists()[0]:
            return ""

        if self.content is None:
            with open(self.file_name, encoding='utf-8') as f:
                self.content = f.read()
        return self.content


if __name__ == '__main__':
    f = File("../test/samples/solution.py")
    print(f.file_exists())
    print(f.file_not_empty())
    print(f.file_is_python())
    a = f.get_file_text()
    print(a)
