const AbstractHandler = require("./AbstractHandler")


class ArrayGetItemHandler extends AbstractHandler {
    process(command) {
        try {
            let array = command.payload[0]
            let indexes = command.payload.slice(1)
            return array[indexes]
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new ArrayGetItemHandler()