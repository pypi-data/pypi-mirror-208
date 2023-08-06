from javonet.core.transmitter.PythonTransmitterWrapper import PythonTransmitterWrapper


class PythonTransmitter:

    @staticmethod
    def send_command(message):
        return PythonTransmitterWrapper.send_command(message)

    @staticmethod
    def __activate(email="", licence_key="", proxy_host="", proxy_user_name="", proxy_user_password=""):
        return PythonTransmitterWrapper.activate(email, licence_key, proxy_host, proxy_user_name, proxy_user_password)

    @staticmethod
    def activate_with_licence_file():
        return PythonTransmitter.__activate()

    @staticmethod
    def activate_with_credentials(email, licence_key):
        return PythonTransmitter.__activate(email, licence_key)

    @staticmethod
    def activate_with_credentials_and_proxy(email, licence_key, proxy_host, proxy_user_name, proxy_user_password):
        return PythonTransmitter.__activate(email, licence_key, proxy_host, proxy_user_name, proxy_user_password)
