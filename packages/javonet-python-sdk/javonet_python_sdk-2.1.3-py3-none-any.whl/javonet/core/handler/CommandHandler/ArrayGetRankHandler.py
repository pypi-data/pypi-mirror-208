from javonet.core.handler.CommandHandler.AbstractCommandHandler import AbstractCommandHandler
#import numpy as np


class ArrayGetRankHandler(AbstractCommandHandler):
    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("ArrayGetRankHandler parameters mismatch!")
            raise Exception("ArrayGetRankHandler not implemented")
            #array = command.payload[0]

            #np_array = np.array(array)
            #return np_array.ndim

        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
