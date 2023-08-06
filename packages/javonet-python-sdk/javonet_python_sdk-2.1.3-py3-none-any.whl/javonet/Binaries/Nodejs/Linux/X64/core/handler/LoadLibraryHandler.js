const AbstractHandler = require('./AbstractHandler')

class LoadLibraryHandler extends AbstractHandler {
    constructor() {
        super()
    }

    process(command) {
        let {payload} = command
        let [lib] = payload
        let pathArray = lib.split(/[/\\]/)
        let libraryName = pathArray.length > 1 ? pathArray[pathArray.length - 1] : pathArray[0]
        libraryName = libraryName.replace('.js', '')
        try {
            global[libraryName] = require(lib)
        } catch (error) {
            try {
                global[libraryName] = require(`${process.cwd()}/${lib}`)
            } catch {
                return this.process_stack_trace(error, this.constructor.name)
            }
        }
        return 0
    }
}

module.exports = new LoadLibraryHandler()
