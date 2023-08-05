from enum import Enum

import quick_resto_API.quick_resto_objects.styler as styler

class FilterOperationType(Enum):
    EQ = "eq"
    NEQ = "neq"
    GTE = "gte"
    LTE = "lte"
    GT = "gt"
    LT = "lt"
    LIKE = "like"
    CONTAINS = "contains"
    RANGE = "range"
    UTC_TIME = "utcTime"

class Filter(object):
    @property
    def field(self) -> str:
        return self._field
    
    @property
    def operation(self) -> FilterOperationType:
        return self._operation
    
    @property
    def value(self) -> str:
        return self._value
    
    def get_json_object(self) -> dict:
        as_dict = self.__dict__
        result = dict()

        for key, value in as_dict.items():
            parameter_name = styler.to_camel_case(key)

            if issubclass(type(value), Enum):
                result[parameter_name] = value.value
            else:
                result[parameter_name] = value
        
        return result
    
    def __init__(self, field: str = None, operation: FilterOperationType = None, value: str = None):
        self._field = field
        self._operation = operation
        self._value = value
