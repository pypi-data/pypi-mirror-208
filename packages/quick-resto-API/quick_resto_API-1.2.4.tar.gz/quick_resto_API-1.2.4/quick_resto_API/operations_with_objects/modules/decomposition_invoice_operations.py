from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.decomposition_invoice import DecompositionInvoice
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class DecompositionInvoiceOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.documents.decomposition"

    def get_list_of_decomposition_invoice(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[DecompositionInvoice]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[DecompositionInvoice] = list()

        for object in json_response:
            result.append(DecompositionInvoice(**object))

        return result

    def get_tree_of_decomposition_invoice(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[DecompositionInvoice]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[DecompositionInvoice] = list()

        for object in json_response:
            result.append(DecompositionInvoice(**object))

        return result

    def get_decomposition_invoice(self, objectId: int, objectRid: int = None) -> DecompositionInvoice:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return DecompositionInvoice(**json_response)

    def get_decomposition_invoice_with_subobjects(self, objectId: int, objectRid: int = None) -> DecompositionInvoice:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return DecompositionInvoice(**json_response)

    def create_decomposition_invoice(self, object: DecompositionInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> DecompositionInvoice:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return DecompositionInvoice(**json_response)

    def update_decomposition_invoice(self, object: DecompositionInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> DecompositionInvoice:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return DecompositionInvoice(**json_response)

    def remove_decomposition_invoice(self, object: DecompositionInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> DecompositionInvoice:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return DecompositionInvoice(**json_response)

    def recover_decomposition_invoice(self, object: DecompositionInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> DecompositionInvoice:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return DecompositionInvoice(**json_response)