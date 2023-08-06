from javonet.core.handler.CommandHandler.AbstractCommandHandler import AbstractCommandHandler


class ArraySetItemHandler(AbstractCommandHandler):
    def __init__(self):
        self._required_parameters_count = 3

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("ArraySetItemHandler parameters mismatch!")

            array = command.payload[0]
            value = command.payload[1]
            indexes = command.payload[2:]
            if len(indexes) == 1:
                array[indexes[0]] = value
                return 0

        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
