from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.front.raspberry_terminal import RaspberryTerminal
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class RaspberryTerminalOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "front.terminals.raspberry"

    def get_list_of_raspberry_terminal(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[RaspberryTerminal]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[RaspberryTerminal] = list()

        for object in json_response:
            result.append(RaspberryTerminal(**object))

        return result

    def get_tree_of_raspberry_terminal(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[RaspberryTerminal]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[RaspberryTerminal] = list()

        for object in json_response:
            result.append(RaspberryTerminal(**object))

        return result

    def get_raspberry_terminal(self, objectId: int, objectRid: int = None) -> RaspberryTerminal:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return RaspberryTerminal(**json_response)

    def get_raspberry_terminal_with_subobjects(self, objectId: int, objectRid: int = None) -> RaspberryTerminal:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return RaspberryTerminal(**json_response)

    def create_raspberry_terminal(self, object: RaspberryTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> RaspberryTerminal:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return RaspberryTerminal(**json_response)

    def update_raspberry_terminal(self, object: RaspberryTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> RaspberryTerminal:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return RaspberryTerminal(**json_response)

    def remove_raspberry_terminal(self, object: RaspberryTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> RaspberryTerminal:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return RaspberryTerminal(**json_response)

    def recover_raspberry_terminal(self, object: RaspberryTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> RaspberryTerminal:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return RaspberryTerminal(**json_response)