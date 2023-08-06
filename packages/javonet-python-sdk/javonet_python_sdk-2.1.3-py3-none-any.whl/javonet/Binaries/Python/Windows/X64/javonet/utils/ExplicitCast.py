from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType


class ExplicitCast:
    @staticmethod
    def cast(value, target_type):
        return Command(
            100,
            CommandType.Cast,
            [
                value,
                Command(
                    100,
                    CommandType.GetType,
                    [
                        target_type
                    ]
                )
            ]
        )
