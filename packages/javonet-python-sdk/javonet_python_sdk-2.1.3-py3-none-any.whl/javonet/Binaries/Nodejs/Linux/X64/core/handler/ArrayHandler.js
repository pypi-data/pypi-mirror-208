const AbstractHandler = require("./AbstractHandler")


class ArrayHandler extends AbstractHandler {
    process(command) {
        try {
            let array = command.payload
            return array
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new ArrayHandler()