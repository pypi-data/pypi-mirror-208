const AbstractHandler =  require("./AbstractHandler")


class ValueHandler extends AbstractHandler {
    process(command) {
        const {payload} = command
        return payload[0]
    }
}

module.exports = new ValueHandler()