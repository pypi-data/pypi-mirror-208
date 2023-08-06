const AbstractHandler = require("./AbstractHandler")

class GetGlobalStaticFieldHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        try {
            const {payload} = command
            const splitted = payload[0].split(".")
            let fieldToGet

            for (let i = 0; i < splitted.length; i++) {
                fieldToGet = !fieldToGet ? global[splitted[i]] : fieldToGet[splitted[i]]
            }
            return fieldToGet

        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new GetGlobalStaticFieldHandler()