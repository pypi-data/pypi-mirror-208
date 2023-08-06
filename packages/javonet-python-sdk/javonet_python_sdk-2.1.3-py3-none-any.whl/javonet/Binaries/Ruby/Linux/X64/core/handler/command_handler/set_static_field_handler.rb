require_relative 'abstract_command_handler'

class SetStaticFieldHandler < AbstractCommandHandler
  def initialize
    @required_parameters_count = 3
  end

  def process(command)
    Command.new(RuntimeName::RUBY, CommandType::VALUE, [set_static_field(command)])
  end

  def set_static_field(command)
    begin
      if command.payload.length != @required_parameters_count
        raise "Set static field parameters mismatch"
      end

      merged_value = '@@' + command.payload[1]
      command.payload[0].class_variable_set(merged_value, command.payload[2])
    rescue Exception => e
      return e
    end
  end
end