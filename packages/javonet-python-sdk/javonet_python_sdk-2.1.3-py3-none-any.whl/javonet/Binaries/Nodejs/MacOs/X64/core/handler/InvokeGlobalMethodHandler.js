const AbstractHandler = require("./AbstractHandler");

class InvokeGlobalMethodHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        try {
            const {payload} = command
            const splitted = payload[0].split(".")
            const args = payload.slice(1)
            let methodToInvoke

            for (let i = 0; i < splitted.length; i++) {
                methodToInvoke = !methodToInvoke ? global[splitted[i]] : methodToInvoke[splitted[i]]
            }
            return methodToInvoke(args)
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }

}

module.exports = new InvokeGlobalMethodHandler()