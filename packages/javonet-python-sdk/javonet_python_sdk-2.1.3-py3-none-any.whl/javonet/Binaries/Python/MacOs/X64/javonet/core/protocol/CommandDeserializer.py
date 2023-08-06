from javonet.core.protocol.TypeDeserializer import TypeDeserializer
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.Type import Type
from javonet.utils.StringEncodingMode import StringEncodingMode


class CommandDeserializer:
    position = 0
    buffer = []
    command = 0
    buffer_len = 0

    def __init__(self, buffer, buffer_len):
        self.buffer = buffer
        self.buffer_len = buffer_len
        self.command = Command(RuntimeName(buffer[0]), CommandType(buffer[10]), [])
        self.position = 11

    def is_at_end(self):
        return self.position == self.buffer_len

    def decode(self):
        while not self.is_at_end():
            self.command = self.command.add_arg_to_payload(self.read_object(self.buffer[self.position]))
        return self.command

    # def copy_from(self, bytes_to_copy, elements_to_skip):
    #     size = len(bytes_to_copy) - elements_to_skip
    #     new_byte_array = bytes_to_copy[size]
    #
    #
    #     return new_byte_array

    def read_object(self, type_num):
        type_value = Type(type_num)
        if type_value == Type.Command:
            return self.read_command()
        elif type_value == Type.JavonetInteger:
            return self.read_int()
        elif type_value == Type.JavonetString:
            return self.read_string()
        elif type_value == Type.JavonetBoolean:
            return self.read_bool()
        elif type_value == Type.JavonetFloat:
            return self.read_float()
        elif type_value == Type.JavonetDouble:
            return self.read_double()
        else:
            Exception("Type not supported")

    def read_command(self):
        p = self.position
        number_of_elements_in_payload = TypeDeserializer.deserialize_int(self.buffer[p + 1: p + 5])
        runtime = self.buffer[p + 5]
        command_type = self.buffer[p + 6]

        self.position += 7
        return_command = Command(RuntimeName(runtime), CommandType(command_type), [])
        return self.read_command_recursively(number_of_elements_in_payload, return_command)

    def read_command_recursively(self, number_of_elements_in_payload_left, cmd):
        if number_of_elements_in_payload_left == 0:
            return cmd
        else:
            p = self.position
            cmd = cmd.add_arg_to_payload(self.read_object(self.buffer[p]))
            return self.read_command_recursively(number_of_elements_in_payload_left - 1, cmd)

    def read_int(self):
        self.position += 2
        p = self.position
        self.position += 4
        return TypeDeserializer.deserialize_int(self.buffer[p:p + 4])

    def read_string(self):
        p = self.position
        string_encoding_mode = StringEncodingMode(self.buffer[p+1])
        size = TypeDeserializer.deserialize_int(self.buffer[p + 2:p + 6])
        self.position += 6
        p = self.position
        decoded_string = TypeDeserializer.deserialize_string(string_encoding_mode, self.buffer[p:p + size])
        self.position += size
        return decoded_string

    def read_bool(self):
        p = self.position
        size = self.buffer[p + 1]
        self.position += 2
        p = self.position
        decoded_bool = TypeDeserializer.deserialize_bool(self.buffer[p:p + size])
        self.position += size
        return decoded_bool

    def read_float(self):
        p = self.position
        size = self.buffer[p + 1]
        self.position += 2
        p = self.position
        decoded_float = TypeDeserializer.deserialize_float(self.buffer[p:p + size])
        self.position += size
        return decoded_float

    def read_double(self):
        p = self.position
        size = self.buffer[p + 1]
        self.position += 2
        p = self.position
        decoded_double = TypeDeserializer.deserialize_double(self.buffer[p:p + size])
        self.position += size
        return decoded_double
