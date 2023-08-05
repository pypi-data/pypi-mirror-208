import heaobject.root

from ..appproperty import HEA_DB
from .. import response
from ..heaobjectsupport import new_heaobject_from_type, has_permissions, PermissionGroup, new_heaobject_from_type_name, \
    populate_heaobject
from .mongo import Mongo
from .database import get_file_system_and_credentials_from_volume
from heaobject.error import DeserializeException
from heaobject.volume import MongoDBFileSystem
from aiohttp.web import Request, StreamResponse, Response
from typing import Type, IO, Optional
from heaobject.root import DesktopObject
from heaserver.service.oidcclaimhdrs import SUB
from pymongo.errors import WriteError


async def get(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets the HEA object with the specified id.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response with the requested HEA object or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get(request, collection, var_parts='id', sub=request.headers.get(SUB))

    if result is not None:
        obj = heaobject.root.desktop_object_from_dict(result)
        permitted = has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.GETTER_PERMS.perms)
        if not permitted:
            return response.status_not_found()

    return await response.get(request, result if result is not None else None)


async def get_content(request: Request, collection: str, volume_id: Optional[str] = None) -> StreamResponse:
    """
    Gets the HEA object's associated content.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: an aiohttp StreamResponse with the requested HEA object or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get(request, collection, var_parts='id', sub=request.headers.get(SUB))

    if result is not None:
        obj = heaobject.root.desktop_object_from_dict(result)
        permitted = has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.GETTER_PERMS.perms)
        if not permitted:
            return response.status_not_found()
    out = await mongo.get_content(request, collection, var_parts='id', sub=request.headers.get(SUB))
    if out is not None:
        return await response.get_streaming(request, out, 'text/plain')
    else:
        return response.status_not_found()


async def get_by_name(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets the HEA object with the specified name.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response with the requested HEA object or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get(request, collection, var_parts='name', sub=request.headers.get(SUB))

    if result is not None:
        obj = heaobject.root.desktop_object_from_dict(result)
        permitted = has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.GETTER_PERMS.perms)
        if not permitted:
            return response.status_not_found()

    return await response.get(request, result if result is not None else None)


async def get_all(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets all HEA objects.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response with a list of HEA object dicts.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get_all(request, collection, sub=request.headers.get(SUB))
    permitted_result = []
    for r in result:
        obj = heaobject.root.desktop_object_from_dict(r)
        if has_permissions(obj=obj,
                           sub=request.headers.get(SUB),
                           permissions=PermissionGroup.GETTER_PERMS.perms):
            permitted_result.append(r)

    return await response.get_all(request, permitted_result)


async def opener(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets choices for opening an HEA desktop object's content.

    :param request: the HTTP request. Required. If an Accepts header is provided, MIME types that do not support links
    will be ignored.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with status code 300, and a body containing the HEA desktop object and links
    representing possible choices for opening the HEA desktop object; or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get(request, collection, var_parts='id', sub=request.headers.get(SUB))

    if result is not None:
        obj = heaobject.root.desktop_object_from_dict(result)
        permitted = has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.GETTER_PERMS.perms)
        if not permitted:
            return response.status_not_found()

    return await response.get_multiple_choices(request, result if result is not None else None)


async def post(request: Request, collection: str, type_: Type[DesktopObject], default_content: Optional[IO] = None, volume_id: Optional[str] = None) -> Response:
    """
    Posts the provided HEA object.

    :param request: the HTTP request.
    :param collection: the Mongo collection name. Required.
    :param type_: The HEA object type. Required.
    :param default_content: an optional blank document or other default content as a file-like object. This must be not-None
    for any microservices that manage content.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with a status of Created and the object's URI in the
    """
    try:
        obj = await new_heaobject_from_type(request, type_)
    except DeserializeException as e:
        return response.status_bad_request(str(e).encode())
    if obj.owner is None:
        obj.owner = request.headers.get(SUB, None)
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.post(request, obj, collection, default_content)
    return await response.post(request, result, collection)


async def put(request: Request, collection: str, type_: Type[DesktopObject], volume_id: Optional[str] = None) -> Response:
    """
    Updates the HEA object with the specified id.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param type_: The HEA object type. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with a status of No Content, Forbidden, or Not Found.
    """
    sub = request.headers.get(SUB, None)
    mongo = await _get_mongo(request, volume_id)
    try:
        obj = await new_heaobject_from_type(request, type_)
    except DeserializeException as e:
        return response.status_bad_request(str(e).encode())
    try:
        permitted = has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.PUTTER_PERMS.perms)
        if not permitted:
            if has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.GETTER_PERMS.perms):
                return response.status_forbidden()
            else:
                return response.status_not_found()

        result = await mongo.put(request, obj, collection, sub=sub)  # if lacks permissions or object is not in database, then updates no records.
    except WriteError as e:
        if e.code == 66:
            return response.status_bad_request(e.details['errmsg'])
        else:
            return response.status_internal_error(e.details.get('errmsg'))
    return await response.put(result.matched_count if result else False)


async def put_content(request: Request, collection: str, type_: Type[DesktopObject], volume_id: Optional[str] = None) -> Response:
    """
    Updates the HEA object's associated content.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param type_: The HEA object type. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with a status of No Content, Forbidden, or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    sub = request.headers.get(SUB)
    result = await mongo.get(request, collection, var_parts='id', sub=sub)

    if result is not None:
        obj = heaobject.root.desktop_object_from_dict(result)
        permitted = has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.PUTTER_PERMS.perms)
        if not permitted:
            if has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.GETTER_PERMS.perms):
                return response.status_forbidden()
            else:
                return response.status_not_found()
        result2 = await mongo.put_content(request, collection, sub=sub)  # if lacks permissions, then updates no records.
        return await response.put(result2)
    else:
        return response.status_not_found()


async def delete(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Deletes the HEA object with the specified id and any associated content.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: No Content, Forbidden, or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    sub = request.headers.get(SUB)
    result = await mongo.get(request, collection, var_parts='id', sub=request.headers.get(SUB))

    if result is not None:
        obj = heaobject.root.desktop_object_from_dict(result)
        permitted = has_permissions(obj=obj, sub=request.headers.get(SUB), permissions=PermissionGroup.DELETER_PERMS.perms)
        if not permitted:
            return response.status_forbidden()
        result = await mongo.delete(request, collection, var_parts='id', sub=sub)  # if lacks permissions, then deletes no records.
    else:
        return response.status_not_found()
    return await response.delete(result.deleted_count if result else False)


async def _get_mongo(request: Request, volume_id: Optional[str]) -> Mongo:
    """
    Gets a mongo client.

    :param request: the HTTP request (required).
    :param volume_id: the id string of a volume.
    :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
    was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
    application-level property.
    :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
    or a necessary service is not registered.
    """

    if volume_id is not None:
        file_system, credentials = await get_file_system_and_credentials_from_volume(request, volume_id, MongoDBFileSystem)
        if credentials is None:
            return Mongo(None, connection_string=file_system.connection_string)
        else:
            return Mongo(None, connection_string=file_system.connection_string, username=credentials.account, password=credentials.password)
    else:
        return request.app[HEA_DB]


