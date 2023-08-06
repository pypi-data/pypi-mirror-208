from javonet.core.handler.CommandHandler.AbstractCommandHandler import AbstractCommandHandler


class CastingHandler(AbstractCommandHandler):
    def process(self, command):
        raise Exception("Explicit cast is forbidden in dynamically typed languages")
