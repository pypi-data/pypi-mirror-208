import traceback

from javonet.core.handler.AbstractHandler import AbstractHandler
from javonet.core.handler.CommandHandler.ValueHandler import ValueHandler
from javonet.core.handler.CommandHandler.LoadLibraryHandler import LoadLibraryHandler
from javonet.core.handler.CommandHandler.InvokeStaticMethodHandler import InvokeStaticMethodHandler
from javonet.core.handler.CommandHandler.SetStaticFieldHandler import SetStaticFieldHandler
from javonet.core.handler.CommandHandler.CreateClassInstanceHandler import CreateClassInstanceHandler
from javonet.core.handler.CommandHandler.GetStaticFieldHandler import GetStaticFieldHandler
from javonet.core.handler.CommandHandler.ResolveInstanceHandler import ResolveInstanceHandler
from javonet.core.handler.CommandHandler.GetTypeHandler import GetTypeHandler
from javonet.core.handler.CommandHandler.InvokeInstanceMethodHandler import InvokeInstanceMethodHandler
from javonet.core.handler.CommandHandler.CastingHandler import CastingHandler
from javonet.core.handler.CommandHandler.GetInstanceFieldHandler import GetInstanceFieldHandler
from javonet.core.handler.CommandHandler.DestructReferenceHandler import DestructReferenceHandler
from javonet.core.handler.CommandHandler.ArrayGetItemHandler import ArrayGetItemHandler
from javonet.core.handler.CommandHandler.ArrayGetSizeHandler import ArrayGetSizeHandler
from javonet.core.handler.CommandHandler.ArrayGetRankHandler import ArrayGetRankHandler
from javonet.core.handler.CommandHandler.ArraySetItemHandler import ArraySetItemHandler
from javonet.core.handler.CommandHandler.ArrayHandler import ArrayHandler

from javonet.core.handler.HandlerDictionary import handler_dict
from javonet.core.handler.ReferencesCache import ReferencesCache
from javonet.core.exception.ExceptionSerializer import ExceptionSerializer
from javonet.utils.CommandType import CommandType
from javonet.utils.Command import Command


class Handler(AbstractHandler):

    def __init__(self):
        value_handler = ValueHandler()
        load_library_handler = LoadLibraryHandler()
        invoke_static_method_handler = InvokeStaticMethodHandler()
        set_static_field_handler = SetStaticFieldHandler()
        create_class_instance_handler = CreateClassInstanceHandler()
        get_static_field_handler = GetStaticFieldHandler()
        resolve_instance_handler = ResolveInstanceHandler()
        get_type_handler = GetTypeHandler()
        invoke_instance_method_handler = InvokeInstanceMethodHandler()
        casting_handler = CastingHandler()
        get_instance_field_handler = GetInstanceFieldHandler()
        destruct_reference_handler = DestructReferenceHandler()
        array_get_item_handler = ArrayGetItemHandler()
        array_get_size_handler = ArrayGetSizeHandler()
        array_get_rank_handler = ArrayGetRankHandler()
        array_set_item_handler = ArraySetItemHandler()
        array_handler = ArrayHandler()

        handler_dict[CommandType.Value] = value_handler
        handler_dict[CommandType.LoadLibrary] = load_library_handler
        handler_dict[CommandType.InvokeStaticMethod] = invoke_static_method_handler
        handler_dict[CommandType.SetStaticField] = set_static_field_handler
        handler_dict[CommandType.CreateClassInstance] = create_class_instance_handler
        handler_dict[CommandType.GetStaticField] = get_static_field_handler
        handler_dict[CommandType.Reference] = resolve_instance_handler
        handler_dict[CommandType.GetType] = get_type_handler
        handler_dict[CommandType.InvokeInstanceMethod] = invoke_instance_method_handler
        handler_dict[CommandType.Cast] = casting_handler
        handler_dict[CommandType.GetInstanceField] = get_instance_field_handler
        handler_dict[CommandType.DestructReference] = destruct_reference_handler
        handler_dict[CommandType.ArrayGetItem] = array_get_item_handler
        handler_dict[CommandType.ArrayGetSize] = array_get_size_handler
        handler_dict[CommandType.ArrayGetRank] = array_get_rank_handler
        handler_dict[CommandType.ArraySetItem] = array_set_item_handler
        handler_dict[CommandType.Array] = array_handler

    def handle_command(self, command):
        try:
            response = handler_dict.get(command.command_type).handle_command(command)
            return self.__parse_response(response, command.runtime_name)
        except Exception as e:

            return ExceptionSerializer.serialize_exception(e, command)

    def __parse_response(self, response, runtime_name):
        if self.__is_response_simple_type(response):
            return Command.create_response(response, runtime_name)
        else:
            reference_cache = ReferencesCache()
            guid = reference_cache.cache_reference(response)
            return Command.create_reference(guid, runtime_name)

    @staticmethod
    def __is_response_simple_type(response):
        return isinstance(response, (int, float, bool, str))

    @staticmethod
    def __is_response_array(response):
        return isinstance(response, list);
