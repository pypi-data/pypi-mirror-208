require_relative 'abstract_command_handler'

class GetTypeHandler < AbstractCommandHandler
  def initialize
    @required_parameters_count = 1
  end

  def process(command)
    begin
      if command.payload.length < @required_parameters_count
        raise "Get Type parameters mismatch"
      end
      if command.payload.length > @required_parameters_count
        return Object::const_get(command.payload[1])
      else
        return Object::const_get(command.payload[0])
      end
    rescue Exception => e
      return e
    end
  end
end