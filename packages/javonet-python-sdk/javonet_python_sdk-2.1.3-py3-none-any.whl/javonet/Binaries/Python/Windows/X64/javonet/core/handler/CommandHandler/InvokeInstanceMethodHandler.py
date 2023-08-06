from javonet.core.handler.CommandHandler.AbstractCommandHandler import *


class InvokeInstanceMethodHandler(AbstractCommandHandler):

    def __init__(self):
        self._required_parameters_count = 2

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("InvokeInstanceMethod Parameters mismatch!")

            clazz = command.payload[0]
            method = getattr(clazz, command.payload[1])

            if len(command.payload) > 2:
                method_arguments = command.payload[2:]
                return method(*method_arguments)
            return method()
        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
