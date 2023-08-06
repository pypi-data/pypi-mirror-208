require_relative 'abstract_command_handler'

class InvokeStaticMethodHandler < AbstractCommandHandler
  def initialize
    @required_parameters_count = 2
  end

  def process(command)
    invoke_static_method(command)
  end

  def invoke_static_method(command)
    begin
      if command.payload.length < @required_parameters_count
        raise "Static method parameters mismatch"
      end
      if command.payload.length > @required_parameters_count
        args = command.payload[2..]
        command.payload[0].send(command.payload[1], *args)
      else
        command.payload[0].send(command.payload[1])
      end
    rescue Exception => e
      return e
    end
  end
end
