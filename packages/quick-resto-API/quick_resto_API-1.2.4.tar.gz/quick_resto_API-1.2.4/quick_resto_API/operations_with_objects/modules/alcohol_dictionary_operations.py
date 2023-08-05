from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.alcohol.alcohol_dictionary import AlcoholDictionary
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class AlcoholDictionaryOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "alcohol.dictionary"

    def get_list_of_alcohol_dictionary(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[AlcoholDictionary]:

        json_response = self._operations_with_objects.get_list(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[AlcoholDictionary] = list()

        for object in json_response:
            result.append(AlcoholDictionary(**object))

        return result

    def get_tree_of_alcohol_dictionary(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[AlcoholDictionary]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        result:list[AlcoholDictionary] = list()

        for object in json_response:
            result.append(AlcoholDictionary(**object))

        return result

    def get_alcohol_dictionary(self, objectId: int, objectRid: int = None) -> AlcoholDictionary:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        return AlcoholDictionary(**json_response)

    def get_alcohol_dictionary_with_subobjects(self, objectId: int, objectRid: int = None) -> AlcoholDictionary:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        return AlcoholDictionary(**json_response)

    def create_alcohol_dictionary(self, object: AlcoholDictionary,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> AlcoholDictionary:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return AlcoholDictionary(**json_response)

    def update_alcohol_dictionary(self, object: AlcoholDictionary,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> AlcoholDictionary:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return AlcoholDictionary(**json_response)

    def remove_alcohol_dictionary(self, object: AlcoholDictionary,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> AlcoholDictionary:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return AlcoholDictionary(**json_response)

    def recover_alcohol_dictionary(self, object: AlcoholDictionary,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> AlcoholDictionary:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return AlcoholDictionary(**json_response)