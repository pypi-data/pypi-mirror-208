const AbstractHandler = require("./AbstractHandler");
const ReferencesCache = require("./ReferencesCache")

class DestructReferenceHandler extends AbstractHandler {

    constructor() {
        super()
    }

    process(command) {
        try {
            let cache = ReferencesCache.getInstance()
            return cache.deleteReference(command.payload[0])
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new DestructReferenceHandler()