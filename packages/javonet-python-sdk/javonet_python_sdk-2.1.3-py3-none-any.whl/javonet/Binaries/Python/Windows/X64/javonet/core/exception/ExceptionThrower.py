import re
import sys
import traceback
import types

from javonet.core.exception.JavonetException import JavonetException
from javonet.utils.ExceptionType import ExceptionType
from javonet.utils.Command import Command


class ExceptionThrower:

    @staticmethod
    def throw_exception(command_exception: Command):
        original_exception = ExceptionType.to_exception(command_exception.get_payload()[0])
        javonet_stack_command = command_exception.get_payload()[1]
        exception_name = command_exception.get_payload()[2]
        exception_message = command_exception.get_payload()[3]

        stack_classes, stack_methods, stack_lines, stack_files = ExceptionThrower.get_local_stack_trace(command_exception.get_payload()[4],
                                                command_exception.get_payload()[5],
                                                command_exception.get_payload()[6],
                                                command_exception.get_payload()[7])
        traceback_str = ""

        for i in range(len(stack_methods) - 1):
            traceback_str += "File \"{}\", line {}, in {}\n".format(stack_files[i], stack_lines[i], stack_methods[i])
            if stack_classes[i]:
                traceback_str += "    {}\n".format(stack_classes[i])

        ExceptionThrower.raise_exception(original_exception,exception_message,traceback_str)


    @staticmethod
    def raise_exception(original_exception, exception_message, traceback_str):
        raise JavonetException(str(original_exception), exception_message, traceback_str)

    @staticmethod
    def get_local_stack_trace(stack_trace_classes, stack_trace_methods, stack_trace_lines, stack_trace_files):
        stack_classes = re.split("\\|", stack_trace_classes)
        stack_methods = re.split("\\|", stack_trace_methods)
        stack_lines = re.split("\\|", stack_trace_lines)
        stack_files = re.split("\\|", stack_trace_files)

        return [stack_classes, stack_methods, stack_lines, stack_files]