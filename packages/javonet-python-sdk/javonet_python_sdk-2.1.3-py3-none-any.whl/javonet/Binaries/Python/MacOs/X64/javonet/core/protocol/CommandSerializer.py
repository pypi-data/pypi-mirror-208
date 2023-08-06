import struct
from collections import deque
from typing import Deque

from javonet.core.protocol.TypeSerializer import TypeSerializer
from javonet.utils.Command import Command
from javonet.utils.ConnectionType import ConnectionType
from javonet.utils.RuntimeName import RuntimeName


class CommandSerializer:
    byte_buffer = []

    def encode(self, root_command, connection_type, tcp_address=None, runtime_version=0):
        queue: Deque[Command] = deque()
        queue.append(root_command)
        self.insert_into_buffer([root_command.runtime_name.value, runtime_version])
        if connection_type == ConnectionType.Tcp.value:
            self.insert_into_buffer([ConnectionType.Tcp.value])
            self.insert_into_buffer(self.serialize_tcp(tcp_address))
        else:
            self.insert_into_buffer([ConnectionType.InMemory.value])
            self.insert_into_buffer(self.serialize_tcp("0.0.0.0:0"))
        self.insert_into_buffer([RuntimeName.python.value, root_command.command_type.value])
        return self.serialize_recursively(queue)

    @staticmethod
    def serialize_tcp(tcp_address):
        if isinstance(tcp_address, list):
            return tcp_address
        else:
            tcp_address_array = tcp_address.split(':')
            tcp_address_ip = tcp_address_array[0].split('.')
            tcp_address_port = tcp_address_array[1]
            tcp_address_bytearray = []
            for address in tcp_address_ip:
                tcp_address_bytearray += [int(address)]
            tcp_address_bytearray += list(bytearray(struct.pack("<h", int(tcp_address_port))))
            return tcp_address_bytearray

    @staticmethod
    def serialize_primitive(payload_item):
        if isinstance(payload_item, bool):
            serialized_bool = TypeSerializer.serialize_bool(payload_item)
            return serialized_bool
        elif isinstance(payload_item, int):
            serialized_int = TypeSerializer.serialize_int(payload_item)
            return serialized_int
        elif isinstance(payload_item, float):
            serialized_float = TypeSerializer.serialize_float(payload_item)
            return serialized_float
        elif isinstance(payload_item, str):
            serialized_string = TypeSerializer.serialize_string(payload_item)
            return serialized_string
        else:
            return None

    def insert_into_buffer(self, arguments):
        self.byte_buffer = self.byte_buffer + arguments

    def serialize_recursively(self, queue):
        if not queue:
            return self.byte_buffer
        command = queue.pop()
        queue.append(command.drop_first_payload_argument())
        if len(command.get_payload()) > 0:
            if isinstance(command.get_payload()[0], Command):
                inner_command = command.get_payload()[0]
                self.insert_into_buffer(TypeSerializer.serialize_command(inner_command))
                queue.append(inner_command)
            elif isinstance(command.get_payload()[0], Exception):
                result = self.serialize_primitive(str(command.get_payload()[0]))
                self.insert_into_buffer(result)
            else:
                result = self.serialize_primitive(command.get_payload()[0])
                self.insert_into_buffer(result)
            return self.serialize_recursively(queue)
        else:
            queue.pop()

        return self.serialize_recursively(queue)
