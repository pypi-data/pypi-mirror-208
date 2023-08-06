import abc


class AbstractInstanceContext(abc.ABC):

    @abc.abstractmethod
    def invoke_instance_method(self, string):
        pass

    @abc.abstractmethod
    def get_instance_field(self, string: str):
        pass

    @abc.abstractmethod
    def create_instance(self, class_name: str):
        pass
