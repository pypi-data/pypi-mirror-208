const Command = require('./Command')
const CommandType = require('./CommandType')
class ExplicitCast {
  static cast(value, targetType) {
      return new Command(
            100,
            CommandType.Cast,
            [
                value,
                new Command(
                    100,
                    CommandType.GetType,
                    [targetType]
                )
            ]
      )
  }
}

module.exports = ExplicitCast