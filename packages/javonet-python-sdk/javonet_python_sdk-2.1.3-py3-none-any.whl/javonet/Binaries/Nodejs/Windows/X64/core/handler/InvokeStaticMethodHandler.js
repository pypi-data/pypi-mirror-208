const AbstractHandler = require('./AbstractHandler')

class InvokeStaticMethodHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        try {
            const {payload} = command
            let type = payload[0]
            let methodName = payload[1]
            let args = payload.slice(2)
            return Reflect.apply(type[methodName], undefined, args)
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new InvokeStaticMethodHandler()
