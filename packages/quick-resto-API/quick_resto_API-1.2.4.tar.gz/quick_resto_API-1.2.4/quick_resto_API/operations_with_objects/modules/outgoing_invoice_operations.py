from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.outgoing_invoice import OutgoingInvoice
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class OutgoingInvoiceOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.documents.outgoing"

    def get_list_of_outgoing_invoice(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[OutgoingInvoice]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[OutgoingInvoice] = list()

        for object in json_response:
            result.append(OutgoingInvoice(**object))

        return result

    def get_tree_of_outgoing_invoice(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[OutgoingInvoice]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[OutgoingInvoice] = list()

        for object in json_response:
            result.append(OutgoingInvoice(**object))

        return result

    def get_outgoing_invoice(self, objectId: int, objectRid: int = None) -> OutgoingInvoice:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return OutgoingInvoice(**json_response)

    def get_outgoing_invoice_with_subobjects(self, objectId: int, objectRid: int = None) -> OutgoingInvoice:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return OutgoingInvoice(**json_response)

    def create_outgoing_invoice(self, object: OutgoingInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OutgoingInvoice:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OutgoingInvoice(**json_response)

    def update_outgoing_invoice(self, object: OutgoingInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OutgoingInvoice:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OutgoingInvoice(**json_response)

    def remove_outgoing_invoice(self, object: OutgoingInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OutgoingInvoice:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OutgoingInvoice(**json_response)

    def recover_outgoing_invoice(self, object: OutgoingInvoice,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> OutgoingInvoice:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return OutgoingInvoice(**json_response)