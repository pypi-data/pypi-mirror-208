require_relative '../../utils/string_encoding_mode'

class TypeDeserializer

  def self.deserialize_int(encoded_int)
    int_value = encoded_int.map(&:chr).join.unpack('i').first
    return int_value
  end

  # def self.deserialize_unsigned_int(encoded_unsigned_int)
  #   unsigned_int_value = struct.unpack("<I", bytearray(encoded_unsigned_int))[0]
  #   return unsigned_int_value
  # end
  #
  # def self.deserialize_longlong(encoded_longlong)
  #   longlong_value = struct.unpack("<q", bytearray(encoded_longlong))[0]
  #   return longlong_value
  # end


  def self.deserialize_double(encoded_double)
    double_value = encoded_double.map(&:chr).join.unpack('d').first
    return double_value
  end

  def self.deserialize_string(string_encoding_mode, encoded_string)

    case string_encoding_mode
    when StringEncodingMode::ASCII
        string_value = encoded_string.pack('C*').force_encoding("US-ASCII").encode("UTF-8")
    when StringEncodingMode::UTF8
        string_value = encoded_string.pack("C*").force_encoding("UTF-8").encode("UTF-8")
    when StringEncodingMode::UTF16
        string_value = encoded_string.pack("C*").force_encoding("UTF-16LE").encode("UTF-8")
    when StringEncodingMode::UTF32
        string_value = encoded_string.pack("C*").force_encoding("UTF-32").encode("UTF-8")
    else
        raise "Argument out of range in deserialize_string"
    end

    return string_value
  end

  def self.deserialize_float(encoded_float)
    float_value = encoded_float.map(&:chr).join.unpack('f').first
    return float_value
  end

  def self.deserialize_bool(encoded_bool)
    if encoded_bool[0] == 1
      bool_value = true
    else
      bool_value = false
    end

    return bool_value
  end

  # def self.deserialize_char(encoded_char)
  #   char_value = struct.unpack("<c", bytearray(encoded_char))[0]
  #   return char_value
  # end
  #
  # def self.deserialize_bytes(encoded_bytes)
  #   bytes_value = struct.unpack("<c", bytearray(encoded_bytes))[0]
  #   return bytes_value
  # end

  def self.deserialize_command(command_byte_array)
    python_command = Command.new(RuntimeName(command_byte_array[0]), CommandType(command_byte_array[1]), [])
    return python_command
  end

end