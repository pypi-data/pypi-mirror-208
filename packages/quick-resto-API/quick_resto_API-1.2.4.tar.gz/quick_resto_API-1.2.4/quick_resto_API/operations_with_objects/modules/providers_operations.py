from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.businessman import Businessman
from quick_resto_API.quick_resto_objects.modules.warehouse.natural_person import NaturalPerson
from quick_resto_API.quick_resto_objects.modules.warehouse.organization import Organization
from quick_resto_API.quick_resto_objects.modules.warehouse.provider_group import ProviderGroup
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class ProvidersOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.providers"

    def get_list_of_provider(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[Businessman|NaturalPerson|Organization|ProviderGroup]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[Businessman|NaturalPerson|Organization|ProviderGroup] = list()

        for object in json_response:
            if 'Businessman' in object['className']:
                result.append(Businessman(**object))
            elif 'NaturalPerson' in object['className']:
                result.append(NaturalPerson(**object))
            elif 'Organization' in object['className']:
                result.append(Organization(**object))
            elif 'ProviderGroup' in object['className']:
                result.append(ProviderGroup(**object))

        return result

    def get_tree_of_provider(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[Businessman|NaturalPerson|Organization|ProviderGroup]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[Businessman|NaturalPerson|Organization|ProviderGroup] = list()

        for object in json_response:
            if 'Businessman' in object['className']:
                result.append(Businessman(**object))
            elif 'NaturalPerson' in object['className']:
                result.append(NaturalPerson(**object))
            elif 'Organization' in object['className']:
                result.append(Organization(**object))
            elif 'ProviderGroup' in object['className']:
                result.append(ProviderGroup(**object))

        return result

    def get_provider(self, objectId: int, objectRid: int = None) -> Businessman|NaturalPerson|Organization|ProviderGroup:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        if 'Businessman' in object['className']:
            return Businessman(**json_response)
        elif 'NaturalPerson' in object['className']:
            return NaturalPerson(**json_response)
        elif 'Organization' in object['className']:
            return Organization(**json_response)
        else:
            return ProviderGroup(**json_response)

    def get_provider_with_subobjects(self, objectId: int, objectRid: int = None) -> Businessman|NaturalPerson|Organization|ProviderGroup:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        if 'Businessman' in object['className']:
            return Businessman(**json_response)
        elif 'NaturalPerson' in object['className']:
            return NaturalPerson(**json_response)
        elif 'Organization' in object['className']:
            return Organization(**json_response)
        else:
            return ProviderGroup(**json_response)

    def create_provider(self, object: Businessman|NaturalPerson|Organization|ProviderGroup,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Businessman|NaturalPerson|Organization|ProviderGroup:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'Businessman' in object['className']:
            return Businessman(**json_response)
        elif 'NaturalPerson' in object['className']:
            return NaturalPerson(**json_response)
        elif 'Organization' in object['className']:
            return Organization(**json_response)
        else:
            return ProviderGroup(**json_response)

    def update_provider(self, object: Businessman|NaturalPerson|Organization|ProviderGroup,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Businessman|NaturalPerson|Organization|ProviderGroup:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'Businessman' in object['className']:
            return Businessman(**json_response)
        elif 'NaturalPerson' in object['className']:
            return NaturalPerson(**json_response)
        elif 'Organization' in object['className']:
            return Organization(**json_response)
        else:
            return ProviderGroup(**json_response)

    def remove_provider(self, object: Businessman|NaturalPerson|Organization|ProviderGroup,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Businessman|NaturalPerson|Organization|ProviderGroup:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'Businessman' in object['className']:
            return Businessman(**json_response)
        elif 'NaturalPerson' in object['className']:
            return NaturalPerson(**json_response)
        elif 'Organization' in object['className']:
            return Organization(**json_response)
        else:
            return ProviderGroup(**json_response)

    def recover_provider(self, object: Businessman|NaturalPerson|Organization|ProviderGroup,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Businessman|NaturalPerson|Organization|ProviderGroup:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'Businessman' in object['className']:
            return Businessman(**json_response)
        elif 'NaturalPerson' in object['className']:
            return NaturalPerson(**json_response)
        elif 'Organization' in object['className']:
            return Organization(**json_response)
        else:
            return ProviderGroup(**json_response)