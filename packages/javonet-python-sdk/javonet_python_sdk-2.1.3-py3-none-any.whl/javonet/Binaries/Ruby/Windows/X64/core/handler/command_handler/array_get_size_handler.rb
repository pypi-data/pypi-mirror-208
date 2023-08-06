require_relative 'abstract_command_handler'

class ArrayGetSizeHandler < AbstractCommandHandler
  def process(command)
    begin
      array = command.payload[0]
      return array.length()
    rescue Exception => e
      return e
    end
  end
end