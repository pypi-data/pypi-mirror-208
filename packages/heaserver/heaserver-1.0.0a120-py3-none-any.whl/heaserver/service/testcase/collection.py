"""
Defines a collection, storing data about the objects in the collection and the database to which it is relevant.
"""

from heaobject.root import HEAObjectDict
from ..db.database import MicroserviceDatabaseManager

from typing import TypeVar, Any, Type, Mapping


class CollectionKey:
    """
    A key to a collection that contains its name and relevant database manager class. CollectionKeys should only ever
    be used in testing environments.
    """

    def __init__(self, *, name: str | None,
                 db_manager_cls: type[MicroserviceDatabaseManager] = MicroserviceDatabaseManager):
        """
        Creates a collection key with a provided name and a database manager class.

        :param name: The name of the collection. If None, the key refers to any collection relevant to the given
        database manager. Required (keyword-only).
        :param db_manager_cls: A MicroserviceDatabaseManager type to which the collection is relevant. Defaults to
        MicroserviceDatabaseManager (keyword-only).
        """
        if db_manager_cls is None:
            db_manager_cls = MicroserviceDatabaseManager
        if not issubclass(db_manager_cls, MicroserviceDatabaseManager):
            raise TypeError(
                f'db_manager_cls has incorrect type: expected {MicroserviceDatabaseManager}, was {db_manager_cls}')
        self.__name = str(name) if name is not None else None
        self.__db_manager_cls = db_manager_cls

    @property
    def name(self) -> str | None:
        """
        The collection key's name.
        """
        return self.__name

    @property
    def db_manager_cls(self) -> type[MicroserviceDatabaseManager]:
        """
        The collection key's database manager class. The default value is MicroserviceDatabaseManager.
        """
        return self.__db_manager_cls

    def coll_is_relevant_to(self, db_manager: MicroserviceDatabaseManager | Type[MicroserviceDatabaseManager]) -> bool:
        """
        Determines if the collection represented by this CollectionKey is relevant to the given database manager.
        :param db_manager: A DatabaseManager or DatabaseManager class.
        :return: True if the collection represented by this CollectionKey is relevant to the given database manager,
        otherwise False.
        """
        if isinstance(db_manager, type):
            return issubclass(db_manager, self.db_manager_cls)
        else:
            return isinstance(db_manager, self.db_manager_cls)

    def matches(self, other: 'str | CollectionKey',
                default_db_manager_cls: Type[MicroserviceDatabaseManager] = MicroserviceDatabaseManager) -> bool:
        """
        Determines if the collection represented by this CollectionKey is represented by a part or entirety of the
        other string or CollectionKey. Since all DatabaseManagers inherit relevant collections from their superclasses,
        the database manager of the other collection key may be a subclass of the DatabaseManager class stored with
        this CollectionKey and vice versa.

        :param other: the other collection key, as either a string or CollectionKey (required).
        :param default_db_manager_cls: if other is a string, then this database manager class is used as the
        database manager class for the other collection key. Defaults to DatabaseManager (i.e. match
        any DatabaseManager).
        :return: True if the other collection key matches this one, otherwise False.
        """
        if isinstance(other, CollectionKey):
            other_ = other
        else:
            other_ = CollectionKey(name=str(other), db_manager_cls=default_db_manager_cls)
        return (self.name == other_.name if self.name is not None and other_.name is not None else True) \
               and (issubclass(self.db_manager_cls, other_.db_manager_cls) or issubclass(other_.db_manager_cls,
                                                                                         self.db_manager_cls))

    def __str__(self):
        return f'CollectionKey(name={self.name}, db_manager_cls={self.db_manager_cls}'


def coll_is_relevant_to(key: str | CollectionKey,
                        db_manager: MicroserviceDatabaseManager | Type[MicroserviceDatabaseManager]) -> bool:
    """
    Determines whether the collection represented by the given collection key is relevant to the given database
    manager. If the collection is a string, True will be returned.

    :param key: a collection key as a string or CollectionKey (required).
    :param db_manager: either a DatabaseManager or DatabaseManager class (required).
    :return: True if the collection represented by the given collection key is relevant to the given database
    manager, otherwise False.
    """
    if isinstance(key, CollectionKey):
        return key.coll_is_relevant_to(db_manager)
    else:
        return CollectionKey(name=str(key)).coll_is_relevant_to(db_manager)


