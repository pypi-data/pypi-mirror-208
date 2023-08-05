from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.cooking_place import CookingPlace
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class CookingPlaceOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.nomenclature.cooking_place"

    def get_list_of_cooking_place(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[CookingPlace]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[CookingPlace] = list()

        for object in json_response:
            result.append(CookingPlace(**object))

        return result

    def get_tree_of_cooking_place(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[CookingPlace]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[CookingPlace] = list()

        for object in json_response:
            result.append(CookingPlace(**object))

        return result

    def get_cooking_place(self, objectId: int, objectRid: int = None) -> CookingPlace:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return CookingPlace(**json_response)

    def get_cooking_place_with_subobjects(self, objectId: int, objectRid: int = None) -> CookingPlace:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return CookingPlace(**json_response)

    def create_cooking_place(self, object: CookingPlace,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> CookingPlace:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return CookingPlace(**json_response)

    def update_cooking_place(self, object: CookingPlace,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> CookingPlace:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return CookingPlace(**json_response)

    def remove_cooking_place(self, object: CookingPlace,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> CookingPlace:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return CookingPlace(**json_response)

    def recover_cooking_place(self, object: CookingPlace,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> CookingPlace:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return CookingPlace(**json_response)