from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.warehouse.dish import Dish
from quick_resto_API.quick_resto_objects.modules.warehouse.dish_category import DishCategory
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class DishOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "warehouse.nomenclature.dish"

    def get_list_of_dishes(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[Dish|DishCategory]:

        json_response = self._operations_with_objects.get_list(self._module_name, ownerContextId, 
                                                                    ownerContextClassName, showDeleted, listRequest).json()

        dishes:list[Dish|DishCategory] = list()

        for dish in json_response:
            if 'DishCategory' in dish['className']:
                dishes.append(DishCategory(**dish))
            elif 'Dish' in dish['className']:
                dishes.append(Dish(**dish))

        return dishes

    def get_tree_of_dishes(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False, listRequest: ListRequest = None) -> list[Dish|DishCategory]:

        json_response = self._operations_with_objects.get_tree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted, listRequest).json()

        dishes:list[Dish|DishCategory] = list()

        for dish in json_response:
            if 'DishCategory' in dish['className']:
                dishes.append(DishCategory(**dish))
            elif 'Dish' in dish['className']:
                dishes.append(Dish(**dish))

        return dishes

    def get_dish_or_dish_category(self, objectId: int, objectRid: int = None) -> Dish | DishCategory:
        json_response = self._operations_with_objects.get_object(self._module_name, objectId, objectRid).json()

        if 'DishCategory' in json_response['className']:
            return DishCategory(**json_response)
        else:
            return Dish(**json_response)

    def get_dish_or_dish_category_with_subobjects(self, objectId: int, objectRid: int = None) -> Dish | DishCategory:
        json_response = self._operations_with_objects.get_object_with_subobjects(self._module_name, objectId, objectRid).json()

        if 'DishCategory' in json_response['className']:
            return DishCategory(**json_response)
        else:
            return Dish(**json_response)

    def create_dish_or_dish_category(self, object: Dish | DishCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Dish | DishCategory:

        json_response = self._operations_with_objects.create_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'DishCategory' in json_response['className']:
            return DishCategory(**json_response)
        else:
            return Dish(**json_response)

    def update_dish_or_dish_category(self, object: Dish | DishCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Dish | DishCategory:

        json_response = self._operations_with_objects.update_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'DishCategory' in json_response['className']:
            return DishCategory(**json_response)
        else:
            return Dish(**json_response)

    def remove_dish_or_dish_category(self, object: Dish | DishCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Dish | DishCategory:

        json_response = self._operations_with_objects.remove_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'DishCategory' in json_response['className']:
            return DishCategory(**json_response)
        else:
            return Dish(**json_response)

    def recover_dish_or_dish_category(self, object: Dish | DishCategory,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Dish | DishCategory:

        json_response = self._operations_with_objects.recover_object(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        if 'DishCategory' in json_response['className']:
            return DishCategory(**json_response)
        else:
            return Dish(**json_response)