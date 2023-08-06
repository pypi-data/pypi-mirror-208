from javonet.core.handler.CommandHandler.AbstractCommandHandler import *
import sys


class LoadLibraryHandler(AbstractCommandHandler):
    loaded_library = 0

    def __init__(self):
        pass

    def process(self, command):
        try:
            if len(command.payload) != 1:
                raise Exception("LoadLibrary payload parameters mismatch")

            sys.path.append(command.payload[0])

            return 0
        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
