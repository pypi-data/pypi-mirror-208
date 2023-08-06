from javonet.core.interpreter.Interpreter import Interpreter


class Receiver:

    def __init__(self):
        self.python_interpreter = Interpreter()

    def SendCommand(self, messageByteArray, messageByteArrayLen):
        return bytearray(self.python_interpreter.process(messageByteArray, len(messageByteArray)))

    def HeartBeat(self, messageByteArray, messageByteArrayLen):
        return bytearray([49, 48])
