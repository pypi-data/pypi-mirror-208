module TransmitterWrapper
  extend FFI::Library
  if OS.linux?
    ffi_lib File.expand_path('../../../Binaries/Native/Linux/X64/libJavonetRubyRuntimeNative.so', __FILE__)
  elsif OS.mac?
    ffi_lib File.expand_path('../../../Binaries/Native/MacOs/X64/libJavonetRubyRuntimeNative.dylib', __FILE__)
  else
    RubyInstaller::Runtime.add_dll_directory(File.expand_path('../../../Binaries/Native/Windows/X64/', __FILE__))
    ffi_lib File.expand_path('../../../Binaries/Native/Windows/X64/JavonetRubyRuntimeNative.dll', __FILE__)
  end
  attach_function :SendCommand, [:pointer, :int], :int
  attach_function :ReadResponse, [:pointer, :int], :int
  attach_function :Activate, [:pointer, :pointer, :pointer, :pointer, :pointer], :int
  attach_function :GetNativeError, [], :string

end
