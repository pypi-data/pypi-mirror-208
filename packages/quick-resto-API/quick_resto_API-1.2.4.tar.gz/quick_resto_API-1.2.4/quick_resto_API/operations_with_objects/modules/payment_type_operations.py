from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.core.payment_types import PaymentType
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class PaymentTypeOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "core.dictionaries.paymenttypes"

    def get_list_of_payment_type(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[PaymentType]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[PaymentType] = list()

        for object in json_response:
            result.append(PaymentType(**object))

        return result

    def get_tree_of_payment_type(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[PaymentType]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[PaymentType] = list()

        for object in json_response:
            result.append(PaymentType(**object))

        return result

    def get_payment_type(self, objectId: int, objectRid: int = None) -> PaymentType:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return PaymentType(**json_response)

    def get_payment_type_with_subobjects(self, objectId: int, objectRid: int = None) -> PaymentType:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return PaymentType(**json_response)

    def create_payment_type(self, object: PaymentType,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PaymentType:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PaymentType(**json_response)

    def update_payment_type(self, object: PaymentType,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PaymentType:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PaymentType(**json_response)

    def remove_payment_type(self, object: PaymentType,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PaymentType:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PaymentType(**json_response)

    def recover_payment_type(self, object: PaymentType,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> PaymentType:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return PaymentType(**json_response)