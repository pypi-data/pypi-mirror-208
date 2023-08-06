require_relative '../../utils/type'
require_relative '../../utils/string_encoding_mode'

class TypeSerializer

  def self.serialize_type(type_value)
      return TypeSerializer.serialize_int(type_value)
  end

  def self.serialize_int(int_value)
    encoded_int_list = [int_value].pack("i").bytes
    length = encoded_int_list.length
    return [Type::JAVONET_INTEGER, length] + encoded_int_list
  end

  def self.serialize_unsigned_int(unsigned_int_value)
      encoded_unsigned_int_list = [unsigned_int_value].pack("I").bytes
      length = len(encoded_unsigned_int_list)
      return [Type::JAVONET_UNSIGNED_INTEGER, length] + encoded_unsigned_int_list
  end

  # def serialize_longlong(longlong_value)
  #     encoded_longlong_list = list(bytearray(struct.pack("<q", longlong_value)))
  #     length = len(encoded_longlong_list)
  #     return [Type::JAVONET_LONG_LONG, length] + encoded_longlong_list
  # end
  #
  # def serialize_unsignedlonglong(unsigned_longlong_value)
  #     encoded_unsignedlonglong_list = list(bytearray(struct.pack("<q", unsigned_longlong_value)))
  #     length = len(encoded_unsignedlonglong_list)
  #     return [Type::JAVONET_UNSIGNED_LONG_LONG, length] + encoded_unsignedlonglong_list
  # end

  def self.serialize_double(double_value)
      encoded_double_list = [double_value].pack("d").bytes
      length = encoded_double_list.length
      return [Type::JAVONET_DOUBLE, length] + encoded_double_list
  end

  def self.serialize_string(string_value)
      encoded_string_list = string_value.bytes
      length = [encoded_string_list.length].pack("i").bytes
      return [Type::JAVONET_STRING, StringEncodingMode::UTF8] + length + encoded_string_list
  end

  def self.serialize_float(float_value)
      encoded_float_list = [float_value].pack("f").bytes
      length = encoded_float_list.length
      return [Type::JAVONET_FLOAT, length] + encoded_float_list
  end

  def self.serialize_bool(bool_value)
    if bool_value
      encoded_bool_list = [1]
    else
      encoded_bool_list = [0]
    end
      length = encoded_bool_list.length
      return [Type::JAVONET_BOOLEAN, length] + encoded_bool_list
  end


  def self.serialize_command(command)
      length = [command.payload.length()].pack("i").bytes
      return [Type::COMMAND] + length + [command.runtime_name, command.command_type]
  end

end
