const wrapper = require('./TransmitterWrapper')

class Transmitter {

   static sendCommand(messageArray) {
        return wrapper.sendCommand(messageArray)
    }

    static #activate = function(email = "", licenceKey = "", proxyHost = "", proxyUserName="", proxyUserPassword="") {
        return wrapper.activate(email, licenceKey, proxyHost, proxyUserName, proxyUserPassword)
    }

    static activateWithLicenceFile() {
        return this.#activate()
    }

    static activateWithCredentials(email, licenceKey) {
        return this.#activate(email, licenceKey)
    }

    static activateWithCredentialsAndProxy(email, licenceKey, proxyHost, proxyUserName, proxyUserPassword) {
        return this.#activate(email, licenceKey, proxyHost, proxyUserName, proxyUserPassword)
    }
}

module.exports = Transmitter
