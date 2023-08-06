from javonet.core.exception.ExceptionThrower import ExceptionThrower
from javonet.core.interpreter.Interpreter import Interpreter
from javonet.sdk.internal.InvocationContextEnum import InvocationContextEnum
from javonet.sdk.internal.abstract.AbstractInstanceContext import AbstractInstanceContext
from javonet.sdk.internal.abstract.AbstractInvocationContext import AbstractInvocationContext
from javonet.sdk.internal.abstract.AbstractMethodInvocationContext import AbstractMethodInvocationContext
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.ConnectionType import ConnectionType
from javonet.utils.RuntimeName import RuntimeName


class InvocationContext(AbstractInvocationContext, AbstractMethodInvocationContext, AbstractInstanceContext):

    def __init__(self, runtime_name: RuntimeName, connection_type: ConnectionType, tcp_ip_address,
                 current_command: Command, is_executed=False):
        self.__is_executed = is_executed
        self.__runtime_name = runtime_name
        self.__connection_type = connection_type
        self.__tcp_ip_address = tcp_ip_address
        self.__current_command = current_command
        self.__response_command = None
        self.__python_interpreter = Interpreter()

    def __del__(self):
        if self.__current_command.command_type == CommandType.Reference and self.__is_executed is True:
            self.__current_command = Command(self.__runtime_name, CommandType.DestructReference,
                                             self.__current_command.payload)
            self.execute()

    def __iter__(self):
        if self.__current_command.command_type != CommandType.Reference:
            raise Exception("Object is not iterable")
        else:
            self.__invocation_context_enum = InvocationContextEnum(self)
            return self.__invocation_context_enum.__iter__()

    def __next__(self):
        if self.__current_command.command_type != CommandType.Reference:
            raise Exception("Object is not iterable")
        else:
            return self.__invocation_context_enum.__next__()

    def __getitem__(self, key):
        if self.__current_command.command_type != CommandType.Reference:
            raise Exception("Object is not iterable")
        else:
            self.__invocation_context_enum = InvocationContextEnum(self)
            return self.__invocation_context_enum.__getitem__(key)

    def __setitem__(self, key, value):
        if self.__current_command.command_type != CommandType.Reference:
            raise Exception("Object is not iterable")
        else:
            self.__invocation_context_enum = InvocationContextEnum(self)
            return self.__invocation_context_enum.__setitem__(key, value)

    def execute(self):
        self.__response_command = self.__python_interpreter.execute(self.__current_command,
                                                                    self.__connection_type,
                                                                    self.__tcp_ip_address)

        if self.__response_command.command_type == CommandType.Exception:
            ExceptionThrower.throw_exception(self.__response_command)

        if self.__current_command.command_type == CommandType.CreateClassInstance:
            self.__current_command = self.__response_command
            self.__is_executed = True
            return self

        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__response_command, True)

    def invoke_static_method(self, *args):
        local_command = Command(self.__runtime_name, CommandType.InvokeStaticMethod, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def invoke_instance_method(self, *args):
        local_command = Command(self.__runtime_name, CommandType.InvokeInstanceMethod, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def get_static_field(self, *args):
        local_command = Command(self.__runtime_name, CommandType.GetStaticField, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def set_static_field(self, *args):
        local_command = Command(self.__runtime_name, CommandType.SetStaticField, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def create_instance(self, *args):
        local_command = Command(self.__runtime_name, CommandType.CreateClassInstance, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def set_generic_type(self, string: str):
        return self

    def get_instance_field(self, *args):
        local_command = Command(self.__runtime_name, CommandType.GetInstanceField, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def get_index(self, *args):
        local_command = Command(self.__runtime_name, CommandType.ArrayGetItem, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def get_size(self, *args):
        local_command = Command(self.__runtime_name, CommandType.ArrayGetSize, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def get_rank(self, *args):
        local_command = Command(self.__runtime_name, CommandType.ArrayGetRank, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def set_index(self, *args):
        local_command = Command(self.__runtime_name, CommandType.ArraySetItem, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_type, self.__tcp_ip_address,
                                 self.__build_command(local_command))

    def get_value(self):
        return self.__current_command.payload[0]

    def __build_command(self, command):
        for i in range(len(command.payload)):
            command.payload[i] = self.__encapsulate_payload_item(command.payload[i])

        return command.append_arg_to_payload(self.__current_command)

    # encapsulate payload item into command
    def __encapsulate_payload_item(self, payload_item):
        if isinstance(payload_item, InvocationContext):
            return Command(self.__runtime_name, CommandType.Value, [payload_item.__current_command])
        elif isinstance(payload_item, list):
            for i in range(len(payload_item)):
                payload_item[i] = self.__encapsulate_payload_item(payload_item[i])
            return Command(self.__runtime_name, CommandType.Array, payload_item)
        else:
            return Command(self.__runtime_name, CommandType.Value, [payload_item])
