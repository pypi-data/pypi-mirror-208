from aiohttp import hdrs, web, ClientSession
from heaobject import root
from heaobject.root import DesktopObject, DesktopObjectTypeVar, DesktopObjectDict
from heaobject.registry import Component, Property
from heaobject.volume import DEFAULT_FILE_SYSTEM, DefaultFileSystem, FileSystem
from . import appproperty, response
from .aiohttp import StreamReaderWrapper, SupportsAsyncRead
from .representor import nvpjson
from yarl import URL
from typing import Optional, Union, Dict, Type, Mapping, AsyncGenerator, Sequence
import logging


async def get_streaming(request: web.Request, url: Union[str, URL],
                        headers: Optional[Dict[str, str]] = None,
                        client_session: ClientSession | None = None) -> web.StreamResponse:
    _logger = logging.getLogger(__name__)
    session = client_session if client_session is not None else request.app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting streaming content at %s with headers %s', url, headers)
    async with session.get(url, headers=headers, raise_for_status=False) as response_:
        if response_.status == 200:
            content_type = response_.headers.get(hdrs.CONTENT_TYPE, None)
            return await response.get_streaming(request, StreamReaderWrapper(response_.content),
                                                content_type=content_type)
        elif response_.status == 404:
            return response.status_not_found()
        else:
            return web.Response(status=response_.status)


async def put_streaming(request: web.Request, url: Union[str, URL], data: SupportsAsyncRead,
                        headers: Optional[Dict[str, str]] = None,
                        client_session: ClientSession | None = None) -> None:
    session = client_session if client_session is not None else request.app[appproperty.HEA_CLIENT_SESSION]
    async with session.put(url, data=data, headers=headers):
        pass


async def get_dict(app, url, headers=None,
                   client_session: ClientSession | None = None) -> Optional[DesktopObjectDict]:
    """
    Co-routine that gets a dict from a HEA service that returns JSON.

    :param app: the aiohttp application context (required).
    :param url: The URL (str or URL) of the resource (required).
    :param headers: optional dict of headers.
    :return: the dict populated with the resource's content, None if no such resource exists, or another HTTP
    status code if an error occurred.
    """
    _logger = logging.getLogger(__name__)
    session = client_session if client_session is not None else app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting dict at %s with headers %s', url, headers)
    async with session.get(url, headers=headers, raise_for_status=False) as response_:
        if response_.status == 404:
            return None
        else:
            response_.raise_for_status()
            result = await response_.json()
            _logger.debug('Client returning %s', result)
            result_len = len(result)
            if result_len != 1:
                raise ValueError(f'Result from {url} has {result_len} values')
            return result[0] if isinstance(result, list) else result


async def get(app: web.Application, url: Union[URL, str],
              type_or_obj: Union[DesktopObjectTypeVar, Type[DesktopObjectTypeVar]],
              query_params: Optional[Mapping[str, str]] = None,
              headers: Optional[Mapping[str, str]] = None,
              client_session: ClientSession | None = None) -> Optional[DesktopObjectTypeVar]:
    """
    Co-routine that gets a HEA desktop object from a HEA service.


    :param app: the aiohttp application context (required).
    :param url: The URL (str or URL) of the resource (required).
    :param type_or_obj: the HEA desktop object type to populate with the resource's content, or a desktop object instance. If a
    type, this function will attempt to create an instance using the type's no-arg constructor.
    :param query_params: optional Mapping, iterable of tuple of key/value pairs or string to be sent as parameters in the query string of the new request.
    :param headers: optional dict of headers. Attempts to set the Accept header will be ignored. The service will
    always receive Accepts: application/json.
    :return: the HEAObject populated with the resource's content, None if no such resource exists, or another HTTP
    status code if an error occurred.
    """
    _logger = logging.getLogger(__name__)
    _logger.info("about to make the GET client call ")
    if isinstance(type_or_obj, type) and issubclass(type_or_obj, root.DesktopObject):
        obj_ = type_or_obj()
    elif isinstance(type_or_obj, root.DesktopObject):
        obj_ = type_or_obj
    else:
        raise TypeError('obj must be an HEAObject instance or an HEAObject type')
    _logger.info("here is the obj_ type: %s" % obj_.get_type_name())
    headers_ = dict(headers) if headers else {}
    headers_[hdrs.ACCEPT] = nvpjson.MIME_TYPE

    session = client_session if client_session is not None else app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting content at %s with headers %s', url, headers_)
    async with session.get(url, headers=headers_, params=query_params,
                           raise_for_status=False) as response_:
        if response_.status == 404:
            return None
        else:
            response_.raise_for_status()
            result = await response_.json()
            _logger.debug('Client returning %s', result)
            result_len = len(result)
            if result_len != 1:
                raise ValueError(f'Result from {url} has {result_len} values')
            obj_.from_dict(result[0])
            _logger.debug('Got desktop object %s', obj_)
            return obj_


