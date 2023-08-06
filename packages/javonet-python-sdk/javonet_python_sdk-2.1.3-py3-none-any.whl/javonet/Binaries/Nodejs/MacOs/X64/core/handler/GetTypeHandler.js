const AbstractHandler = require("./AbstractHandler");

class GetTypeHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        try {
            const {payload} = command
            let typeName = payload[0]
            typeName = typeName.replace(".js", "")
            let type = global[typeName]
            if (type == undefined) {
                throw `Cannot load ${typeName}`
            } else {
                return type
            }
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }

    }
}

module.exports = new GetTypeHandler()