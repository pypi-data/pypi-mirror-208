from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.ConnectionType import ConnectionType
from javonet.sdk.internal.RuntimeContext import RuntimeContext
from javonet.sdk.internal.abstract.AbstractRuntimeFactory import AbstractRuntimeFactory


class RuntimeFactory(AbstractRuntimeFactory):

    def __init__(self, connection_type, tcp_address=None):
        self.connection_type = connection_type
        if connection_type is ConnectionType.Tcp:
            if tcp_address is None:
                raise Exception("Error tcp ip adress is not given!")
        self.tcp_address = tcp_address

    def clr(self):
        return RuntimeContext.get_instance(RuntimeName.clr, self.connection_type, self.tcp_address)

    def go(self):
        return RuntimeContext.get_instance(RuntimeName.go, self.connection_type, self.tcp_address)

    def jvm(self):
        return RuntimeContext.get_instance(RuntimeName.jvm, self.connection_type, self.tcp_address)

    def netcore(self):
        return RuntimeContext.get_instance(RuntimeName.netcore, self.connection_type, self.tcp_address)

    def perl(self):
        return RuntimeContext.get_instance(RuntimeName.perl, self.connection_type, self.tcp_address)

    def ruby(self):
        return RuntimeContext.get_instance(RuntimeName.ruby, self.connection_type, self.tcp_address)

    def nodejs(self):
        return RuntimeContext.get_instance(RuntimeName.nodejs, self.connection_type, self.tcp_address)

    def python(self):
        return RuntimeContext.get_instance(RuntimeName.python, self.connection_type, self.tcp_address)
