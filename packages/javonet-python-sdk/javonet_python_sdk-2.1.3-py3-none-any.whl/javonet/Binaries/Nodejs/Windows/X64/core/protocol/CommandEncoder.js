const Command = require("../../utils/Command")
const TypeEncoder = require('./TypeEncoder')
const ConnectionType = require("../../utils/ConnectionType");
const Runtime = require('../../utils/RuntimeName')

class CommandEncoder {
    buffer = new Int8Array(2)
    encodedTcp;

    encode(command, connectionType, tcpConnectionData, runtimeVersion = 0) {
        let deque = [command]
        this.buffer[0] = command.runtimeName
        this.buffer[1] = runtimeVersion
        this.#insertIntoBuffer(this.#encodeTcpConnection(connectionType, tcpConnectionData))
        this.#insertIntoBuffer(new Int8Array([Runtime.Nodejs, command.commandType]))
        return this.#encodeRecursively(deque)
    }

    #encodeTcpConnection = function(connectionType, tcpConnectionData) {
        this.encodedTcp = new Int8Array(7)
        if (ConnectionType.IN_MEMORY === connectionType) {
            this.encodedTcp[0] = ConnectionType.IN_MEMORY.valueOf()
            for (let i = 1; i < this.encodedTcp.length; i++) {
                this.encodedTcp[i] = 0
            }
            return this.encodedTcp
        }
        else if (ConnectionType.TCP === connectionType) {
            this.encodedTcp[0] = ConnectionType.TCP.valueOf()
            let port = tcpConnectionData.get_port();
            let hostname = tcpConnectionData.get_hostname();
            let split_hostname = hostname.split(".");

            for (let i = 0; i < split_hostname.length; i++) {
                this.encodedTcp[i + 1] = split_hostname[i]
            }
            this.encodedTcp.push(new Int8Array.of(
                port,
                (port >>> 8 & 0xFF)))
            return this.encodedTcp
        }
    }

    #encodeRecursively = function(deque) {
        if (deque.length === 0) return this.buffer;
        let cmd = deque.pop()
        deque.push(cmd.dropFirstPayloadArg())
        if (cmd.payload.length > 0) {
            if (cmd.payload[0] instanceof Command) {
                let innerCommand = cmd.payload[0]
                this.#insertIntoBuffer(TypeEncoder.encodeCommand(innerCommand))
                deque.push(innerCommand)
            } else {
                let result = TypeEncoder.encodePrimitive(cmd.payload[0])
                this.#insertIntoBuffer(result)
            }
            return this.#encodeRecursively(deque)
        } else {
            deque.pop()
        }
        return this.#encodeRecursively(deque)
    }

    #insertIntoBuffer = function(arg) {
        let newArray = new Int8Array(this.buffer.length + arg.length)
        newArray.set(this.buffer, 0)
        newArray.set(arg, this.buffer.length)
        this.buffer = newArray
    }
}

module.exports = CommandEncoder