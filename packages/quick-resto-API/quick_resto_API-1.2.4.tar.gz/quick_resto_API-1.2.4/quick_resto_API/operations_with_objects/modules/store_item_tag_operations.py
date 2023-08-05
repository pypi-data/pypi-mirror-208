from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.core.store_item_tag import StoreItemTag
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class StoreItemTagOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "core.dictionaries.storeitemtag"

    def get_list_of_store_item_tag(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[StoreItemTag]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[StoreItemTag] = list()

        for object in json_response:
            result.append(StoreItemTag(**object))

        return result

    def get_tree_of_store_item_tag(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[StoreItemTag]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[StoreItemTag] = list()

        for object in json_response:
            result.append(StoreItemTag(**object))

        return result

    def get_store_item_tag(self, objectId: int, objectRid: int = None) -> StoreItemTag:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return StoreItemTag(**json_response)

    def get_store_item_tag_with_subobjects(self, objectId: int, objectRid: int = None) -> StoreItemTag:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return StoreItemTag(**json_response)

    def create_store_item_tag(self, object: StoreItemTag,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> StoreItemTag:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return StoreItemTag(**json_response)

    def update_store_item_tag(self, object: StoreItemTag,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> StoreItemTag:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return StoreItemTag(**json_response)

    def remove_store_item_tag(self, object: StoreItemTag,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> StoreItemTag:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return StoreItemTag(**json_response)

    def recover_store_item_tag(self, object: StoreItemTag,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> StoreItemTag:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return StoreItemTag(**json_response)