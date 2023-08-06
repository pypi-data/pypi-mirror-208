require_relative 'abstract_command_handler'

class ArrayGetRankHandler < AbstractCommandHandler
  def process(command)
    begin
      raise "ArrayGetRankHandler not implemented"
    rescue Exception => e
      return e
    end
  end
end