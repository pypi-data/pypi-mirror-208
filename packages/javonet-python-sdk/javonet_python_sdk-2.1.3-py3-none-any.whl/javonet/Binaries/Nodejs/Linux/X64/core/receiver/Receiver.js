const Interpreter = require('../interpreter/Interpreter')
const CommandEncoder = require('../protocol/CommandEncoder')
const interpreter = new Interpreter()

class Receiver {
    static sendCommand(byteArray) {
        let command = interpreter.process(byteArray)
        let commandEncoder = new CommandEncoder()
        return commandEncoder.encode(command, 0, 0)
    }
    static heartBeat(byteArray) {
        return Int8Array.from([49, 48])
    }
}

module.exports = Receiver
