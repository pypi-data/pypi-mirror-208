let library;

class TransmitterWrapper {
    static initialize() {
        if (process.platform === "win32")
            library = require(`${require('path').resolve(__dirname, '../../../')}/build/Release/JavonetNodejsRuntimeAddon.node`)
        else if (process.platform === "darwin")
            library = require(`${require('path').resolve(__dirname, '../../../')}/build/Release/JavonetNodejsRuntimeAddon.node`)
        else
            library = require(`${require('path').resolve(__dirname, '../../../')}/build/Release/JavonetNodejsRuntimeAddon.node`)
        let binariesRootPath = String(`${require('path').resolve(__dirname, '../../../')}`)
        return library.initializeTransmitter(binariesRootPath)
    }

    static activate(email, licenceKey, proxyHost, proxyUserName, proxyUserPassword) {
        this.initialize()
        return library.activate(email, licenceKey, proxyHost, proxyUserName, proxyUserPassword)
    }

    static sendCommand(messageArray) {
        return library.sendCommand(messageArray)
    }
}

module.exports = TransmitterWrapper
