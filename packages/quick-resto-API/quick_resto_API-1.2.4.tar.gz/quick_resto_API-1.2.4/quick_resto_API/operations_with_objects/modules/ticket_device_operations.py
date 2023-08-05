from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.front.ticket_device import TicketDevice
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class TicketDeviceOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "front.terminals.ticketdevices"

    def get_list_of_ticket_device(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[TicketDevice]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[TicketDevice] = list()

        for object in json_response:
            result.append(TicketDevice(**object))

        return result

    def get_tree_of_ticket_device(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[TicketDevice]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[TicketDevice] = list()

        for object in json_response:
            result.append(TicketDevice(**object))

        return result

    def get_ticket_device(self, objectId: int, objectRid: int = None) -> TicketDevice:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return TicketDevice(**json_response)

    def get_ticket_device_with_subobjects(self, objectId: int, objectRid: int = None) -> TicketDevice:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return TicketDevice(**json_response)

    def create_ticket_device(self, object: TicketDevice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> TicketDevice:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return TicketDevice(**json_response)

    def update_ticket_device(self, object: TicketDevice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> TicketDevice:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return TicketDevice(**json_response)

    def remove_ticket_device(self, object: TicketDevice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> TicketDevice:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return TicketDevice(**json_response)

    def recover_ticket_device(self, object: TicketDevice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> TicketDevice:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return TicketDevice(**json_response)