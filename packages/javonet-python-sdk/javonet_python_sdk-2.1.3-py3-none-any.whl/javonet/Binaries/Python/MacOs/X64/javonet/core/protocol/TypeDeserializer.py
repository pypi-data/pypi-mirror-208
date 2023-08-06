import struct

from javonet.utils import Command, CommandType, RuntimeName
from javonet.utils.StringEncodingMode import StringEncodingMode


class TypeDeserializer:

    @staticmethod
    def deserialize_int(encoded_int):
        int_value = struct.unpack("<i", bytearray(encoded_int))[0]
        return int_value

    @staticmethod
    def deserialize_unsigned_int(encoded_unsigned_int):
        unsigned_int_value = struct.unpack("<I", bytearray(encoded_unsigned_int))[0]
        return unsigned_int_value

    @staticmethod
    def deserialize_longlong(encoded_longlong):
        longlong_value = struct.unpack("<q", bytearray(encoded_longlong))[0]
        return longlong_value

    @staticmethod
    def deserialize_unsignedlonglong(encoded_unsigned_longlong):
        unsigned_longlong_value = struct.unpack("<Q", bytearray(encoded_unsigned_longlong[2:]))[0]
        return unsigned_longlong_value

    @staticmethod
    def deserialize_double(encoded_double):
        double_value = struct.unpack("<d", bytearray(encoded_double))[0]
        return double_value

    @staticmethod
    def deserialize_string(string_encoding_mode, encoded_string):

        if string_encoding_mode == StringEncodingMode.ASCII:
            string_value = bytearray(encoded_string).decode('ascii')
            return string_value
        if string_encoding_mode == StringEncodingMode.UTF8:
            string_value = bytearray(encoded_string).decode('utf-8')
            return string_value
        if string_encoding_mode == StringEncodingMode.UTF16:
            string_value = bytearray(encoded_string).decode('utf-16')
            return string_value
        if string_encoding_mode == StringEncodingMode.UTF32:
            string_value = bytearray(encoded_string).decode('utf-32')
            return string_value

        raise IndexError("String encoding mode out of range")


    @staticmethod
    def deserialize_float(encoded_float):
        float_value = struct.unpack("<f", bytearray(encoded_float))[0]
        return float_value

    @staticmethod
    def deserialize_bool(encoded_bool):
        bool_value = struct.unpack("?", bytearray(encoded_bool))[0]
        return bool_value

    @staticmethod
    def deserialize_char(encoded_char):
        char_value = struct.unpack("<c", bytearray(encoded_char))[0]
        return char_value

    @staticmethod
    def deserialize_bytes(encoded_bytes):
        bytes_value = struct.unpack("<c", bytearray(encoded_bytes))[0]
        return bytes_value

    @staticmethod
    def deserialize_command(command_byte_array):
        command = Command(RuntimeName(command_byte_array[0]), CommandType(command_byte_array[1]), [])
        return command
