from enum import Enum

import quick_resto_API.quick_resto_objects.styler as styler
from quick_resto_API.operations_with_objects.list_request.filter import Filter

class ListRequest(object):
    @property
    def filters(self) -> list[Filter]:
        return self._filters
    
    @property
    def mode(self) -> str:
        return self._mode
    
    @property
    def ext_params(self) -> dict[str, list[str]]:
        return self._ext_params
    
    @property
    def sort_fields(self) -> list[str]:
        return self._sort_fields
    
    @property
    def sort_orders(self) -> list[str]:
        return self._sort_orders
    
    def get_json_object(self) -> dict:
        as_dict = self.__dict__
        result = dict()

        for key, value in as_dict.items():
            parameter_name = styler.to_camel_case(key)

            if value is None:
                continue

            if issubclass(type(value), Enum):
                result[parameter_name] = value.value
            elif issubclass(type(value), list):
                list_of_subobjects = []

                for obj in value:
                    if issubclass(type(obj), Filter):
                        list_of_subobjects.append(obj.get_json_object())

                result[parameter_name] = list_of_subobjects
            else:
                result[parameter_name] = value
        
        return result

    def __init__(self, filters: list[Filter] = None, mode: str = None, ext_params: dict[str, list[str]] = None, 
                 sort_fields: list[str] = None, sort_orders: list[str] = None):
        self._filters = filters
        self._mode = mode
        self._ext_params = ext_params
        self._sort_fields = sort_fields
        self._sort_orders = sort_orders
    