class TcpConnectionData {
    constructor(hostname, port) {
        this.hostname = hostname
        this.port = port
    }
    get_hostname() { return this.hostname }

    get_port() { return this.port }
}


module.exports = TcpConnectionData