require_relative 'abstract_command_handler'

class ArrayGetItemHandler < AbstractCommandHandler
  def process(command)
    begin
      array = command.payload[0]
      index = command.payload[1,]
      return array[index]
    rescue Exception => e
      return e
    end
  end
end