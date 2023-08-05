from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.semi_product import SemiProduct
from quick_resto_API.quick_resto_objects.modules.warehouse.store_category import StoreCategory
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class SemiProductOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.nomenclature.semiproduct"

    def get_list_of_semi_product(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[SemiProduct|StoreCategory]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[SemiProduct|StoreCategory] = list()

        for object in json_response:
            if 'StoreCategory' in object['className']:
                result.append(StoreCategory(**object))
            elif 'SemiProduct' in object['className']:
                result.append(SemiProduct(**object))

        return result

    def get_tree_of_semi_product(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[SemiProduct|StoreCategory]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[SemiProduct|StoreCategory] = list()

        for object in json_response:
            if 'StoreCategory' in object['className']:
                result.append(StoreCategory(**object))
            elif 'SemiProduct' in object['className']:
                result.append(SemiProduct(**object))

        return result

    def get_semi_product_or_store_category(self, objectId: int, objectRid: int = None) -> SemiProduct | StoreCategory:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        if 'StoreCategory' in json_response['className']:
            return StoreCategory(**json_response)
        else:
            return SemiProduct(**json_response)

    def get_semi_product_or_store_category_with_subobjects(self, objectId: int, objectRid: int = None) -> SemiProduct | StoreCategory:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        if 'StoreCategory' in json_response['className']:
            return StoreCategory(**json_response)
        else:
            return SemiProduct(**json_response)

    def create_semi_product_or_store_category(self, object: SemiProduct | StoreCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SemiProduct | StoreCategory:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'StoreCategory' in json_response['className']:
            return StoreCategory(**json_response)
        else:
            return SemiProduct(**json_response)

    def update_semi_product_or_store_category(self, object: SemiProduct | StoreCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SemiProduct | StoreCategory:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'StoreCategory' in json_response['className']:
            return StoreCategory(**json_response)
        else:
            return SemiProduct(**json_response)

    def remove_semi_product_or_store_category(self, object: SemiProduct | StoreCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SemiProduct | StoreCategory:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'StoreCategory' in json_response['className']:
            return StoreCategory(**json_response)
        else:
            return SemiProduct(**json_response)

    def recover_semi_product_or_store_category(self, object: SemiProduct | StoreCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SemiProduct | StoreCategory:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'StoreCategory' in json_response['className']:
            return StoreCategory(**json_response)
        else:
            return SemiProduct(**json_response)