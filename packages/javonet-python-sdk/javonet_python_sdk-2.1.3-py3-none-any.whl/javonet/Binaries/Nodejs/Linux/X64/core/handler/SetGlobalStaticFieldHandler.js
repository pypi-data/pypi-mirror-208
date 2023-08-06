const AbstractHandler = require("./AbstractHandler")

class SetGlobalStaticFieldHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        const { payload } = command
        const splitted = payload[0].split(".")
        const value = payload[1]
        let fieldToSet

        for(let i = 0; i < splitted.length; i++) {
            fieldToSet = !fieldToSet ? global[splitted[i]] : fieldToSet[splitted[i]]
        }
        fieldToSet = value
    }
}

module.exports = new SetGlobalStaticFieldHandler()