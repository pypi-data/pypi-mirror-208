require_relative 'abstract_command_handler'

class ArraySetItemHandler < AbstractCommandHandler
  def process(command)
    begin
      array = command.payload[0]
      value = command.payload[1]
      index = command.payload[2,]
      array[index] = value
      return 0
    rescue Exception => e
      return e
    end
  end
end