require_relative 'abstract_command_handler'

class CreateClassInstanceHandler < AbstractCommandHandler
  def initialize
    @required_parameters_count = 1
  end

  def process(command)
    return create_class_instance(command)
  end

  def create_class_instance(command)
    begin
      if command.payload.length < @required_parameters_count
        raise "Class instance parameters mismatch"
      end
      if command.payload.length > 1
        constructor_arguments = command.payload[1..]
        class_instance = command.payload[0].send('new', *constructor_arguments)
      else
        class_instance = command.payload[0].send('new')
      end
      return class_instance
    rescue Exception => e
      return e
    end
  end

end