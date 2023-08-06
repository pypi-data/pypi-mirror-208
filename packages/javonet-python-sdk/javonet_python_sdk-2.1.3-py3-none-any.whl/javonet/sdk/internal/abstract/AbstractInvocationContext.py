import abc


class AbstractInvocationContext(abc.ABC):

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def get_value(self):
        pass
