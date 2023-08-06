class ExplicitCast
  def cast(value, target_type)
    Command.new(
      100,
      CommandType::CAST,
      [
        value,
        Command.new(
          100,
          CommandType::GET_TYPE,
          target_type
        )
      ]
    )
  end
end