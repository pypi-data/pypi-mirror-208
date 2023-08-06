const CommandType = require('../../utils/CommandType')
const ValueHandler = require('./ValueHandler')
const LoadLibraryHandler = require('./LoadLibraryHandler')
const GetTypeHandler = require('./GetTypeHandler')
const InvokeStaticMethodHandler = require('./InvokeStaticMethodHandler')
const GetStaticFieldHandler = require('./GetStaticFieldHandler')
const SetStaticFieldHandler = require('./SetStaticFieldHandler')
const ResolveReferenceHandler = require('./ResolveReferenceHandler')
const CreateClassInstanceHandler = require('./CreateClassInstanceHandler')
const GetInstanceFieldHandler = require('./GetInstanceFieldHandler')
const InvokeInstanceMethodHandler = require('./InvokeInstanceMethodHandler')
const DestructReferenceHandler = require("./DestructReferenceHandler");
const CastHandler = require('./CastingHandler')
const InvokeGlobalMethodHandler = require('./InvokeGlobalMethodHandler')
const ArrayGetItemHandler = require('./ArrayGetItemHandler')
const ArrayGetSizeHandler = require('./ArrayGetSizeHandler')
const ArrayGetRankHandler = require('./ArrayGetRankHandler')
const ArraySetItemHandler = require('./ArraySetItemHandler')
const ArrayHandler = require('./ArrayHandler')


const ExceptionSerializer = require('../exception/ExceptionSerializer')

const ReferenceCache = require('./ReferencesCache')
const Command = require("../../utils/Command");

function isResponseSimpleType(response) {
    let type = typeof(response)
    return ['string', 'boolean', 'number'].includes(type)
}

function isResponseArray(response) {
    return response instanceof Array
}

function isResponseError(response) {
    return response instanceof Error
}

const handlers = {
    [CommandType.Value]: ValueHandler,
    [CommandType.LoadLibrary]: LoadLibraryHandler,
    [CommandType.InvokeStaticMethod]: InvokeStaticMethodHandler,
    [CommandType.GetType]: GetTypeHandler,
    [CommandType.GetStaticField]: GetStaticFieldHandler,
    [CommandType.SetStaticField]: SetStaticFieldHandler,
    [CommandType.CreateClassInstance]: CreateClassInstanceHandler,
    [CommandType.Reference]: ResolveReferenceHandler,
    [CommandType.Cast]: CastHandler,
    [CommandType.GetInstanceField]: GetInstanceFieldHandler,
    [CommandType.InvokeInstanceMethod]: InvokeInstanceMethodHandler,
    [CommandType.InvokeGlobalMethod]: InvokeGlobalMethodHandler,
    [CommandType.DestructReference]: DestructReferenceHandler,
    [CommandType.ArrayGetItem]: ArrayGetItemHandler,
    [CommandType.ArrayGetSize]: ArrayGetSizeHandler,
    [CommandType.ArrayGetRank]: ArrayGetRankHandler,
    [CommandType.ArraySetItem]: ArraySetItemHandler,
    [CommandType.Array]: ArrayHandler
}

class Handler {

    handleCommand(command) {
            let response = handlers[command.commandType].handleCommand(command)
            if(isResponseError(response)) {
                return ExceptionSerializer.serializeException(response, command)
            }
            else {
                return this.parseCommand(response, command.runtimeName)
            }
    }

    parseCommand(response, runtimeName) {
        if(isResponseSimpleType(response)) {
            return Command.createResponse(response, runtimeName)
        }
        else {
            let cache = ReferenceCache.getInstance()
            let uuid = cache.cacheReference(response)
            return Command.createReference(uuid, runtimeName)
        }
    }
}

module.exports.Handler = Handler
module.exports.handlers = handlers

