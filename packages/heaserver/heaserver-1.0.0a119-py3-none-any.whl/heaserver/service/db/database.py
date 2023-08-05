import abc
import configparser
from abc import ABC, abstractmethod
from contextlib import ExitStack, contextmanager, AbstractContextManager

from aiohttp import web, hdrs
from typing import Optional, Type, Tuple, Mapping, List, Callable, Awaitable, Union, Dict, Generator, AsyncGenerator

from aiohttp.web_request import Request
from aiohttp.web_response import Response
from heaobject.keychain import Credentials, CredentialTypeVar
from heaobject.volume import FileSystemTypeVar, FileSystem, Volume, AWSFileSystem
from heaobject.root import DesktopObjectDict, DesktopObject
from yarl import URL
from multidict import istr, CIMultiDict, CIMultiDictProxy

from heaserver.service import client, response
from heaserver.service.heaobjectsupport import type_to_resource_url, desktop_object_type_or_type_name_to_type
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.util import modified_environ

from copy import copy, deepcopy
import logging


class NotStartedError(ValueError):

    def __init__(self, *args: object) -> None:
        super().__init__('The database is not running. Call start_database() first.', *args)

class Database(abc.ABC):
    """
    Connectivity to databases and other data storage systems for HEA microservices. The database object may be
    optionally configured by providing a ConfigParser object to the constructor. The ConfigParser class provides a
    similar structure to what is found in Windows INI files, including the use of section headers. Section headers
    should be prefixed by the Database subclass' full class name as produced by str(cls) to avoid name clashes.
    Properties in the ConfigParser object should be named using CamelCase. This class is not designed for multiple
    inheritance.
    """

    def __init__(self, config: Optional[configparser.ConfigParser], **kwargs) -> None:
        """
        Initializes the database object. Subclasses must call this constructor.

        :param config: Optional HEA configuration.
        """
        super().__init__(**kwargs)
        logger = logging.getLogger(__name__)
        logger.debug(f'Initialized {type(self)} database object')

    @classmethod
    def get_config_section(cls) -> str:
        """
        Gets this database type's section in the HEA configuration. By default, the section name is that produced by
        str(cls) in order to avoid name clashes. When overriding this method, take care not to construct a name that
        might clash with the current or future section header of another Database class.
        """
        return str(cls)

    async def get_file_system_and_credentials_from_volume(self, request: web.Request, volume_id: Optional[str]) -> \
    Tuple[AWSFileSystem, Optional[CredentialTypeVar]]:
        """
        Gets the file system and credentials for the given volume. It uses the registry microservice to access the
        file system and credentials microservices. Override this method to mock getting a file system and credentials.

        :param request: the aiohttp request (required).
        :param volume_id: a volume id string (required).
        :return: a tuple containing a FileSystem object and, if one exists, a Credentials object (or None if one does
        not).
        :raise ValueError: if no volume with that id exists, no file system exists for the given volume, or the volumes's
        credentials were not found.
        """
        return await get_file_system_and_credentials_from_volume(request, volume_id, AWSFileSystem)

    async def get_volumes(self, request: Request, file_system_type_or_type_name: Union[str, type[FileSystem]]) -> AsyncGenerator[Volume, None]:
        async for volume in get_volumes(request, file_system_type_or_type_name):
            yield volume


