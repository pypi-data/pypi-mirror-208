require_relative 'type_serializer'
require_relative '../../utils/connection_type'
require_relative '../../utils/runtime_name'

class CommandSerializer

  def initialize
    @byte_buffer = []
  end


  def encode(root_command, connection_type = ConnectionType::IN_MEMORY, tcp_address = nil, runtimeVersion = 0)
    queue = []
    queue.unshift(root_command)
    self.insert_into_buffer([root_command.runtime_name, runtimeVersion])
    if connection_type == ConnectionType::TCP
      self.insert_into_buffer([ConnectionType::TCP])
      self.insert_into_buffer(self.serialize_tcp(tcp_address))
    end
    if connection_type == ConnectionType::IN_MEMORY
      self.insert_into_buffer([ConnectionType::IN_MEMORY])
      self.insert_into_buffer([0, 0, 0, 0, 0, 0])
    end
    self.insert_into_buffer([RuntimeName::RUBY, root_command.command_type])
    return self.serialize_recursively(queue)
  end

  def serialize_tcp(tcp_address)
    if tcp_address.kind_of?(Array)
      return tcp_address
    else
      tcp_address_array = tcp_address.split(':')
      tcp_address_ip = tcp_address_array[0].split('.')
      tcp_address_port = tcp_address_array[1]
      tcp_address_bytearray = []
      for address in tcp_address_ip
        tcp_address_bytearray.concat([address.to_i])
      end
      port_byte = [tcp_address_port.to_i].pack("s_").bytes
      tcp_address_bytearray.concat(port_byte)
      return tcp_address_bytearray

    end

  end

  def serialize_primitive(payload_item)
    if payload_item.is_a? Integer
      serialized_int = TypeSerializer.serialize_int(payload_item)
      return serialized_int
    elsif payload_item.is_a? String
      serialized_string = TypeSerializer.serialize_string(payload_item)
      return serialized_string
    elsif payload_item.is_a? Float
      serialized_float = TypeSerializer.serialize_float(payload_item)
      return serialized_float
    elsif [true,false].include? payload_item
      serialized_bool = TypeSerializer.serialize_bool(payload_item)
      return serialized_bool
    else
      return nil
    end
  end

  def insert_into_buffer(arguments)
    new_byte_buffer = @byte_buffer + arguments
    @byte_buffer = new_byte_buffer

  end

  def serialize_recursively(queue)
    if queue.length == 0
      return @byte_buffer
    end
    command = queue.shift
    queue.unshift(command.drop_first_payload_argument)
    if command.payload.length > 0
      if command.payload[0].is_a? Command
        inner_command = command.payload[0]
        self.insert_into_buffer(TypeSerializer.serialize_command(inner_command))
        queue.unshift(inner_command)
      else
        result = self.serialize_primitive(command.payload[0])
        self.insert_into_buffer(result)
        return self.serialize_recursively(queue)
      end
    else
      queue.shift
    end
    return self.serialize_recursively(queue)
  end

end