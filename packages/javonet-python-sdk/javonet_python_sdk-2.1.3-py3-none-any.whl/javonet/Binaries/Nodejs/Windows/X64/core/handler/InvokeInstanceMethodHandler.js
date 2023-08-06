const AbstractHandler = require("./AbstractHandler");

class InvokeInstanceMethodHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        try {
            const {payload} = command
            let instance = payload[0]
            let methodName = payload[1]
            let args = payload.slice(2)
            return Reflect.apply(instance[methodName], undefined, args)
        }
        catch (error){
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new InvokeInstanceMethodHandler()