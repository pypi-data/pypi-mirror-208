from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.crm.scheduled_discount import ScheduledDiscount
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class ScheduledDiscountOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "crm.settings.scheduled"

    def get_list_of_scheduled_discount(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[ScheduledDiscount]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[ScheduledDiscount] = list()

        for object in json_response:
            result.append(ScheduledDiscount(**object))

        return result

    def get_tree_of_scheduled_discount(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[ScheduledDiscount]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[ScheduledDiscount] = list()

        for object in json_response:
            result.append(ScheduledDiscount(**object))

        return result

    def get_scheduled_discount(self, objectId: int, objectRid: int = None) -> ScheduledDiscount:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return ScheduledDiscount(**json_response)

    def get_scheduled_discount_with_subobjects(self, objectId: int, objectRid: int = None) -> ScheduledDiscount:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return ScheduledDiscount(**json_response)

    def create_scheduled_discount(self, object: ScheduledDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ScheduledDiscount:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ScheduledDiscount(**json_response)

    def update_scheduled_discount(self, object: ScheduledDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ScheduledDiscount:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ScheduledDiscount(**json_response)

    def remove_scheduled_discount(self, object: ScheduledDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ScheduledDiscount:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ScheduledDiscount(**json_response)

    def recover_scheduled_discount(self, object: ScheduledDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ScheduledDiscount:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ScheduledDiscount(**json_response)