import json

from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.quick_resto_object import QuickRestoObject
from quick_resto_API.operations_with_objects.list_request.list_request import ListRequest

class OperationsWithObjects:
    def __init__(self, quick_resto_api: QuickRestoApi):
        self._api: QuickRestoApi = quick_resto_api

    def get_list(self, moduleName: str, ownerContextId: int = None,
                ownerContextClassName: str = None, showDeleted: bool = False, listRequest: ListRequest = None):
        params = {
            "moduleName": moduleName,
            "ownerContextId": ownerContextId,
            "ownerContextClassName": ownerContextClassName,
            "showDeleted": showDeleted
        }

        return self._api.get("/api/list", parameters=params, json_data=listRequest.get_json_object())

    def get_tree(self, moduleName: str, ownerContextId: int = None,
                ownerContextClassName: str = None, showDeleted: bool = False, listRequest: ListRequest = None):
        params = {
            "moduleName": moduleName,
            "ownerContextId": ownerContextId,
            "ownerContextClassName": ownerContextClassName,
            "showDeleted": showDeleted
        }

        return self._api.get("/api/tree", parameters=params, json_data=listRequest.get_json_object())

    def get_object(self, moduleName: str, objectId: int, objectRid: int = None):
        params = {
            "moduleName": moduleName,
            "objectId": objectId,
            "objectRid": objectRid
        }

        return self._api.get("/api/get", parameters=params)

    def get_object_with_subobjects(self, moduleName: str, objectId: int, objectRid: int = None):
        params = {
            "moduleName": moduleName,
            "objectId": objectId,
            "objectRid": objectRid
        }

        return self._api.get("/api/read", parameters=params)

    def create_object(self, object: QuickRestoObject, moduleName: str, ownerContextId: int = None,
                     ownerContextClassName: str = None, parentContextId: int = None,
                     parentContextClassName: str = None):
        params = {
            "moduleName": moduleName,
            "ownerContextId": ownerContextId,
            "ownerContextClassName": ownerContextClassName,
            "parentContextId": parentContextId,
            "parentContextClassName": parentContextClassName
        }

        json_data = object.get_json_object()

        return self._api.post("/api/create", parameters=params, json_data=json_data)

    def update_object(self, object: QuickRestoObject, moduleName: str, ownerContextId: int = None,
                     ownerContextClassName: str = None, parentContextId: int = None,
                     parentContextClassName: str = None):
        params = {
            "moduleName": moduleName,
            "ownerContextId": ownerContextId,
            "ownerContextClassName": ownerContextClassName,
            "parentContextId": parentContextId,
            "parentContextClassName": parentContextClassName
        }

        json_data = object.get_json_object()

        return self._api.post("/api/update", parameters=params, json_data=json_data)

    def remove_object(self, object: QuickRestoObject, moduleName: str, ownerContextId: int = None,
                     ownerContextClassName: str = None, parentContextId: int = None,
                     parentContextClassName: str = None):
        params = {
            "moduleName": moduleName,
            "ownerContextId": ownerContextId,
            "ownerContextClassName": ownerContextClassName,
            "parentContextId": parentContextId,
            "parentContextClassName": parentContextClassName
        }

        json_data = object.get_json_object()

        return self._api.post("/api/remove", parameters=params, json_data=json_data)

    def recover_object(self, object: QuickRestoObject, moduleName: str, ownerContextId: int = None,
                      ownerContextClassName: str = None, parentContextId: int = None,
                      parentContextClassName: str = None):
        params = {
            "moduleName": moduleName,
            "ownerContextId": ownerContextId,
            "ownerContextClassName": ownerContextClassName,
            "parentContextId": parentContextId,
            "parentContextClassName": parentContextClassName
        }

        json_data = object.get_json_object()

        return self._api.post("/api/recover", parameters=params, json_data=json_data)
