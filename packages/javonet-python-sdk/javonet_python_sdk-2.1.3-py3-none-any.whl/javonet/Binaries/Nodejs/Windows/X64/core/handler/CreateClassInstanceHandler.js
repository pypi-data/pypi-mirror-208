const AbstractHandler = require("./AbstractHandler");

class CreateClassInstanceHandler extends AbstractHandler {
    process(command) {
        try {
            let clazz = command.payload[0]
            let methodArguments = command.payload.slice(1)
            return new clazz(...methodArguments)
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new CreateClassInstanceHandler()