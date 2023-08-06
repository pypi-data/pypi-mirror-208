import abc


class AbstractTypeContext(abc.ABC):

    @abc.abstractmethod
    def get_type(self, string):
        pass
