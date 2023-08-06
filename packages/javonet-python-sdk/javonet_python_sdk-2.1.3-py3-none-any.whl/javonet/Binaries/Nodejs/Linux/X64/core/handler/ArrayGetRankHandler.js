const AbstractHandler = require("./AbstractHandler")


class ArrayGetRankHandler extends AbstractHandler {
    process(command) {
        try {
            throw new Error("ArrayGetRankHandler not implemented")
        } catch (error) {
            return this.process_stack_trace(error, this.constructor.name)
        }
    }
}

module.exports = new ArrayGetRankHandler()