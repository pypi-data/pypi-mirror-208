from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.exchange_invoice import ExchangeInvoice
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class ExchangeInvoiceOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.documents.exchange"

    def get_list_of_exchange_invoice(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[ExchangeInvoice]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[ExchangeInvoice] = list()

        for object in json_response:
            result.append(ExchangeInvoice(**object))

        return result

    def get_tree_of_exchange_invoice(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[ExchangeInvoice]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[ExchangeInvoice] = list()

        for object in json_response:
            result.append(ExchangeInvoice(**object))

        return result

    def get_exchange_invoice(self, objectId: int, objectRid: int = None) -> ExchangeInvoice:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return ExchangeInvoice(**json_response)

    def get_exchange_invoice_with_subobjects(self, objectId: int, objectRid: int = None) -> ExchangeInvoice:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return ExchangeInvoice(**json_response)

    def create_exchange_invoice(self, object: ExchangeInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ExchangeInvoice:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ExchangeInvoice(**json_response)

    def update_exchange_invoice(self, object: ExchangeInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ExchangeInvoice:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ExchangeInvoice(**json_response)

    def remove_exchange_invoice(self, object: ExchangeInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ExchangeInvoice:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ExchangeInvoice(**json_response)

    def recover_exchange_invoice(self, object: ExchangeInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> ExchangeInvoice:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return ExchangeInvoice(**json_response)