const Command = require('../../utils/Command')
const Type = require('../../utils/Type')
const StringEncodingMode = require('../../utils/StringEncodingMode')

const util = require('util');
let encoder = new util.TextEncoder();

class TypeEncoder {
    static encodePrimitive(obj) {
        if (obj instanceof Command) {
            return TypeEncoder.encodeCommand(obj)
        } else if (typeof (obj) === 'number' || obj instanceof Number) {
            if (Number.isInteger(obj)) {
                return TypeEncoder.encodeInt32(obj)
            } else {
                return TypeEncoder.encodeNumber(obj)
            }
        } else if (typeof (obj) === 'string' || obj instanceof String) {
            return TypeEncoder.encodeString(obj)
        } else if (typeof (obj) === 'boolean' || obj instanceof Boolean) {
            return TypeEncoder.encodeBoolean(obj)
        }
    }

    static encodeCommand(cmd) {
        const buffer = Buffer.alloc(7, cmd)
        buffer.writeInt8(Type.JAVONET_COMMAND, 0)
        buffer.fill(Buffer.from(this.encodeInt32Value(cmd.payload.length)), 1, 5)
        buffer.writeInt8(cmd.runtime, 5)
        buffer.writeInt8(cmd.commandType, 6)
        return Int8Array.from(buffer)
    }

    static encodeInt32Value(val) {
        return Int8Array.of(
            val,
            (val >>> 8 & 0xFF),
            (val >>> 16 & 0xFF),
            (val >>> 24 & 0xFF)
        )
    }

    static encodeString(val) {
        let bytes = encoder.encode(val)
        const buffer = Buffer.alloc(6 + bytes.length)
        buffer.writeInt8(Type.JAVONET_STRING, 0)
        buffer.writeInt8(StringEncodingMode.UTF8, 1)
        buffer.fill(Buffer.from(this.encodeInt32Value(bytes.length)), 2, 6)
        buffer.fill(Buffer.from(bytes), 6, 6 + bytes.length)
        return Int8Array.from(buffer)
    }

    static encodeNumber(val) {
        const buffer = Buffer.alloc(10)
        buffer.writeInt8(Type.JAVONET_DOUBLE, 0)
        buffer.writeInt8(8, 1)
        buffer.writeDoubleLE(val, 2)
        return Int8Array.from(buffer)
    }

    static encodeInt32(val) {
        const buffer = Buffer.alloc(6)
        buffer.writeInt8(Type.JAVONET_INTEGER, 0)
        buffer.writeInt8(4, 1)
        buffer.writeInt32LE(val, 2)
        return Int8Array.from(buffer)
    }

    static encodeBoolean(val) {
        return Int8Array.of(
            Type.JAVONET_BOOLEAN,
            1,
            val ? 1 : 0
        )
    }
}

module.exports = TypeEncoder