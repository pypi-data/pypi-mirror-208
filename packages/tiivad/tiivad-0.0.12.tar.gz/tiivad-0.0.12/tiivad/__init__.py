# from tiivad.file import File
# from tiivad.function import Function
# from tiivad.function_execution import FunctionExecution
# from tiivad.program_execution import ProgramExecution
# from tiivad.utils import create_input_file, execute_test, validate_files
import json

from tiivad.help_structures import GenericChecks, OutputFileChecks
from tiivad.results import Results
from tiivad.version import __version__
#
# __all__ = ["File", "file", "function", "function_execution", "program", "program_execution", "utils",
#            "execute_test", "ProgramExecution", "Function", "create_input_file", "FunctionExecution", "Results",
#            "validate_files"]
from tiivad.utils import execute_test, validate_files


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)


__all__ = ["execute_test", "validate_files", "GenericChecks", "OutputFileChecks", "Results", "json",
           "ComplexEncoder"]