def query_fixture_collection(fixtures: Mapping[str, list[HEAObjectDict]] | Mapping[CollectionKey, list[HEAObjectDict]],
                             key: str | CollectionKey,
                             default_db_manager: MicroserviceDatabaseManager | Type[
                                 MicroserviceDatabaseManager] = MicroserviceDatabaseManager,
                             strict=True) -> list[HEAObjectDict]:
    """
    Get the collection with the given key.

    :param fixtures: The fixtures to query. Required.
    :param key: The name and database manager class must match those stored in the CollectionKey if
    key is a CollectionKey. If key is a string, then the database manager class is assumed to be default_db_manager.
    :param default_db_manager: The database manager to if the collection key is a string. Defaults to DatabaseManager.
    :param strict: If True, raises KeyError if nothing is found. If False, returns None if nothing is found. Defaults
    to True.
    :return: The objects in the collection that match with the given key, or the empty list if none do.
    """
    if fixtures is None:
        raise TypeError('fixtures may not be None')
    if isinstance(key, CollectionKey) and key.name is None:
        raise TypeError('the name of the CollectionKey may not be None when used as a parameter to '
                        'query_fixture_collection')
    result = query_fixtures(fixtures, default_db_manager=default_db_manager, strict=strict, key=key)
    if not result:
        return []
    else:
        return result[key.name if isinstance(key, CollectionKey) else key]


def query_content_collection(content: dict[str, dict[str, bytes]] | dict[CollectionKey, dict[str, bytes]],
                             key: str | CollectionKey,
                             default_db_manager: MicroserviceDatabaseManager | Type[
                                 MicroserviceDatabaseManager] = MicroserviceDatabaseManager,
                             strict=True) -> dict[str, bytes] | None:
    """
    Get the collection with the given key.

    :param content: The content dictionary to query. If None, returns the empty dictionary. Required.
    :param key: The name and database manager class must match those stored in the CollectionKey if
    key is a CollectionKey. If key is a string, then the database manager class is assumed to be default_db_manager.
    :param default_db_manager: The database manager to use if the collection key is a string. Defaults to
    DatabaseManager.
    :param strict: If True, raises KeyError if nothing is found. If False, returns None if nothing is found. Defaults
    to True.
    :return: The content in the collection that matches with the given key.
    """
    if content is None:
        raise TypeError('content may not be None')
    else:
        if isinstance(key, CollectionKey) and key.name is None:
            raise TypeError('the name of the CollectionKey may not be None when used as a parameter to '
                            'query_fixture_collection')
        result = query_content(content, default_db_manager=default_db_manager, strict=strict, key=key)
        if not result:
            return None
        elif isinstance(key, CollectionKey):
            return result[key.name]
        else:
            return result[key]


