const AbstractHandler = require("./AbstractHandler")


class ArrayGetSizeHandler extends AbstractHandler {
    process(command) {
        try {
            let array = command.payload[0]
            return array.length
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new ArrayGetSizeHandler()