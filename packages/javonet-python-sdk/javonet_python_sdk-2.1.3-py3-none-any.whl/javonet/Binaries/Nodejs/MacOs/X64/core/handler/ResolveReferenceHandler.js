const AbstractHandler = require("./AbstractHandler");
const ReferenceCache = require("./ReferencesCache")

class ResolveReferenceHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        return ReferenceCache.getInstance().resolveReference(command.payload[0])
    }
}

module.exports = new ResolveReferenceHandler()