const ExceptionType = require("../../utils/ExceptionType");


class ExceptionThrower {

    static throwException(commandException) {
        let javonetStackCommand = commandException.payload[1];
        let exceptionName = commandException.payload[2];
        let exceptionMessage =  commandException.payload[3];

        let stackTraceClasses = commandException.payload[4];
        let stackTraceMethods = commandException.payload[5];
        let stackTraceLines = commandException.payload[6];
        let stackTraceFiles = commandException.payload[7];

        let exceptionType = commandException.payload[0];

        switch (exceptionType) {
            case ExceptionType.EXCEPTION:
            case ExceptionType.IO_EXCEPTION:
            case ExceptionType.FILE_NOT_FOUND_EXCEPTION:
            case ExceptionType.RUNTIME_EXCEPTION:
            case ExceptionType.ARITHMETIC_EXCEPTION:
                let error = new Error()
                error.stack = this.serializeStack(stackTraceClasses, stackTraceMethods, stackTraceLines, stackTraceFiles)
                error.name = exceptionName
                error.message = exceptionMessage
                error.path = javonetStackCommand
                throw error
            case ExceptionType.ILLEGAL_ARGUMENT_EXCEPTION:
            case ExceptionType.NULL_POINTER_EXCEPTION:
                let typeError = new TypeError()
                typeError.stack = this.serializeStack(stackTraceClasses, stackTraceMethods, stackTraceLines, stackTraceFiles)
                typeError.name = exceptionName
                typeError.message = exceptionMessage
                typeError.path = javonetStackCommand
                throw typeError
            case ExceptionType.INDEX_OUT_OF_BOUNDS_EXCEPTION:
                let rangeError = new RangeError()
                rangeError.stack = this.serializeStack(stackTraceClasses, stackTraceMethods, stackTraceLines, stackTraceFiles)
                rangeError.name = exceptionName
                rangeError.message = exceptionMessage
                rangeError.path = javonetStackCommand
                throw rangeError
            default:
                let defaultError = new Error()
                defaultError.stack = this.serializeStack(stackTraceClasses, stackTraceMethods, stackTraceLines, stackTraceFiles)
                defaultError.name = exceptionName
                defaultError.message = exceptionMessage
                defaultError.path = javonetStackCommand
                throw defaultError
        }
    }

    static serializeStack(stackTraceClasses, stackTraceMethods, stackTraceLines, stackTraceFiles) {
        let stackTraceClassesArray = stackTraceClasses.split('|')
        let stackTraceMethodsArray = stackTraceMethods.split('|')
        let stackTraceLinesArray = stackTraceLines.split('|')
        let stackTraceFilesArray = stackTraceFiles.split('|')

        const stackFrames = [];


        for (let i = 0; i < stackTraceClassesArray.length; i++) {
            const frameString = `    at ${stackTraceClassesArray[i]}.${stackTraceMethodsArray[i]} (${stackTraceFilesArray[i]}:${stackTraceLinesArray[i]})`;
            stackFrames.push(frameString);
        }
        return stackFrames.join("\n")


    }
}
module.exports = ExceptionThrower