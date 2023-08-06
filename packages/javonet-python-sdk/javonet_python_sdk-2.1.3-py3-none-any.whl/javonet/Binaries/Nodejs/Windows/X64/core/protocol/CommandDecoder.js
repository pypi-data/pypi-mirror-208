const Command = require("../../utils/Command")
const Type = require("../../utils/Type")
const StringEncodingMode = require("../../utils/StringEncodingMode")
const util = require('util')

class CommandDecoder {
    constructor(byteArray) {
        this.buffer = byteArray
        this.command = new Command(
            byteArray[0],
            byteArray[10],
            []
        )
        this.position = 11
    }

    decode() {
        while (!this.#isAtEnd()) {
            this.command = this.command.addArgToPayload((this.#readObject(this.buffer[this.position])))
        }
        return this.command
    }

    #isAtEnd = function () {
        return this.position === this.buffer.length
    }

    #readObject = function (typeNum) {
        let type = Object.entries(Type).find(entry => entry[1] === typeNum)[0]
        switch (type) {
            case 'JAVONET_COMMAND':
                return this.#readCommand()
            case 'JAVONET_STRING':
                return this.#readString()
            case 'JAVONET_INTEGER':
                return this.#readInt32()
            case 'JAVONET_BOOLEAN':
                return this.#readBoolean();
            case 'JAVONET_FLOAT':
                return this.#readFloat();
            case 'JAVONET_BYTE':
                return this.#readByte();
            case 'JAVONET_CHAR':
                return this.#readChar();
            case 'JAVONET_LONG_LONG':
                throw 'Type long long not supported in JavaScript'
            case 'JAVONET_DOUBLE':
                return this.#readDouble();
            case 'JAVONET_UNSIGNED_LONG_LONG':
                return 'Type unsigned long long not supported in JavaScript'
            case 'JAVONET_UNSIGNED_INTEGER':
                return 'Type unsigned integer not supported in JavaScript'
            default:
                throw 'Unknown type - not supported in JavaScript'
        }
    }

    #readCommand = function () {
        let p = this.position
        let numberOfElementsInPayload = this.#readInt32Value(p + 1)
        let runtime = this.buffer[p + 5]
        let type = this.buffer[p + 6]
        this.position += 7
        let command = new Command(runtime, type, [])

        return this.#readCommandRecursively(numberOfElementsInPayload, command)
    }

    #readCommandRecursively = function (numberOfElementsInPayloadLeft, cmd) {
        if (numberOfElementsInPayloadLeft === 0) return cmd
        let p = this.position
        cmd = cmd.addArgToPayload(this.#readObject(this.buffer[p]))
        return this.#readCommandRecursively(numberOfElementsInPayloadLeft - 1, cmd)
    }

    #readString = function() {
        let p = this.position
        let stringEncodingMode = this.buffer[p+1]
        let size = this.#readInt32Value(p + 2)
        let firstChar = p + 6
        switch (stringEncodingMode) {
            case StringEncodingMode.ASCII:
                let charArrayASCII = this.buffer.slice(firstChar, firstChar + size)
                this.position += size + 6
                return String.fromCharCode(...charArrayASCII)
            case StringEncodingMode.UTF8:
                let charArrayUTF8 = this.buffer.slice(firstChar, firstChar + size)
                this.position += size + 6
                let decoder = new util.TextDecoder('UTF-8');
                return decoder.decode(new Uint8Array(charArrayUTF8))
            case StringEncodingMode.UTF16:
                let str = "";
                let newBuffer = new Uint8Array(this.buffer.length)
                for ( let i=0;i<this.buffer.length;i++) {
                    newBuffer[i] = this.buffer[i]
                }
                for ( let i=0;i<size;i=i+2 ) {
                    str += String.fromCharCode(newBuffer[firstChar + i] + 256 * newBuffer[firstChar + i + 1])
                }
                this.position += size + 6
                return str;
            case StringEncodingMode.UTF32:
                throw "Type utf32-encoded string not supported in JavaScript"
            default:
                throw "Unknown string encoding - not supported in JavaScript";
        }
    }

    #readInt32Value = function (p) {
        return (
            (this.buffer[p] & 0xFF)
            | ((this.buffer[p + 1] & 0xFF) << 8)
            | ((this.buffer[p + 2] & 0xFF) << 16)
            | ((this.buffer[p + 3] & 0xFF) << 24)
        )
    }

    #readInt32 = function () {
        let p = this.position += 2
        this.position += 4

        return (
            (this.buffer[p] & 0xFF)
            | ((this.buffer[p + 1] & 0xFF) << 8)
            | ((this.buffer[p + 2] & 0xFF) << 16)
            | ((this.buffer[p + 3] & 0xFF) << 24)
        )
    }

    #readByte = function () {
        let p = this.position += 2
        this.position += 1
        return (
            (this.buffer[p])
        )
    }

    #readChar = function () {
        let p = this.position += 2
        this.position += 1
        return String.fromCharCode(this.buffer[p])
    }

    #readBoolean = function () {
        let p = this.position += 2
        this.position += 1
        if (this.buffer[p] == 0 )
        {
            return false
        } else {
            return true
        }
    }

    #readFloat = function () {
        let p = this.position += 2
        this.position += 4
        const buffer = Buffer.from(this.buffer.slice(p, p+4));
        return buffer.readFloatLE(0)
    }

    #readDouble = function () {
        let p = this.position +=2
        this.position += 8
        const buffer = Buffer.from(this.buffer.slice(p, p+8));
        return buffer.readDoubleLE(0)
    }

}

module.exports = CommandDecoder