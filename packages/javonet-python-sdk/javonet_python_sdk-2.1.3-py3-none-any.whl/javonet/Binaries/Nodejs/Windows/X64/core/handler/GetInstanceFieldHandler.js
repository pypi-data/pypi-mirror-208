const AbstractHandler = require("./AbstractHandler");

class GetInstanceFieldHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        try {
            const {payload} = command
            let instance = payload[0]
            let field = payload[1]

            return instance[field]
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new GetInstanceFieldHandler()