const AbstractHandler = require('./AbstractHandler')

class SetStaticFieldHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        const { payload } = command
        let [obj, field, value] = payload        
        obj[field] = value
        return 0
    }
}

module.exports =  new SetStaticFieldHandler()