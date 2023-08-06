require_relative 'type_deserializer'
require_relative '../../utils/type'
require_relative '../../utils/command'
require_relative '../../utils/string_encoding_mode'

class CommandDeserializer


    def initialize(buffer,byte_array_len)
        @buffer = buffer
        @byte_array_len = byte_array_len
        @command = Command.new(buffer[0], buffer[10], [])
        @position = 11
    end

    def is_at_end
        return @position == @byte_array_len
    end

    def decode
        until is_at_end
            @command = @command.add_arg_to_payload(read_object(@buffer[@position]))
        end
        return @command
    end

    # def copy_from(self, bytes_to_copy, elements_to_skip):
    #     size = len(bytes_to_copy) - elements_to_skip
    #     new_byte_array = bytes_to_copy[size]
    #
    #
    #     return new_byte_array

    def read_object(type_num)
        type_value = type_num
        if type_value == Type::COMMAND
            return self.read_command
        elsif type_value == Type::JAVONET_INTEGER
            return self.read_int
        elsif type_value == Type::JAVONET_STRING
            return self.read_string
        elsif type_value == Type::JAVONET_BOOLEAN
            return self.read_bool
        elsif type_value == Type::JAVONET_FLOAT
            return self.read_float
        elsif type_value == Type::JAVONET_DOUBLE
            return self.read_double
        else
            Exception("Type not supported")
        end
    end


    def read_command
        p = @position
        number_of_elements_in_payload = TypeDeserializer.deserialize_int(@buffer[p+1..p+4])
        runtime = @buffer[p + 5]
        command_type = @buffer[p + 6]

        @position += 7
        return_command = Command.new(runtime, command_type, [])
        return read_command_recursively(number_of_elements_in_payload, return_command)
    end

    def read_command_recursively(number_of_elements_in_payload_left, cmd)
        if number_of_elements_in_payload_left == 0
            return cmd
        else
            p = @position
            new_command = cmd.add_arg_to_payload(self.read_object(@buffer[p]))
            return read_command_recursively(number_of_elements_in_payload_left - 1, new_command)
        end

    end

    def read_int
        @position += 2
        p = @position
        @position += 4
        return TypeDeserializer.deserialize_int(@buffer[p..p + 4 - 1])
    end


    def read_string
        p = @position
        string_encoding_mode = @buffer[p+1]
        size = TypeDeserializer.deserialize_int(@buffer[p+2..p + 5])
        @position += 6
        p = @position
        decoded_string = TypeDeserializer.deserialize_string(string_encoding_mode, @buffer[p..p + size-1])
        @position += size
        return decoded_string
    end

    def read_bool
        p = @position
        size = @buffer[p + 1]
        @position += 2
        p = @position
        decoded_bool = TypeDeserializer.deserialize_bool(@buffer[p..p + size])
        @position += size
        return decoded_bool
    end


    def read_float
        p = @position
        size = @buffer[p + 1]
        @position += 2
        p = @position
        decoded_float = TypeDeserializer.deserialize_float(@buffer[p..p + size - 1])
        @position += size
        return decoded_float
    end


    def read_double
        p = @position
        size = @buffer[p + 1]
        @position += 2
        p = @position
        decoded_double = TypeDeserializer.deserialize_double(@buffer[p..p + size -1])
        @position += size
        return decoded_double
    end
end