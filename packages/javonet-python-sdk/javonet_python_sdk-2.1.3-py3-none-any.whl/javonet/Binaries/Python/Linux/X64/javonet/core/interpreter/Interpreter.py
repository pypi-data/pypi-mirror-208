from javonet.core.handler.Handler import Handler
from javonet.core.protocol.CommandDeserializer import CommandDeserializer
from javonet.core.protocol.CommandSerializer import CommandSerializer
from javonet.utils.RuntimeName import RuntimeName


class Interpreter:

    response = None

    def execute(self, command, connection_type, tcp_address):
        command_serializer = CommandSerializer()
        serialized_command = command_serializer.encode(command, connection_type, tcp_address)
        if command.runtime_name == RuntimeName.python:
            from javonet.core.receiver.Receiver import Receiver
            response = Receiver().SendCommand(serialized_command, len(serialized_command))
        else:
            from javonet.core.transmitter.PythonTransmitter import PythonTransmitter
            response = PythonTransmitter.send_command(serialized_command)
        command_deserializer = CommandDeserializer(response, len(response))

        return command_deserializer.decode()

    def process(self, byte_array, byte_array_len):
        command_deserializer = CommandDeserializer(byte_array, byte_array_len)
        received_command = command_deserializer.decode()
        python_handler = Handler()
        command_serializer = CommandSerializer()
        response_command = python_handler.handle_command(received_command)
        encoded_response = command_serializer.encode(response_command, 0, "0.0.0.0:0")
        return encoded_response