class InMemoryDatabase(Database, abc.ABC):
    """
    In-memory store of desktop objects and content.
    """

    def __init__(self, config: Optional[configparser.ConfigParser], **kwargs) -> None:
        """
        Initializes the in-memory database.

        :param config: a configparser.ConfigParser object.
        """
        super().__init__(config, **kwargs)
        self.__desktop_objects: Dict[str, List[DesktopObjectDict]] = {}
        self.__content: Dict[str, Dict[str, bytes]] = {}

    def add_desktop_objects(self, data: Mapping[str, List[DesktopObjectDict]] | None):
        """
        Adds the given desktop objects to the given collection. If the collection does not exist, add that collection
        along with its objects.

        :param data: A dictionary whose keys are collections and whose contents are desktop objects
        """
        for coll, objs in (data or {}).items():
            if coll in self.__desktop_objects:
                self.__desktop_objects[coll].extend(deepcopy(objs))
            else:
                self.__desktop_objects.update({coll: deepcopy(objs)})
        # self.__desktop_objects.update(deepcopy(data) if data is not None else {})

    def get_desktop_objects_by_collection(self, coll: str) -> List[DesktopObjectDict]:
        return deepcopy(self.__desktop_objects.get(coll, []))

    def get_desktop_object_by_collection_and_id(self, coll: str, id_: Optional[str]) -> Optional[DesktopObjectDict]:
        return deepcopy(next((d for d in self.__desktop_objects.get(coll, []) if d['id'] == id_), None))

    def update_desktop_object_by_collection_and_id(self, coll: str, id_: Optional[str],
                                                   new_value: DesktopObjectDict):
        """
        Updates the desktop object at the given location.

        :param coll: The collection in which the desktop object is located
        :param id_: The ID of the desktop object
        :param new_value: The new value of the desktop object
        """
        index = next((i for i, d in enumerate(self.__desktop_objects.get(coll, [])) if d['id'] == id_), None)
        if index is not None:
            self.__desktop_objects[coll][index] = new_value

    def remove_desktop_object_by_collection_and_id(self, coll: str, id_: Optional[str]):
        """
        Removes the desktop object (and its associated content) at the given location.

        :param coll: The collection in which the desktop object is located
        :param id_: The ID of the desktop object
        """
        index = next((i for i, d in enumerate(self.__desktop_objects.get(coll, [])) if d['id'] == id_), None)
        if index is not None:
            del self.__desktop_objects[coll][index]
            if coll in self.__content and id_ in self.__content[coll]:
                self.__content[coll].pop(id_)

    def add_content(self, content: Mapping[str, Mapping[str, bytes]] | None):
        """
        Adds the given content to the given collection. If there already is content for the object at the ID, replaces
        the content with new content.

        :param content: A dictionary whose keys are collections and whose values are dictionaries whose keys are the IDs
        of their corresponding desktop objects and whose values are the content
        """
        for coll, data in (content or {}).items():
            if coll in self.__content:
                self.__content[coll].update(dict(data))
            else:
                self.__content.update({coll: dict(data)})

    def get_content_by_collection(self, coll: str) -> Optional[Dict[str, bytes]]:
        return copy(self.__content.get(coll, None))

    def get_content_by_collection_and_id(self, coll: str, id_: str) -> Optional[bytes]:
        if (result := self.__content.get(coll, None)) is not None:
            return result.get(id_, None)
        else:
            return None


async def get_file_system_and_credentials_from_volume(request: Request, volume_id: Optional[str],
                                                      file_system_type: Type[FileSystemTypeVar],
                                                      credential_type: Optional[Type[CredentialTypeVar]] = None) -> \
Tuple[FileSystemTypeVar, Optional[CredentialTypeVar]]:
    """
    Get the file system and credentials for the given volume.

    :param request: the aiohttp request (required).
    :param volume_id: a volume id string (required).
    :param file_system_type: the type of file system (required).
    :param credential_type: the type of credential (optional)
    :return: a tuple containing a FileSystem object and, if one exists, a Credentials object (or None if one does not).
    :raise ValueError: if no volume with that id exists, no file system exists for the given volume, or the volumes's
    credentials were not found.
    """
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    volume, volume_url = await _get_volume(request.app, volume_id, headers)
    if volume is None:
        raise ValueError(f'No volume with id {volume_id}')
    if volume_url is None:
        raise ValueError(f'Volume {volume_id} has no URL')
    fs_url = await type_to_resource_url(request, FileSystem)
    assert fs_url is not None, 'No file system service registered'
    file_system = await client.get(request.app,
                                   URL(fs_url) / 'bytype' / file_system_type.get_type_name() / 'byname' / volume.file_system_name,
                                   file_system_type,
                                   headers=headers)
    if file_system is None:
        raise ValueError(f"Volume {volume.id}'s file system {volume.file_system_name} does not exist")
    return file_system, await _get_credentials(request.app, volume, credential_type, headers)


async def has_volume(request: Request, volume_id: Optional[str] = None,
                     headers: Optional[Mapping[str, str]] = None) -> Response:
    if volume_id is None:
        if 'volume_id' in request.match_info:
            volume_id_ = request.match_info['volume_id']
        elif 'id' in request.match_info:
            volume_id_ = request.match_info['id']
        else:
            volume_id_ = None
    else:
        volume_id_ = volume_id
    if volume_id_ is not None:
        volume_url = await type_to_resource_url(request, Volume)
        assert volume_url is not None, 'No volume service registered'
        volume = await client.get(request.app, URL(volume_url) / volume_id_, Volume, headers=headers)
        if volume is None:
            return response.status_not_found()
        return response.status_ok()
    else:
        return response.status_not_found()


