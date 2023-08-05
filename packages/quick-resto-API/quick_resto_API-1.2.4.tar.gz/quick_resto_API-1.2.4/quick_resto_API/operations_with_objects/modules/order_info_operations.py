from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.front.order_info import OrderInfo
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class OrderInfoOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "front.orders"

    def get_list_of_order_info(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[OrderInfo]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[OrderInfo] = list()

        for object in json_response:
            result.append(OrderInfo(**object))

        return result

    def get_tree_of_order_info(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[OrderInfo]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[OrderInfo] = list()

        for object in json_response:
            result.append(OrderInfo(**object))

        return result

    def get_order_info(self, objectId: int, objectRid: int = None) -> OrderInfo:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return OrderInfo(**json_response)

    def get_order_info_with_subobjects(self, objectId: int, objectRid: int = None) -> OrderInfo:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return OrderInfo(**json_response)

    def create_order_info(self, object: OrderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OrderInfo:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OrderInfo(**json_response)

    def update_order_info(self, object: OrderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OrderInfo:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OrderInfo(**json_response)

    def remove_order_info(self, object: OrderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OrderInfo:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OrderInfo(**json_response)

    def recover_order_info(self, object: OrderInfo,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OrderInfo:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OrderInfo(**json_response)