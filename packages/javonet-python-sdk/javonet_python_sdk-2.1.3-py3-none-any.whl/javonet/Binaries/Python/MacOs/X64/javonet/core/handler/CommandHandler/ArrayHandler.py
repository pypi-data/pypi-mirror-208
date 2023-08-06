from javonet.core.handler.CommandHandler.AbstractCommandHandler import AbstractCommandHandler


class ArrayHandler(AbstractCommandHandler):
    def process(self, command):
        try:
            array = command.payload
            return array

        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
