from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.front.preorder_info import PreorderInfo
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class PreorderInfoOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "front.preorders"

    def get_list_of_preorder_info(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[PreorderInfo]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[PreorderInfo] = list()

        for object in json_response:
            result.append(PreorderInfo(**object))

        return result

    def get_tree_of_preorder_info(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[PreorderInfo]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[PreorderInfo] = list()

        for object in json_response:
            result.append(PreorderInfo(**object))

        return result

    def get_preorder_info(self, objectId: int, objectRid: int = None) -> PreorderInfo:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return PreorderInfo(**json_response)

    def get_preorder_info_with_subobjects(self, objectId: int, objectRid: int = None) -> PreorderInfo:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return PreorderInfo(**json_response)

    def create_preorder_info(self, object: PreorderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PreorderInfo:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PreorderInfo(**json_response)

    def update_preorder_info(self, object: PreorderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PreorderInfo:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PreorderInfo(**json_response)

    def remove_preorder_info(self, object: PreorderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PreorderInfo:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PreorderInfo(**json_response)

    def recover_preorder_info(self, object: PreorderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PreorderInfo:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PreorderInfo(**json_response)