def query_fixtures(fixtures: Mapping[str, list[HEAObjectDict]] | Mapping[CollectionKey, list[HEAObjectDict]] | None,
                   default_db_manager: MicroserviceDatabaseManager | Type[
                       MicroserviceDatabaseManager] = MicroserviceDatabaseManager,
                   strict=False, *,
                   name: str | None = None,
                   db_manager: MicroserviceDatabaseManager | Type[MicroserviceDatabaseManager] | None = None,
                   key: str | CollectionKey | None = None) -> dict[str | None, list[HEAObjectDict]]:
    """
    Query a dictionary of fixtures by collection.

    :param fixtures: The fixtures to query. If the key to a collection is a string, then the database manager class
    will be assumed to be default_db_manager. If None, returns the empty dictionary. Required.
    :param default_db_manager: The database manager to if the collection key is a string. Defaults to DatabaseManager.
    :param strict: If True, raises KeyError if nothing is found. If False, an empty dictionary is returned. Defaults
    to False.
    :param name: If specified, the name of the collection must match the given name.
    :param db_manager: If specified, the database manager of the collection must be the given database manager, its
    class if it is an instance of a database manager, or a subclass.
    :param key: If specified, the name and database manager class must match those stored in the CollectionKey if
    key is a CollectionKey. If key is a string, it is the same as specifying name. Both name and db_manager are
    ignored if this argument is specified.
    :return: All the collections and their data that matches the given query parameters. Any CollectionKeys in the
    keys of the given fixtures are replaced with their names if key is either not specified or not a CollectionKey.
    """
    if isinstance(default_db_manager, type) and not issubclass(default_db_manager, MicroserviceDatabaseManager):
        raise TypeError(f'default_db_manager not a subclass of MicroserviceDatabaseManager; was a {default_db_manager}')
    if not isinstance(default_db_manager, type) and not isinstance(default_db_manager, MicroserviceDatabaseManager):
        raise TypeError(f'default_db_manager not a MicroserviceDatabaseManager; was a {default_db_manager}')
    if db_manager is not None:
        if isinstance(db_manager, type) and not issubclass(db_manager, MicroserviceDatabaseManager):
            raise TypeError(f'db_manager not a subclass of MicroserviceDatabaseManager; was a {default_db_manager}')
        if not isinstance(db_manager, type) and not isinstance(db_manager, MicroserviceDatabaseManager):
            raise TypeError(f'db_manager not a MicroserviceDatabaseManager; was a {db_manager}')
    if not fixtures:
        return {}
    key_ = key if isinstance(key, CollectionKey) else CollectionKey(name=str(key) if key is not None else None)
    if db_manager is None:
        db_manager_ = default_db_manager if isinstance(default_db_manager, type) else type(default_db_manager)
    else:
        db_manager_ = db_manager if isinstance(db_manager, type) else type(db_manager)
    coll_key = key_ if key else CollectionKey(name=str(name) if name is not None else None, db_manager_cls=db_manager_)
    result = {(coll.name if isinstance(coll, CollectionKey) else coll): data
              for coll, data in fixtures.items() if coll_key.matches(coll,
                                                                     default_db_manager_cls=
                                                                     default_db_manager
                                                                     if isinstance(default_db_manager, type)
                                                                     else type(default_db_manager))}
    if result:
        return result
    elif strict:
        raise KeyError(f'query result is empty: {key_}')
    else:
        return {}


def query_content(content: Mapping[str, Mapping[str, bytes]] | Mapping[CollectionKey, Mapping[str, bytes]] | None,
                  default_db_manager: MicroserviceDatabaseManager | Type[
                      MicroserviceDatabaseManager] = MicroserviceDatabaseManager,
                  strict=False, *,
                  name: str | None = None,
                  db_manager: MicroserviceDatabaseManager | Type[MicroserviceDatabaseManager] | None = None,
                  key: str | CollectionKey | None = None) -> dict[str | None, dict[str, bytes]]:
    """
    Query a dictionary of content by collection.

    :param content: The content dictionary to query. If the key to a collection is a string, then the database manager
    class will be assumed to be default_db_manager. If None, returns the empty dictionary. Required.
    :param default_db_manager: The database manager to use if the collection key is a string. Defaults to
    DatabaseManager.
    :param strict: If True, raises KeyError if nothing is found. If False, an empty dictionary is returned. Defaults
    to False.
    :param name: If specified, the name of the collection must match the given name.
    :param db_manager: If specified, the database manager of the collection must be the given database manager, its
    class if it is an instance of a database manager, or a subclass.
    :param key: If specified, the name and database manager class must match those stored in the CollectionKey if
    key is a CollectionKey. If key is a string, it is the same as specifying name. Both name and db_manager are
    ignored if this argument is specified.
    :return: All the collections and their content that matches the given query parameters. Any CollectionKeys in the
    keys of the given content dictionary are replaced with their names.
    """
    if isinstance(default_db_manager, type) and not issubclass(default_db_manager, MicroserviceDatabaseManager):
        raise TypeError(f'default_db_manager not a subclass of MicroserviceDatabaseManager; was a {default_db_manager}')
    if not isinstance(default_db_manager, type) and not isinstance(default_db_manager, MicroserviceDatabaseManager):
        raise TypeError(f'default_db_manager not a MicroserviceDatabaseManager; was a {default_db_manager}')
    if db_manager is not None:
        if isinstance(db_manager, type) and not issubclass(db_manager, MicroserviceDatabaseManager):
            raise TypeError(f'db_manager not a subclass of MicroserviceDatabaseManager; was a {default_db_manager}')
        if not isinstance(db_manager, type) and not isinstance(db_manager, MicroserviceDatabaseManager):
            raise TypeError(f'db_manager not a MicroserviceDatabaseManager; was a {db_manager}')
    if not content:
        return {}
    key_ = key if isinstance(key, CollectionKey) else CollectionKey(name=str(key) if key is not None else None)
    if db_manager is None:
        db_manager_ = default_db_manager if isinstance(default_db_manager, type) else type(default_db_manager)
    else:
        db_manager_ = db_manager if isinstance(db_manager, type) else type(db_manager)
    coll_key = key_ if key else CollectionKey(name=str(name) if name is not None else None, db_manager_cls=db_manager_)
    result = {(coll.name if isinstance(coll, CollectionKey) else coll): dict(data)
              for coll, data in content.items() if coll_key.matches(coll)}
    if result:
        return result
    elif strict:
        raise KeyError('query result is empty')
    else:
        return {}


