"""
Convenience functions for handling HEAObjects.
"""

from . import client
from .representor import factory as representor_factory
from .representor.error import ParseException
from heaobject.root import HEAObject, DesktopObjectTypeVar, DesktopObjectDict, DesktopObject, desktop_object_type_for_name, Permission
from heaobject.volume import DEFAULT_FILE_SYSTEM, FileSystem, DefaultFileSystem
from heaobject.error import DeserializeException
from heaobject.user import NONE_USER
from heaserver.service.oidcclaimhdrs import SUB
from aiohttp import web
import logging
from typing import Union, Dict, Optional, Type, AsyncGenerator, List, Sequence, Mapping
from yarl import URL
from enum import Enum


class EnumWithAttrs(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class PermissionGroup(EnumWithAttrs):
    """
    Enum that maps heaobject's root.Permission enum values to get, post, put, and delete REST API calls.

    In order to execute a GET request for an object, the user must have at least one of the permissions in the
    GETTER_PERMS permission group (VIEWER, COOWNER, or EDITOR) for the object.

    In order to execute a POST request to create an object, the user must have at least one of the permissions in the
    POSTER_PERMS permission group (CREATOR, COOWNER) for the container in which the object will be created.

    In order to execute a PUT request to update an object, the user must have at least one of the permissions in the
    PUTTER_PERMS permission group (EDITOR, COOWNER) for the object.

    In order to execute a DELETE request to delete an object, the user must have at least one of the permissions in the
    DELETER_PERMS permission group (DELETER, COOWNER) for the object.
    """

    def __init__(self, perms):
        self.perms = perms

    GETTER_PERMS = [Permission.VIEWER, Permission.COOWNER, Permission.EDITOR, Permission.CHECK_DYNAMIC]
    PUTTER_PERMS = [Permission.EDITOR, Permission.COOWNER, Permission.CHECK_DYNAMIC]
    POSTER_PERMS = [Permission.CREATOR, Permission.COOWNER]
    DELETER_PERMS = [Permission.DELETER, Permission.COOWNER, Permission.CHECK_DYNAMIC]


async def new_heaobject_from_type_name(request: web.Request, type_name: str) -> DesktopObject:
    """
    Creates a new HEA desktop object from the body of a HTTP request.
    :param request: the HTTP request.
    :param type_name: the type name of DesktopObject.
    :return: an instance of the given DesktopObject type.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    obj = desktop_object_type_for_name(type_name)()
    return await populate_heaobject(request, obj)


async def new_heaobject_from_type(request: web.Request, type_: Type[DesktopObjectTypeVar]) -> DesktopObjectTypeVar:
    """
    Creates a new HEA desktop object from the body of a HTTP request. If the object's owner is None or no owner
    property was provided, the owner is set to the current user.

    :param request: the HTTP request.
    :param type_: A DesktopObject type. This is compared to the type of the HEA desktop object in the request body, and
    a DeserializeException is raised if the type of the HEA object is not an instance of this type. If the desktop
    object in the body has no type attribute, a DeserializeException is raised.
    :return: an instance of the given DesktopObject type.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    try:
        representor = representor_factory.from_content_type_header(request.headers['Content-Type'])
        _logger.debug('Using %s input parser', representor)
        result = await representor.parse(request)
        _logger.debug('Got dict %s', result)
        if 'type' not in result:
            raise KeyError("'type' not specified in request body. All types must be specified explicitly in the "
                           "body of the request.")
        actual_type = desktop_object_type_for_name(result['type'])
        if not issubclass(actual_type, type_):
            raise TypeError(f'Type of object in request body must be type {type_} but was {actual_type}')
        if result.get('owner', None) is None:
            result['owner'] = request.headers.get(SUB, None)
        obj = actual_type()
        obj.from_dict(result)
        return obj
    except ParseException as e:
        _logger.exception('Failed to parse %s', await request.text())
        raise DeserializeException(str(e)) from e
    except (ValueError, TypeError) as e:
        _logger.exception('Failed to parse %s', result)
        raise DeserializeException(str(e)) from e
    except KeyError as e:
        _logger.exception('Type not found %s', result)
        raise DeserializeException(str(e)) from e
    except DeserializeException as e:
        _logger.exception('Deserialize exception %s', result)
        raise e
    except Exception as e:
        _logger.exception('Other exception %s', await request.text())
        raise DeserializeException(str(e)) from e


async def populate_heaobject(request: web.Request, obj: DesktopObjectTypeVar) -> DesktopObjectTypeVar:
    """
    Populate an HEA desktop object from a POST or PUT HTTP request.

    :param request: the HTTP request. Required.
    :param obj: the HEAObject instance. Required.
    :return: the populated object.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    try:
        representor = representor_factory.from_content_type_header(request.headers['Content-Type'])
        _logger.debug('Using %s input parser', representor)
        result = await representor.parse(request)
        _logger.debug('Got dict %s', result)
        obj.from_dict(result)
        return obj
    except (ParseException, ValueError) as e:
        _logger.exception('Failed to parse %s%s', obj, e)
        raise DeserializeException from e
    except Exception as e:
        _logger.exception('Got exception %s', e)
        raise DeserializeException from e


async def type_to_resource_url(request: web.Request, type_or_type_name: Union[str, Type[DesktopObject]],
                               file_system_type_or_type_name: Union[str, Type[FileSystem]] = DefaultFileSystem,
                               file_system_name: str = DEFAULT_FILE_SYSTEM,
                               parameters: Optional[dict[str, Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]]] = None,
                               **kwargs: Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]) -> Optional[str]:
    """
    Use the HEA registry service to get the resource URL for accessing HEA objects of the given type.

    :param request: the HTTP request. Required.
    :param type_or_type_name: the type or type name of HEA desktop object. Required.
    :param file_system_type_or_type_name: the type of file system. The default is DefaultFileSystem.
    :param file_system_name: the name of a file system. The default is filesystems.DEFAULT.
    :return: the URL string, or None if no resource URL was found.
    """
    return await client.get_resource_url(request.app, type_or_type_name, file_system_type_or_type_name,
                                         file_system_name, parameters=parameters, kwargs=kwargs)


async def get_dict(request: web.Request, id_: str, type_or_type_name: Union[str, Type[DesktopObject]],
                   file_system_type_or_type_name: Union[str, Type[FileSystem]] = DefaultFileSystem,
                   file_system_name: str = DEFAULT_FILE_SYSTEM,
                   headers: Optional[Dict[str, str]] = None) -> Optional[DesktopObjectDict]:
    """
    Gets the HEA desktop object dict with the provided id from the service for the given type, file system type,
    and file system name.

    :param request: the aiohttp request (required).
    :param id_: the id of the HEA desktop object of interest.
    :param type_or_type_name: the desktop object type or type name.
    :param file_system_type_or_type_name: the file system type or type name.
    :param file_system_name: the file system name.
    :param headers: optional HTTP headers to use.
    :return: the requested HEA desktop object dict, or None if not found.
    :raises ValueError: if no appropriate service was found.
    """
    url = await type_to_resource_url(request, type_or_type_name=type_or_type_name,
                                     file_system_type_or_type_name=file_system_type_or_type_name,
                                     file_system_name=file_system_name)
    if url is None:
        raise ValueError(
            f'No service for type {type_or_type_name}, file system type {file_system_type_or_type_name} and file system name {file_system_name} found')
    return await client.get_dict(request.app, URL(url) / id_, headers)


async def get(request: web.Request, id_: str, type_: Type[DesktopObjectTypeVar],
              file_system_type_or_type_name: Union[str, Type[FileSystem]] = DefaultFileSystem,
              file_system_name: str = DEFAULT_FILE_SYSTEM,
              headers: Optional[Dict[str, str]] = None) -> Optional[DesktopObjectTypeVar]:
    """
    Gets the HEA desktop object with the provided id from the service for the given type, file system type, and file
    system name.

    :param request: the aiohttp request (required).
    :param id_: the id of the HEA desktop object of interest.
    :param type_: the desktop object type.
    :param file_system_type_or_type_name: the file system type or type name.
    :param file_system_name: the file system name.
    :param headers: optional HTTP headers to use.
    :return: the requested HEA desktop object, or None if not found.
    :raises ValueError: if no appropriate service was found.
    """
    url = await type_to_resource_url(request, type_or_type_name=type_,
                                     file_system_type_or_type_name=file_system_type_or_type_name,
                                     file_system_name=file_system_name)
    if url is None:
        raise ValueError(
            f'No service for type {type_}, file system type {file_system_type_or_type_name} and file system name {file_system_name} found')

    return await client.get(request.app, URL(url) / id_, type_, headers)


async def get_all(request: web.Request, type_: Type[DesktopObjectTypeVar],
                  file_system_type_or_type_name: Union[str, Type[FileSystem]] = DefaultFileSystem,
                  file_system_name: str = DEFAULT_FILE_SYSTEM,
                  headers: Optional[Dict[str, str]] = None) -> AsyncGenerator[DesktopObjectTypeVar, None]:
    """
    Async generator for all HEA desktop objects from the service for the given type, file system type, and file system
    name.

    :param request: the aiohttp request (required).
    :param type_: the desktop object type.
    :param file_system_type_or_type_name: the file system type or type name.
    :param file_system_name: the file system name.
    :param headers: optional HTTP headers to use.
    :return: an async generator with the requested desktop objects.
    :raises ValueError: if no appropriate service was found.
    """
    url = await type_to_resource_url(request, type_or_type_name=type_,
                                     file_system_type_or_type_name=file_system_type_or_type_name,
                                     file_system_name=file_system_name)
    if url is None:
        raise ValueError(
            f'No service for type {type_}, file system type {file_system_type_or_type_name} and file system name {file_system_name} found')

    return client.get_all(request.app, url, type_, headers)


def has_permissions(obj: DesktopObject, sub: Optional[str], permissions: List[Permission]) -> bool:
    """
    Return whether the provided user subject has any of the provided permissions to the object.

    :param obj: the HEA desktop object to check (required).
    :param sub: the user subject.
    :param permissions: a list of Permission enum values (required).
    :return: True or False.
    """
    return obj.has_permissions(sub if sub is not None else NONE_USER, permissions)


def desktop_object_type_or_type_name_to_type(type_or_type_name: str | type[DesktopObject], default_type: type[DesktopObject] = None) -> type[DesktopObject]:
    """
    Takes a variable that may contain either a DesktopObject type or type name, and return a type. If a type is passed
    in, and it is a subclass of DesktopObject, it will be returned as-is. If a type name is passed in, its corresponding
    type will be returned if the type is a subclass of DesktopObject.

    :param type_or_type_name: the type or type name. Required.
    :param default_type: what to return if type_or_type_name is None. If omitted, None is returned.
    """
    if default_type is not None and not issubclass(default_type, DesktopObject):
        raise TypeError('default_type is defined and not a DesktopObject')
    if isinstance(type_or_type_name, type):
        if not issubclass(type_or_type_name, DesktopObject):
            raise TypeError(f'type_or_type_name not a DesktopObject')
        if issubclass(type_or_type_name, DesktopObject):
            result_ = type_or_type_name
        else:
            raise TypeError('type_or_type_name not a DesktopObject')
    else:
        file_system_type_ = desktop_object_type_for_name(type_or_type_name)
        if not issubclass(file_system_type_, DesktopObject):
            raise TypeError(f'file_system_type_or_type_name is a {file_system_type_} not a DesktopObject')
        else:
            result_ = file_system_type_
    if result_ is None:
        return default_type
    else:
        return result_


def type_or_type_name_to_type(type_or_type_name: str | type[HEAObject], default_type: type[HEAObject] = None) -> type[HEAObject]:
    """
    Takes a variable that may contain either a HEAObject type or type name, and return a type. If a type is passed
    in, and it is a subclass of HEAObject, it will be returned as-is. If a type name is passed in, its corresponding
    type will be returned if the type is a subclass of HEAObject.

    :param type_or_type_name: the type or type name. Required.
    :param default_type: what to return if type_or_type_name is None. If omitted, None is returned.
    """
    if default_type is not None and not issubclass(default_type, HEAObject):
        raise TypeError('default_type is defined and not a HEAObject')
    if isinstance(type_or_type_name, type):
        if not issubclass(type_or_type_name, HEAObject):
            raise TypeError(f'type_or_type_name not a HEAObject')
        if issubclass(type_or_type_name, HEAObject):
            result_ = type_or_type_name
        else:
            raise TypeError('type_or_type_name not a HEAObject')
    else:
        file_system_type_ = desktop_object_type_for_name(type_or_type_name)
        if not issubclass(file_system_type_, HEAObject):
            raise TypeError(f'file_system_type_or_type_name is a {file_system_type_} not a HEAObject')
        else:
            result_ = file_system_type_
    if result_ is None:
        return default_type
    else:
        return result_
