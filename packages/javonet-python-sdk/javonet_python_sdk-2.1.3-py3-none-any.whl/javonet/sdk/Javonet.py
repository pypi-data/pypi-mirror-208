from javonet.core.transmitter.PythonTransmitter import PythonTransmitter
from javonet.utils.ConnectionType import ConnectionType
from javonet.sdk.internal.RuntimeFactory import RuntimeFactory

PythonTransmitter.activate_with_licence_file()


def in_memory():
    connection_type = ConnectionType.InMemory
    return RuntimeFactory(connection_type)


def tcp(address):
    connection_type = ConnectionType.Tcp
    return RuntimeFactory(connection_type, address)


def activate(email, licence_key, proxy_host=None, proxy_user_name=None, proxy_user_password=None):
    if proxy_host is None:
        return PythonTransmitter.activate_with_credentials(email, licence_key)
    else:
        if proxy_user_name is None:
            proxy_user_name = ""
        if proxy_user_password is None:
            proxy_user_password = ""

        return PythonTransmitter.activate_with_credentials_and_proxy(email, licence_key,
                                                                     proxy_user_name, proxy_user_password)
