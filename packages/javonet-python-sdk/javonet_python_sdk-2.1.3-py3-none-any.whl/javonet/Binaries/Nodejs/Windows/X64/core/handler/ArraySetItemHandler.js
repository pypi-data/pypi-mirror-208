const AbstractHandler = require("./AbstractHandler")


class ArraySetItemHandler extends AbstractHandler {
    process(command) {
        try {
            let array = command.payload[0]
            let value = command.payload[1]
            let indexes = command.payload.slice(2)
            array[indexes] = value
            return 0;
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new ArraySetItemHandler()