async def get_all(app: web.Application, url: Union[URL, str], type_: Type[DesktopObjectTypeVar],
                  query_params: Optional[Mapping[str, str]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  client_session: ClientSession | None = None) -> AsyncGenerator[DesktopObjectTypeVar, None]:
    """
    Generator that returns the requested HEAObjects.

    :param app: the aiohttp application context (required).
    :param url: The URL (str or URL) of the resource (required).
    :param type_: the type to populate with the resource's content.
    :param query_params: optional Mapping, iterable of tuple of key/value pairs or string to be sent as parameters in the query string of the new request.
    :param headers: optional dict of headers. Attempts to set the Accept header will be ignored. The service will
    always receive Accepts: application/json.
    """
    _logger = logging.getLogger(__name__)
    if isinstance(type_, type) and issubclass(type_, root.DesktopObject):
        obj___ = type_
    else:
        raise TypeError('obj must be an HEAObject instance or an HEAObject type')
    headers_ = dict(headers) if headers else {}
    headers_[hdrs.ACCEPT] = nvpjson.MIME_TYPE

    session = client_session if client_session is not None else app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting content at %s with headers %s', url, headers_)
    async with session.get(url, params=query_params, headers=headers_, raise_for_status=False) as response_:
        response_.raise_for_status()
        result = await response_.json()
        _logger.debug('Client returning %s', result)
        for r in result:
            obj__ = obj___()
            obj__.from_dict(r)
            yield obj__


async def post(app: web.Application, url: Union[URL, str], data: root.DesktopObject | root.DesktopObjectDict,
               headers: Dict[str, str] = None,
               client_session: ClientSession | None = None) -> str:  # type: ignore[return]
    """
    Coroutine that posts a HEAObject to a HEA service.

    :param app: the aiohttp application context (required).
    :param url: the The URL (str or URL) of the resource (required).
    :param data: the DesktopObject or DesktopObjectDict (required).
    :param headers: optional dict of headers.
    :return: the URL string in the response's Location header.
    """
    session = client_session if client_session is not None else app[appproperty.HEA_CLIENT_SESSION]
    async with session.post(url, json=data, headers=headers, raise_for_status=False) as response_:
        response_.raise_for_status()
        return response_.headers['Location']


async def put(app: web.Application, url: Union[URL, str], data: root.DesktopObject | root.DesktopObjectDict,
              headers: Dict[str, str] = None,
              client_session: ClientSession | None = None) -> None:
    """
    Coroutine that updates a HEAObject.

    :param app: the aiohttp application context (required).
    :param url: the The URL (str or URL) of the resource (required).
    :param data: the DesktopObject or DesktopObjectDict (required).
    :param headers: optional dict of headers.
    :param client_session: a HTTP client session. If None, the function falls back to the HEA_CLIENT_SESSION application
    property for a client session.
    :returns if successful it returns None else if it fails it will raise HttpError
    """
    session = client_session if client_session is not None else app[appproperty.HEA_CLIENT_SESSION]
    async with session.put(url, json=data, headers=headers, raise_for_status=False) as response_:
        response_.raise_for_status()


async def delete(app: web.Application, url: Union[URL, str],
                 headers: Dict[str, str] = None,
                 client_session: ClientSession | None = None) -> None:
    """
    Coroutine that deletes a HEAObject.

    :param app: the aiohttp application context (required).
    :param url: the URL (str or URL) of the resource (required).
    :param headers: optional dict of headers.
    :returns if successful it returns None else if it fails it will raise HttpError
    """
    _logger = logging.getLogger(__name__)
    session = client_session if client_session is not None else app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Deleting %s', str(url))
    async with session.delete(url, headers=headers, raise_for_status=False) as response_:
        response_.raise_for_status()


async def get_component_by_name(app: web.Application, name: str,
                 client_session: ClientSession | None = None) -> Optional[Component]:
    """
    Gets the Component with the given name from the HEA registry service.

    :param app: the aiohttp app.
    :param name: the component's name.
    :return: a Component instance or None (if not found).
    """
    return await get(app, URL(app[appproperty.HEA_REGISTRY]) / 'components' / 'byname' / name, Component,
                     client_session=client_session)


async def get_component(app: web.Application, type_or_type_name: Union[str, Type[root.HEAObject]],
                        file_system_type_or_type_name: Union[str, Type[FileSystem]] = DefaultFileSystem,
                        file_system_name: str = DEFAULT_FILE_SYSTEM,
                        client_session: ClientSession | None = None) -> Component | None:
    """
    Gets the component corresponding to the HEA object type from the HEA registry service.

    :param app: the aiohttp app.
    :param type_or_type_name: the HEAObject type or type name of the resource.
    :param file_system_type_or_type_name: optional file system type or type name. The default is heaobject.volume.DefaultFileSystem.
    :param file_system_name: optional file system name. The default is heaobject.volume.FileSystem.DEFAULT_FILE_SYSTEM.
    :return: the Component, or None if not found.
    """
    from .heaobjectsupport import desktop_object_type_or_type_name_to_type, type_or_type_name_to_type
    file_system_name_ = DEFAULT_FILE_SYSTEM if file_system_name is None else file_system_name
    file_system_type_ = desktop_object_type_or_type_name_to_type(file_system_type_or_type_name,
                                                                 default_type=DefaultFileSystem)
    type_name_ = type_or_type_name_to_type(type_or_type_name).get_type_name()
    url = URL(app[appproperty.HEA_REGISTRY]) / 'components' / 'bytype' / type_name_ / 'byfilesystemtype' / file_system_type_.get_type_name() / 'byfilesystemname' / file_system_name_
    return await get(app, url, Component, client_session=client_session)


async def get_resource_url(app: web.Application, type_or_type_name: Union[str, Type[root.HEAObject]],
                           file_system_type_or_type_name: Union[str, Type[FileSystem]] = DefaultFileSystem,
                           file_system_name: str = DEFAULT_FILE_SYSTEM,
                           client_session: ClientSession | None = None,
                           parameters: Optional[dict[str, Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]]] = None,
                           **kwargs: Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]) -> Optional[str]:
    """
    Gets the resource URL corresponding to the HEA object type from the HEA registry service. The URL is constructed by
    joining the component's base URL and the resource base path.

    :param app: the aiohttp app.
    :param type_or_type_name: the HEAObject type or type name of the resource.
    :param file_system_type_or_type_name: optional file system type or type name. The default is heaobject.volume.DefaultFileSystem.
    :param file_system_name: optional file system name. The default is heaobject.volume.FileSystem.DEFAULT_FILE_SYSTEM.
    :param parameters: for resource URLs with a URI template, the template parameters.
    :param kwargs: alternative way to provide template parameters.
    :return: a URL string or None (if not found).
    """
    from .heaobjectsupport import type_or_type_name_to_type
    logger = logging.getLogger(__name__)
    component = await get_component(app, type_or_type_name, file_system_type_or_type_name, file_system_name, client_session=client_session)
    logger.debug('Got component %s from registry', component)
    file_system_name_ = DEFAULT_FILE_SYSTEM if file_system_name is None else file_system_name
    type_name_ = type_or_type_name_to_type(type_or_type_name).get_type_name()
    return component.get_resource_url(type_name_, file_system_name=file_system_name_, parameters=parameters, kwargs=kwargs) if component is not None else None


async def get_property(app: web.Application, name: str,
                       client_session: ClientSession | None = None) -> Property | None:
    """
    Gets the Property with the given name from the HEA registry service.

    :param app: the aiohttp app.
    :param name: the property's name.
    :return: a Property instance or None (if not found).
    """
    return await get(app, URL(app[appproperty.HEA_REGISTRY]) / 'properties' / 'byname' / name,
                     Property,
                     client_session=client_session)