async def get_volumes(request: Request, file_system_type_or_type_name: Union[str, type[FileSystem]]) -> AsyncGenerator[
    Volume, None]:
    """
    Gets the volumes accessible to the current user that have the provided filesystem type.

    :param request: the aiohttp request (required).
    :param file_system_type_or_type_name: the filesystem type or type name.
    :return: an async generator of Volume objects.
    :raises ValueError: if no volume microservice is registered.
    :raises TypeError: if file_system_type_or_type_name is a type but not a FileSystem.
    """
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    volume_url = await type_to_resource_url(request, Volume)
    assert volume_url is not None, 'No Volume service registered'
    file_system_type_ = desktop_object_type_or_type_name_to_type(file_system_type_or_type_name)
    if not issubclass(file_system_type_, FileSystem):
        raise TypeError(f'Provided file_system_type_or_type_name is a {file_system_type_} not a FileSystem')
    get_volumes_url = URL(volume_url) / 'byfilesystemtype' / file_system_type_.get_type_name()

    async for volume in client.get_all(request.app, get_volumes_url, Volume, headers=headers):
        yield volume


async def get_options(request: Request, methods: List[str], fn: Callable[[Request], Awaitable[Response]]):
    """
    Responds to an OPTIONS request. It calls the provided function, checks for the 200 status code, and if 200 is
    returned, returns a response with a 200 status code and an Allow header. The function should check if a REST API
    endpoint would return a 200 status code if called.

    :param request: the HTTP request (required).
    :param methods: a list of methods to include in the Allow header (required).
    :param fn: the function to call.
    :return: the HTTP response.
    """
    resp = await fn(request)
    if resp.status == 200:
        return await response.get_options(request, methods)
    else:
        headers: Union[Mapping[Union[str, istr], str], None] = {hdrs.CONTENT_TYPE: 'text/plain; charset=utf-8'}
        return response.status_generic(status=resp.status, body=resp.text, headers=headers)


async def _get_volume(app: web.Application, volume_id: Optional[str], headers: Union[Mapping[Union[str, istr], str], CIMultiDict[str], CIMultiDictProxy[str], None] = None) -> Tuple[Optional[Volume], Optional[Union[str, URL]]]:
    """
    Gets the volume with the provided id.

    :param app: the aiohttp app (required).
    :param volume_id: the id string of a volume.
    :param headers: any headers.
    :return: a two-tuple with either the Volume and its URL, or (None, None).
    :raise ValueError: if there is no volume with the provided volume id.
    """
    if volume_id is not None:
        volume_url = await client.get_resource_url(app, Volume)
        if volume_url is None:
            raise ValueError('No Volume service registered')
        volume = await client.get(app, URL(volume_url) / volume_id, Volume, headers=headers)
        if volume is None:
            raise ValueError(f'No volume with volume_id={volume_id}')
        return volume, volume_url
    else:
        return None, None


async def _get_credentials(app: web.Application, volume: Volume, cred_type: Optional[Type[CredentialTypeVar]] = None,
                           headers: Optional[Mapping] = None) -> Optional[CredentialTypeVar]:
    """
    Gets a credential specified in the provided volume, or if there is none, a credential with the where attribute set
    to the volume's URL.

    :param app: the aiohttp app (required).
    :param volume: the Volume (required).
    :param volume_url: the volume's URL (required).
    :param cred_type: The Credential's Type to be instantiated
    :param headers: any headers.
    :return: the Credentials, or None if the volume has no credentials.
    :raise ValueError: if the volume's credentials were not found.
    """
    if volume.credential_id is not None:
        cred_url = await client.get_resource_url(app, Credentials)
        assert cred_url is not None, 'No credentials service registered'
        credential = await client.get(app, URL(cred_url) / volume.credential_id,
                                      type_or_obj=cred_type if cred_type else Credentials, headers=headers)
        if credential is not None:
            return credential
        else:
            raise ValueError(f'Credentials {volume.credential_id} not found')
    else:
        return None


