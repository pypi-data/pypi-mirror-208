from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.crm.fixed_discount import FixedDiscount
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class FixedDiscountOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "crm.settings.fixed"

    def get_list_of_fixed_discount(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[FixedDiscount]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[FixedDiscount] = list()

        for object in json_response:
            result.append(FixedDiscount(**object))

        return result

    def get_tree_of_fixed_discount(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[FixedDiscount]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[FixedDiscount] = list()

        for object in json_response:
            result.append(FixedDiscount(**object))

        return result

    def get_fixed_discount(self, objectId: int, objectRid: int = None) -> FixedDiscount:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return FixedDiscount(**json_response)

    def get_fixed_discount_with_subobjects(self, objectId: int, objectRid: int = None) -> FixedDiscount:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return FixedDiscount(**json_response)

    def create_fixed_discount(self, object: FixedDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> FixedDiscount:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return FixedDiscount(**json_response)

    def update_fixed_discount(self, object: FixedDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> FixedDiscount:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return FixedDiscount(**json_response)

    def remove_fixed_discount(self, object: FixedDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> FixedDiscount:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return FixedDiscount(**json_response)

    def recover_fixed_discount(self, object: FixedDiscount,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> FixedDiscount:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return FixedDiscount(**json_response)