from javonet.core.handler.CommandHandler.AbstractCommandHandler import *


class SetStaticFieldHandler(AbstractCommandHandler):

    def __init__(self):
        self._required_parameters_count = 3

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("SetStaticFieldHandler parameters mismatch!")

            clazz = command.payload[0]
            setattr(clazz, command.payload[1], command.payload[2])
            return "SetStaticFieldHandler - success"
        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