class DatabaseManager(ABC):
    """
    Abstract base class for database managers. These classes start a database, load data into it, return a Database
    object for manipulating the data, and delete the data. All subclasses of DatabaseManager must have a no-arg
    constructor, and they are expected to be immutable.
    """

    def __init__(self):
        self.__started = False

    def start_database(self, context_manager: ExitStack) -> None:
        """
        Starts the database. The provided context manager will destroy the database automatically. Override this
        method to start a database, such as in a docker container. Place the super() call after the database is
        already started.

        :param context_manager: a context manager for creating and destroying the database (required).
        """
        self.__started = True

    @property
    def started(self) -> bool:
        return self.__started

    def get_env_vars(self, ) -> Dict[str, str]:
        """
        Gets environment variables to connect to this database. This default implementation
        returns an empty dict. This method may only be called after the start_database() method. Override this method
        to return a dictionary of environment variable name-value pairs.

        :return: a str->str dict.
        """
        return {}

    def get_config_file_section(self) -> str:
        """
        Creates a HEA configuration file section for connecting to this database. This default implementation returns
        an empty string. This method may only be called after the start_database() method.

        :return: a string.
        """
        return ''

    @abstractmethod
    def insert_all(self, desktop_objects: Optional[dict[str, list[DesktopObjectDict]]],
                   content: Optional[dict[str, dict[str, bytes]]]):
        """
        Inserts all data and content. Failure may put the object in an inconsistent state where one is properly
        inserted but the other is not. This method is not designed to be overridden.

        :raises KeyError: if an unexpected key was found in the data or the content.
        """
        pass

    def close(self):
        """
        Removes all data and content, and cleans up any other resources created by other methods of this object. This
        method is not designed to be overridden.
        """
        if self.started:
            self.delete_all()

    @classmethod
    def get_environment_to_remove(cls) -> list[str]:
        """
        Gets any environment variables that need to be removed temporarily for the database.

        :return: a list of environment variable names, or the empty list.
        """
        return []

    @classmethod
    def get_environment_updates(cls) -> dict[str, str]:
        """
        Gets a newly created dict with any environment variables that are needed by the database.

        :return: environment variable name -> value dict, or the empty dict if no environment variables are needed.
        """
        return {}

    @classmethod
    @contextmanager
    def environment(cls):
        with modified_environ(*cls.get_environment_to_remove(), **cls.get_environment_updates()):
            yield

    @classmethod
    def get_context(cls) -> list[AbstractContextManager]:
        """
        Gets a newly created list of context managers, or the empty list if there are none. This method is called by
        the context() context manager, which instantiates any context managers in the list.
        """
        return []

    @classmethod
    @contextmanager
    def context(cls):
        with ExitStack() as stack:
            for context_ in cls.get_context():
                stack.enter_context(context_)
            yield

    @abstractmethod
    def delete_all(self):
        pass

    @abstractmethod
    @contextmanager
    def database(self, config: configparser.ConfigParser = None) -> Generator[Database, None, None]:
        """
        Context manager that creates the corresponding Database object. Override this method to return a Database
        instance. The database object will be closed automatically.

        :param config: HEA configuration.
        :return: the database object.
        """
        pass


class MicroserviceDatabaseManager(DatabaseManager, ABC):
    """
    Abstract base class for database managers. These classes start a database, load data into it, return a Database
    object for manipulating the data, and delete the data. All subclasses of TestDatabaseManager must have a no-arg
    constructor, and they are expected to be immutable.
    """

    def insert_desktop_objects(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]]):
        """
        Inserts data into the database. The start_database() method must be called before calling this method. The
        default implementation does nothing and is expected to be overridden with an implementation for a specific
        database technology. Implementations should anticipate multiple inheritance. Call super(), and do not pass
        desktop object collections that are handled by this collection into the superclass' implementation.

        :param desktop_objects: a dict of collection -> list of desktop object dicts. Required.
        :raises KeyError: if an unexpected key was found in the data.
        """
        if not self.started:
            raise NotStartedError

    def insert_content(self, content: Optional[Mapping[str, Mapping[str, bytes]]]):
        """
        Inserts content into the database. The start_database() method must be called before calling this method.
        The default implementation does nothing and is expected to be overridden with an implementation for a specific
        database technology. Implementations should anticipate multiple inheritance. Call super(), and do not pass
        content collections that are handled by this collection into the superclass' implementation.

        :param content: a dict of collection -> dict of desktop object id -> content. Required.
        :raises KeyError: if an unexpected key was found in the content.
        """
        if not self.started:
            raise NotStartedError

    def insert_all(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]], content: Optional[Mapping[str, Mapping[str, bytes]]]):
        """
        Inserts all data and content. Failure may put the object in an inconsistent state where one is properly
        inserted but the other is not. This method is not designed to be overridden.

        :raises KeyError: if an unexpected key was found in the data or the content.
        """
        self.insert_desktop_objects(desktop_objects)
        self.insert_content(content)

    def delete_desktop_objects(self):
        """
        Deletes data from the database. The start_database() method must be called before calling this method. This
        should support being called multiple times, and after the first time have no effect. Override this method to
        delete the provided desktop objects from the database.

        :raises KeyError: if an unexpected key was found in the data.
        """
        if not self.started:
            raise NotStartedError

    def delete_content(self):
        """
        Deletes content from the database. The start_database() method must be called before calling this method. This
        should support being called multiple times, and after the first time have no effect. Override this method to
        delete the provided content from the database.

        :raises KeyError: if an unexpected key was found in the content.
        """
        if not self.started:
            raise NotStartedError

    def delete_all(self):
        try:
            self.delete_desktop_objects()
        finally:
            self.delete_content()
