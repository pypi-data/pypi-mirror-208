from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.front.pos_terminal import PosTerminal
from quick_resto_API.quick_resto_objects.modules.front.virtual_pos_terminal import VirtualPosTerminal
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class PosTerminalOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "front.terminals.pos"

    def get_list_of_terminal(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[PosTerminal|VirtualPosTerminal]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[PosTerminal|VirtualPosTerminal] = list()

        for object in json_response:
            if 'PosTerminal' in object['className']:
                result.append(PosTerminal(**object))
            elif 'VirtualPosTerminal' in object['className']:
                result.append(VirtualPosTerminal(**object))

        return result

    def get_tree_of_terminal(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[PosTerminal|VirtualPosTerminal]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[PosTerminal|VirtualPosTerminal] = list()

        for object in json_response:
            if 'PosTerminal' in object['className']:
                result.append(PosTerminal(**object))
            elif 'VirtualPosTerminal' in object['className']:
                result.append(VirtualPosTerminal(**object))

        return result

    def get_terminal(self, objectId: int, objectRid: int = None) -> PosTerminal|VirtualPosTerminal:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        if 'PosTerminal' in json_response['className']:
            return PosTerminal(**json_response)
        else:
            return VirtualPosTerminal(**json_response)

    def get_terminal_with_subobjects(self, objectId: int, objectRid: int = None) -> PosTerminal|VirtualPosTerminal:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        if 'PosTerminal' in json_response['className']:
            return PosTerminal(**json_response)
        else:
            return VirtualPosTerminal(**json_response)

    def create_terminal(self, object: PosTerminal|VirtualPosTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PosTerminal|VirtualPosTerminal:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'PosTerminal' in json_response['className']:
            return PosTerminal(**json_response)
        else:
            return VirtualPosTerminal(**json_response)

    def update_terminal(self, object: PosTerminal|VirtualPosTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PosTerminal|VirtualPosTerminal:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'PosTerminal' in json_response['className']:
            return PosTerminal(**json_response)
        else:
            return VirtualPosTerminal(**json_response)

    def remove_terminal(self, object: PosTerminal|VirtualPosTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PosTerminal|VirtualPosTerminal:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'PosTerminal' in json_response['className']:
            return PosTerminal(**json_response)
        else:
            return VirtualPosTerminal(**json_response)

    def recover_terminal(self, object: PosTerminal|VirtualPosTerminal,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PosTerminal|VirtualPosTerminal:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'PosTerminal' in json_response['className']:
            return PosTerminal(**json_response)
        else:
            return VirtualPosTerminal(**json_response)