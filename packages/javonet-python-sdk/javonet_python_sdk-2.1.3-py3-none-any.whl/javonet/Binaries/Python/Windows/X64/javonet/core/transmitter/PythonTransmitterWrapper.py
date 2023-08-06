import os
import platform
from ctypes import *

from javonet.core.callback.callbackFunc import callbackFunc

CMPFUNC = CFUNCTYPE(py_object, POINTER(c_ubyte), c_int)
callbackFunction = CMPFUNC(callbackFunc)


class PythonTransmitterWrapper:
    if platform.system() == 'Windows':
        file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        python_lib_path = file_path + '\\Binaries\\Native\\Windows\\X64\\JavonetPythonRuntimeNative.dll'
    if platform.system() == 'Linux':
        file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        python_lib_path = file_path + '/Binaries/Native/Linux/X64/libJavonetPythonRuntimeNative.so'
    if platform.system() == 'Darwin':
        file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        python_lib_path = file_path + '/Binaries/Native/MacOs/X64/libJavonetPythonRuntimeNative.dylib'

    python_lib = cdll.LoadLibrary(python_lib_path)
    python_lib.SetCallback(callbackFunction)

    @staticmethod
    def send_command(message):
        message_array = bytearray(message)
        message_ubyte_array = c_ubyte * len(message_array)
        response_array_len = PythonTransmitterWrapper.python_lib.SendCommand(
            message_ubyte_array.from_buffer(message_array),
            len(message_array))
        if response_array_len > 0:
            response = bytearray(response_array_len)
            response_ubyte_array = c_ubyte * response_array_len
            PythonTransmitterWrapper.python_lib.ReadResponse(response_ubyte_array.from_buffer(response),
                                                             response_array_len)
            return response
        elif response_array_len == 0:
            error_message = "Response is empty"
            raise RuntimeError(error_message)
        else:
            get_native_error = PythonTransmitterWrapper.python_lib.GetNativeError
            get_native_error.restype = c_char_p
            get_native_error.argtypes = []
            error_message = get_native_error()
            raise RuntimeError(
                "Javonet native error code: " + str(response_array_len) + ". " + str(error_message))

    @staticmethod
    def activate(email, licence_key, proxy_host, proxy_user_name, proxy_user_password):
        activate = PythonTransmitterWrapper.python_lib.Activate
        activate.restype = c_int
        activate.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]

        activation_result = activate(email.encode('ascii'),
                                     licence_key.encode('ascii'),
                                     proxy_host.encode('ascii'),
                                     proxy_user_name.encode('ascii'),
                                     proxy_user_password.encode('ascii'))

        if activation_result < 0:
            get_native_error = PythonTransmitterWrapper.python_lib.GetNativeError
            get_native_error.restype = c_char_p
            get_native_error.argtypes = []
            error_message = get_native_error()
            raise RuntimeError(
                "Javonet activation result: " + str(activation_result) + ". Native error message: " + str(error_message))
        else:
            return activation_result
        