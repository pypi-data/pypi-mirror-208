const { Handler } = require('../handler/Handler')
const CommandEncoder = require('../protocol/CommandEncoder')
const CommandDecoder = require('../protocol/CommandDecoder')
const Runtime = require("../../utils/RuntimeName");

let Transmitter

class Interpreter {
    handler = new Handler()

    execute(command, connectionType, tcpAddress) {
        let commandEncoder = new CommandEncoder()
        let byteMessage = commandEncoder.encode(command,connectionType, tcpAddress)
        let responseByteArray

        if (command.runtimeName === Runtime.Nodejs)
        {
            return this.process(byteMessage)
        }
        else {
            // lazy transmitter loading
            if (!Transmitter) {
                Transmitter = require('../transmitter/Transmitter')
            }
            responseByteArray = Transmitter.sendCommand(byteMessage)
            return new CommandDecoder(responseByteArray).decode()
        }
    }

    process(byteArray) {
        let decoder = new CommandDecoder(byteArray)
        let command = decoder.decode()
        return this.handler.handleCommand(command)
    }
}

module.exports = Interpreter
