from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.single_category import SingleCategory
from quick_resto_API.quick_resto_objects.modules.warehouse.single_product import SingleProduct
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class SingleProductOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.nomenclature.singleproduct"
    
    def get_list_of_single_product(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[SingleCategory|SingleProduct]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[SingleCategory|SingleProduct] = list()

        for object in json_response:
            if 'SingleCategory' in object['className']:
                result.append(SingleCategory(**object))
            elif 'SingleProduct' in object['className']:
                result.append(SingleProduct(**object))

        return result

    def get_tree_of_single_product(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[SingleCategory|SingleProduct]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[SingleCategory|SingleProduct] = list()

        for object in json_response:
            if 'SingleCategory' in object['className']:
                result.append(SingleCategory(**object))
            elif 'SingleProduct' in object['className']:
                result.append(SingleProduct(**object))

        return result

    def get_single_product_or_single_category(self, objectId: int, objectRid: int = None) -> SingleProduct | SingleCategory:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        if 'SingleCategory' in json_response['className']:
            return SingleCategory(**json_response)
        else:
            return SingleProduct(**json_response)

    def get_single_product_or_single_category_with_subobjects(self, objectId: int, objectRid: int = None) -> SingleProduct | SingleCategory:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        if 'SingleCategory' in json_response['className']:
            return SingleCategory(**json_response)
        else:
            return SingleProduct(**json_response)

    def create_single_product_or_single_category(self, object: SingleProduct | SingleCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SingleProduct | SingleCategory:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'SingleCategory' in json_response['className']:
            return SingleCategory(**json_response)
        else:
            return SingleProduct(**json_response)

    def update_single_product_or_single_category(self, object: SingleProduct | SingleCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SingleProduct | SingleCategory:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'SingleCategory' in json_response['className']:
            return SingleCategory(**json_response)
        else:
            return SingleProduct(**json_response)

    def remove_single_product_or_single_category(self, object: SingleProduct | SingleCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SingleProduct | SingleCategory:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'SingleCategory' in json_response['className']:
            return SingleCategory(**json_response)
        else:
            return SingleProduct(**json_response)

    def recover_single_product_or_single_category(self, object: SingleProduct | SingleCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> SingleProduct | SingleCategory:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'SingleCategory' in json_response['className']:
            return SingleCategory(**json_response)
        else:
            return SingleProduct(**json_response)