_T = TypeVar('_T')


def simplify_collection_keys(collections: Mapping[str, _T] | Mapping[CollectionKey, _T]) -> dict[str | None, _T]:
    """
    Convert all CollectionKeys in the given collection dictionary to strings that are equal to their names.
    """
    return {(coll_key.name if isinstance(coll_key, CollectionKey) else coll_key): objs
            for coll_key, objs in collections.items()}


def validate_collection_keys(collections: Mapping[str, Any] | Mapping[CollectionKey, Any]):
    """
    Raises a TypeError if the provided collections' keys are not either all-strings or all-CollectionKeys.
    """
    if not all(isinstance(key_name, str) for key_name in collections.keys()) and not all(
        isinstance(key, CollectionKey) for key in collections.keys()):
        raise TypeError(
            f'collections must have either all-string or all-CollectionKey keys, but actually has {set(type(k) for k in collections.keys())}')


def convert_to_collection_keys(collections: Mapping[str, _T] | Mapping[CollectionKey, _T],
                               default_db_manager: MicroserviceDatabaseManager | type[
                                   MicroserviceDatabaseManager] = MicroserviceDatabaseManager) \
    -> dict[CollectionKey, _T]:
    """
    Creates a new collection dictionary with all string keys converted to CollectionKeys with the given default
    database manager. This acts like a shallow copy, i.e., the dictionary's values are not copied.

    :param collections: any mapping with either all-string or all-CollectionKey keys (required).
    :param default_db_manager: the MicroserviceDatabaseManager to use for converting the string keys (optional).
    :return: a dictionary of CollectionKey -> the same values as in collections.
    """
    db_manager = default_db_manager if isinstance(default_db_manager, type) else type(default_db_manager)
    return {(key if isinstance(key, CollectionKey) else CollectionKey(name=key, db_manager_cls=db_manager)): objs
            for key, objs in collections.items()}


def get_collection_key_from_name(collections: Mapping[CollectionKey, Any], name: str) -> CollectionKey | None:
    """
    Get the key to access the collection with the given name. If there are multiple collections with the same name,
    behavior is undefined because this should never happen. If there is no collection with the name, return None.
    """
    return next(iter([x for x in collections.keys() if x.name == name]), None)


def get_collection_from_name(collections: Mapping[str, Any] | Mapping[CollectionKey, Any],
                             name: str) -> str | CollectionKey | None:
    """
    Get the key to access the collection with the given name. If there are multiple collections with the same name,
    behavior is undefined because this should never happen. If there is no collection with the name, return None.
    """
    return next(iter([x for x in collections.keys() if (x.name if isinstance(x, CollectionKey) else str(x)) == name]),
                None)
