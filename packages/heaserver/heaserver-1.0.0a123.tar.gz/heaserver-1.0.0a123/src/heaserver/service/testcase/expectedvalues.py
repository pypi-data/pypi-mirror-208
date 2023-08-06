"""
Functions for automatically generating expected values for unit and integration tests of HEA services.
"""
import copy
import logging
from typing import Dict, Any, List, Optional, cast, Mapping, Type
from heaserver.service import wstl
from yarl import URL
from dataclasses import dataclass
import uritemplate

from .collection import CollectionKey, query_fixture_collection
from ..uritemplate import tvars as extra_tvars
from ..db.database import MicroserviceDatabaseManager
from enum import Enum
from heaobject.root import is_primitive, is_primitive_list, is_heaobject_dict_list, is_heaobject_dict, HEAObjectDict, \
    Primitive, HEAObjectDictValue, MemberObjectDict, Union, DesktopObjectDict
from datetime import date, time
from heaserver.service.representor.cj import add_extended_property_values


class Action:
    def __init__(self,
                 name: str,
                 rel: list[str] | None = None,
                 url: str | None = None,
                 wstl_url: str | None = None,
                 itemif: str | None = None):
        self.__name = name
        self.__rel = list(str(r) for r in rel) if rel is not None else None
        self.__url = str(url) if url is not None else None
        if wstl_url is not None:
            self.__wstl_url = str(wstl_url)
        else:
            self.__wstl_url = self.__url
        self.__itemif = str(itemif) if itemif is not None else None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = str(name)

    @property
    def rel(self) -> list[str] | None:
        return list(self.__rel)

    @rel.setter
    def rel(self, rel: list[str] | None):
        if rel is not None:
            self.__rel = list(rel)
        else:
            self.__rel = None

    @property
    def url(self) -> str | None:
        return self.__url

    @url.setter
    def url(self, url: str | None):
        self.__url = str(url) if url is not None else None
        if url is not None and self.wstl_url is None:
            self.wstl_url = self.__url

    @property
    def itemif(self) -> str | None:
        return self.__itemif

    @itemif.setter
    def itemif(self, itemif=str | None):
        self.__itemif = str(itemif) if itemif is not None else None

    @property
    def wstl_url(self) -> str | None:
        return self.__wstl_url

    @wstl_url.setter
    def wstl_url(self, wstl_url: str | None):
        self.__wstl_url = str(wstl_url)


@dataclass
class Link:
    url: str
    rel: Optional[List[str]]


def body_post(fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
              coll: str | CollectionKey,
              default_db_manager_cls: Type[MicroserviceDatabaseManager]) \
    -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Create a Collection+JSON template from a data test fixture.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :return: a Collection+JSON template as a dict using the first object in the given mongodb collection. Replaces the
    object's name and display_name attribute values with 'tritimus' and 'Tritimus', respectively.
    """
    modified_data = {**query_fixture_collection(fixtures, coll, default_db_manager=default_db_manager_cls)[0],
                     **{'name': 'tritimus', 'display_name': 'Tritimus'}}
    if 'id' in modified_data:
        del modified_data['id']
    return _create_template(modified_data)


def body_put(fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
             coll: str | CollectionKey,
             default_db_manager_cls: Type[MicroserviceDatabaseManager]) \
    -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Create a Collection+JSON template from a data test fixture.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :return: a Collection+JSON template as a dict using the first object in the given mongodb collection. Replaces the
    object's description attribute value with 'A description'.
    """
    logger_ = logging.getLogger(__name__)
    data = query_fixture_collection(fixtures, coll, default_db_manager=default_db_manager_cls)[1]
    logger_.debug('Transforming into template %s', data)
    return _create_template({**data, **{'description': 'A description'}}, exclude=None)


def expected_one_wstl(fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
                      coll: str | CollectionKey,
                      wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                      default_db_manager_cls: Type[MicroserviceDatabaseManager],
                      get_actions: Optional[List[Action]] = None) -> List[Dict[str, Any]]:
    """
    Create a run-time WeSTL document from a data test fixture. The document will contain the first HEAObject dict in
    the given collection, and will contain a single action.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :param get_actions: the actions to include in the body of GET calls.
    :return: a run-time WeSTL document as a dict.
    """
    if get_actions is None:
        get_actions = []
    actions = []
    href_ = wstl_builder.href if wstl_builder.href else ''
    for action, action_name, action_rel, action_url, itemif in ((wstl_builder.find_action(a.name), a.name, a.rel, a.wstl_url, a.itemif) for a
                                                        in get_actions):
        if action is None:
            raise ValueError(f'No action with name {action_name}')
        for input in action.get('inputs', []):
            if optionsFromUrl := wstl.get_extended_property_value('optionsFromUrl', input):
                optionsFromUrl['href'] = 'http://localhost:8080' + optionsFromUrl.get('path', '')
        if action is None:
            raise ValueError(f'Action {action_name} does not exist')
        action = {**action,
                  'href': action_url if action_url else "http://localhost:8080",
                  'rel': action_rel if action_rel else []}
        if itemif is not None:
            action.setdefault('hea', {})['itemIf'] = itemif
        actions.append(action)
    obj = query_fixture_collection(fixtures, coll, default_db_manager=default_db_manager_cls)[0]
    return [{
        'wstl': {
            'data': [_wstl_data_transform(obj)],
            'hea': {'href': str(URL(href_) / str(obj['id']))},
            'actions': actions,
            'title': wstl_builder.design_time_document['wstl']['title']}}]


def expected_one(fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
                 coll: str | CollectionKey,
                 wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                 default_db_manager_cls: Type[MicroserviceDatabaseManager],
                 get_actions: Optional[List[Action]] = None) -> List[Dict[str, Dict[str, Any]]]:
    """
    Create a Collection+JSON document with the first HEAObject from a mongodb collection in the given data test fixture.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :param get_actions: the actions to include in the body of GET calls.
    :return: a list containing Collection+JSON template as a dict using the first object in the given mongodb collection.
    Replaces the object's description attribute value with 'A description'.
    """
    obj = query_fixture_collection(fixtures, coll, default_db_manager=default_db_manager_cls)[0]
    id_ = str(obj['id'])
    href = URL(wstl_builder.href if wstl_builder.href else '') / id_
    get_actions_ = get_actions or []

    def item_links() -> List[Dict[str, Any]]:
        links = []
        for action, action_name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                              get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name}')
            if url is not None:
                match = extra_tvars(route=url, url=str(href))
            else:
                match = {}
            targets = action.get('target', '').split()
            if 'item' in targets and 'read' in targets and 'cj' in targets:
                links.append({
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, {k: v for k, v in (match | obj).items() if
                                                     isinstance(v, (int, float, str))}) if url else str(href),
                    'rel': ' '.join(rel)
                })
        return links

    def item_link() -> Dict[str, Any]:
        for action, action_name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                              get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name}')
            if url is not None:
                match = extra_tvars(route=url, url=URL(href).path)
            else:
                match = {}
            targets = action.get('target', '').split()
            if 'item' in targets and 'href' in targets and 'cj' in targets:
                return {
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, {k: v for k, v in (match | obj).items() if
                                                     isinstance(v, (int, float, str))}) if url else str(href),
                    'rel': ' '.join(rel),
                    'readOnly': 'true'
                }
        return {}

    def top_level_links() -> List[Dict[str, Any]]:
        links = []
        for action, action_name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                              get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name} in get_actions')
            if url is not None:
                match: Mapping = extra_tvars(route=url, url=URL(href).path)
            else:
                match = {}
            targets = action.get('target', '').split()
            if action['type'] == 'safe' and 'app' in targets and 'cj' in targets and (
                'inputs' not in action or not action['inputs']):
                links.append({
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, match | {'id': id_}) if url else str(href),
                    'rel': ' '.join(rel)
                })
        return links

    def queries() -> List[Dict[str, Any]]:
        queries = []
        for action, action_name, rel in ((wstl_builder.find_action(a.name), a.name, a.rel) for a in get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name} in get_actions')
            targets = action.get('target', '').split()
            if 'inputs' in action and action['type'] == 'safe' and 'list' in targets and 'cj' in targets:
                q = {'rel': ' '.join(action['rel']),
                     'href': action['href'],
                     'prompt': action.get('prompt', ''),
                     'data': []}
                inputs_ = action['inputs']
                for i in range(len(inputs_)):
                    d = inputs_[i]
                    nm = d.get('name', 'input' + str(i))
                    rtn = {
                        'name': nm,
                        'value': d.get('value'),
                        'prompt': d.get('prompt', nm),
                        'required': d.get('required', False),
                        'readOnly': d.get('readOnly', False),
                        'pattern': d.get('pattern')
                    }
                    optionsFromUrl = wstl.get_extended_property_value('optionsFromUrl', d)
                    if optionsFromUrl is not None:
                        optionsFromUrl['href'] = 'http://localhost:8080' + optionsFromUrl['path']
                    add_extended_property_values(action, rtn)
                    q['data'].append(rtn)
                queries.append(q)
        return queries

    item_link_ = item_link()

    data_: List[Dict[str, Any]] = []
    for x, y in obj.items():
        _data_append(data_, x, y)
    collection: Dict[str, Any] = {
        'collection': {
            'href': str(href),
            'items': [{'data': data_,
                       'links': item_links()}],
            'version': '1.0'}}
    if item_link_:
        if 'rel' in item_link_:
            collection['collection']['items'][0]['rel'] = item_link_['rel']
        collection['collection']['items'][0]['href'] = item_link_['href']
    top_level_links_ = top_level_links()
    if top_level_links_:
        collection['collection']['links'] = top_level_links_
    queries_ = queries()
    if queries_:
        collection['collection']['queries'] = queries_
    for action, action_name, rel in ((wstl_builder.find_action(a.name), a.name, a.rel) for a in get_actions_):
        if action is None:
            raise ValueError(f'Invalid action name in get_all_actions {action_name}')
        _set_collection_template(action, collection, obj, 1, rel)
    return [collection]


def expected_opener_body(
    fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
    coll: str | CollectionKey,
    wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
    default_db_manager_cls: Type[MicroserviceDatabaseManager],
    get_actions: Optional[List[Action]] = None,
    opener_link: Optional[Link] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Create a Collection+JSON document with the first HEAObject from a mongodb collection in the given data test fixture,
    including an opener link.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :param get_actions: the actions to include in the body of GET calls.
    :param opener_link: link for an opener choice. If None or omitted, this function will return None.
    :return: a list containing the first object in the fixture and mongodb collection as a Collection+JSON template as
    a dict, or None if no opener link was passed in.
    """
    if opener_link:
        body = expected_one(fixtures, coll, wstl_builder, default_db_manager_cls, get_actions=get_actions)
        coll_ = body[0]['collection']
        coll_.pop('template', None)
        coll_['href'] = coll_['href'] + '/opener'
        coll_['items'][0]['links'] = [
            {'prompt': 'Open', 'href': opener_link.url, 'rel': ' '.join(opener_link.rel or [])}]
        logging.getLogger(__name__).debug('Expected opener body is %s', body)
        return body
    else:
        logging.getLogger(__name__).debug('No opener body')
        return None


def expected_one_duplicate_form(
    fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
    coll: str | CollectionKey,
    wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
    default_db_manager_cls: Type[MicroserviceDatabaseManager],
    duplicate_action_name: str,
    duplicate_action_rel: Optional[List[str]] = None,
    actions: list[Action] | None = None) -> List[Dict[str, Any]]:
    """
    Create a Collection+JSON document with the first HEAObject from the given mongodb collection in the given data test
    fixture. The returned Collection+JSON document will contain the HEAObject in the data section and a template
    for duplicating the HEAObject.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :param duplicate_action_name: the name of the service's duplicator action. Required but may be None to indicate that
    these objects do not support duplication.
    :param duplicate_action_rel: list of rel strings for the action. Optional.
    :return: a list of Collection+JSON templates as dicts.
    """
    if not duplicate_action_name:
        return None
    return _expected_one_form(fixtures, coll, wstl_builder, default_db_manager_cls, duplicate_action_name,
                              duplicate_action_rel, suffix='/duplicator', actions=actions)


def expected_all_wstl(fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
                      coll: str | CollectionKey,
                      wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                      default_db_manager_cls: Type[MicroserviceDatabaseManager],
                      get_all_actions: Optional[List[Action]] = None) -> List[Dict[str, Dict[str, Any]]]:
    """
    Create a run-time WeSTL document from a data test fixture. The document will contain all HEAObject dicts in
    the given collection, and it will contain a single action.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :param get_all_actions: the actions to include in the body of GET-all calls.
    :return: a run-time WeSTL document as a dict.
    """
    if get_all_actions is None:
        get_all_actions = []

    href_ = wstl_builder.href if wstl_builder.href else ''

    def runtime_actions():
        result = []
        for action, action_name, action_rel, action_url, itemif in ((wstl_builder.find_action(a.name), a.name, a.rel, a.wstl_url, a.itemif) for
                                                            a in get_all_actions):
            if action is None:
                raise ValueError(f'Action {action_name} does not exist')
            href = action_url if action_url else 'http://localhost:8080'
            action['href'] = href
            action['rel'] = action_rel if action_rel else []
            for input in action.get('inputs', []):
                optionsFromUrl = wstl.get_extended_property_value('optionsFromUrl', input)
                if optionsFromUrl is not None:
                    optionsFromUrl['href'] = 'http://localhost:8080' + optionsFromUrl['path']
            if itemif is not None:
                action.setdefault('hea', {})['itemIf'] = itemif
            result.append(action)
        return result

    return [{
        'wstl': {
            'data': _wstl_data_transform(
                query_fixture_collection(fixtures, coll, default_db_manager=default_db_manager_cls)),
            'actions': runtime_actions(),
            'title': wstl_builder.design_time_document['wstl']['title'],
            'hea': {'href': href_ if href_ else '#'}
        }
    }]


def expected_all(fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
                 coll: str | CollectionKey,
                 wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                 default_db_manager_cls: Type[MicroserviceDatabaseManager],
                 get_all_actions: Optional[List[Action]] = None) -> List[Dict[str, Any]]:
    """
    Create a list of Collection+JSON documents with all HEAObjects from a mongodb collection in the given data test fixture.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :param get_all_actions: the actions to include in the body of GET-all calls.
    :return: a list of Collection+JSON dicts.
    """
    if get_all_actions is None:
        get_all_actions_ = []
    else:
        get_all_actions_ = get_all_actions

    href_ = wstl_builder.href if wstl_builder.href else ''

    def item_links(obj: DesktopObjectDict):
        links = []
        for action, name, rel, route in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                         get_all_actions_):
            if action is None:
                raise KeyError(f'No action found with name {name}')
            if route is not None:
                match = extra_tvars(route=route, url=href_)
            else:
                match = {}
            targets = action.get('target', '').split()
            if 'item' in targets and 'read' in targets and 'cj' in targets:
                links.append({
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(route, match | obj) if route else str(URL(href_) / obj['id']),
                    'rel': ' '.join(rel)
                })
        return links

    def item_link(obj: DesktopObjectDict):
        for action, name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                       get_all_actions_):
            if action is None:
                raise KeyError(f'No action found with name {name}')
            if url is not None:
                match = extra_tvars(route=url, url=URL(href_).path)
            else:
                match = {}
            targets = action.get('target', '').split()
            if 'item' in targets and 'href' in targets and 'cj' in targets:
                return {
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, match | obj) if url else str(URL(href_) / obj['id']),
                    'rel': ' '.join(rel),
                    'readOnly': 'true'
                }
        return {}

    def top_level_links():
        links = []
        for action, rel, url in ((wstl_builder.find_action(a.name), a.rel or [], a.url) for a in get_all_actions_):
            targets = action.get('target', '').split()
            if action['type'] == 'safe' and 'app' in targets and 'cj' in targets and (
                'inputs' not in action or not action['inputs']):
                links.append({
                    'prompt': action['prompt'],
                    'href': url if url else str(URL(href_) / ''),
                    'rel': ' '.join(rel)
                })
        return links

    items = []
    collection = query_fixture_collection(fixtures, coll, default_db_manager=default_db_manager_cls)
    for f in collection:
        data_: List[Dict[str, Any]] = []
        id_ = f['id']
        item_link_ = item_link(f)
        for x, y in f.items():
            _data_append(data_, x, y)
        item = {'data': data_,
                'links': item_links(f)}
        if item_link_:
            if 'rel' in item_link_:
                item['rel'] = item_link_['rel']
            item['href'] = item_link_['href']
        items.append(item)

    collection_doc = {'collection': {'href': str(wstl_builder.href if wstl_builder.href else '#'),
                                     'items': items,
                                     'version': '1.0'}}
    for action, action_name, rel in ((wstl_builder.find_action(a.name), a.name, a.rel) for a in get_all_actions_):
        if action is None:
            raise ValueError(f'Invalid action name in get_all_actions {action_name}')
        _set_collection_template(action, collection_doc, f, len(collection), rel)
    top_level_links_ = top_level_links()
    if top_level_links_:
        collection_doc['collection']['links'] = top_level_links_
    return [collection_doc]


def expected_values(fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
                    coll: str | CollectionKey,
                    wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                    duplicate_action_name: str | None,
                    href: Optional[Union[str, URL]],
                    get_actions: Optional[List[Action]] = None,
                    get_all_actions: Optional[List[Action]] = None,
                    opener_link: Optional[Link] = None,
                    default_db_manager_cls: Type[MicroserviceDatabaseManager] = MicroserviceDatabaseManager,
                    duplicate_action_actions: list[Action] | None = None,
                    exclude: list[str] | None = None) -> Dict[str, Any]:
    """
    Generate a dict of all the expected values for passing into the mongotestcase and mockmongotestcase
    get_test_case_cls function.

    :param fixtures: the data to load into the database, as a map of collection name -> list of desktop object dicts.
    Required.
    :param coll: the collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param duplicate_action_name: the name of the service's duplicator action. Optional.
    :param href: the resource's URL. If None, then /{coll} is used as the resource_path.
    :param get_actions: optional list of actions for GET calls.
    :param get_all_actions: optional list of actions for GET-all calls.
    :param opener_link: optional link representing a choice for opening the HEA object.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Defaults to
    DatabaseManager.
    :return: a dict of keyword argument name -> Collection+JSON dict or WeSTL document dict, where the keyword arguments
    match those of the mongotestcase and mockmongotestcase get_test_case_cls functions.
    """
    wstl_builder_ = copy.deepcopy(wstl_builder)
    wstl_builder_.href = str(href) if href is not None else None
    result = {}
    if not exclude or ('body_put' not in exclude):
        body_put_ = body_put(fixtures, coll, default_db_manager_cls)
        content_id = next((e.get('value') for e in body_put_['template']['data'] if e['name'] == 'id'), None)
        result['body_put'] = body_put_
        result['content_id'] = content_id
    if not exclude or ('body_post' not in exclude):
        result['body_post'] = body_post(fixtures, coll, default_db_manager_cls)
    if not exclude or ('expected_one_wstl' not in exclude):
        result['expected_one_wstl'] = expected_one_wstl(fixtures, coll, wstl_builder_, default_db_manager_cls,
                                                        get_actions=get_actions)
    if not exclude or ('expected_one' not in exclude):
        result['expected_one'] = expected_one(fixtures, coll, wstl_builder_, default_db_manager_cls,
                                              get_actions=get_actions)
    if not exclude or ('expected_one_duplicate_form' not in exclude):
        result['expected_one_duplicate_form'] = expected_one_duplicate_form(fixtures, coll, wstl_builder_,
                                                                   default_db_manager_cls, duplicate_action_name,
                                                                   actions=duplicate_action_actions)
    if not exclude or ('expected_all_wstl' not in exclude):
        result['expected_all_wstl'] = expected_all_wstl(fixtures, coll, wstl_builder_, default_db_manager_cls,
                                               get_all_actions=get_all_actions)
    if not exclude or ('expected_all' not in exclude):
        result['expected_all'] = expected_all(fixtures, coll, wstl_builder_, default_db_manager_cls,
                                     get_all_actions=get_all_actions)
    if not exclude or ('expected_opener' not in exclude):
        result['expected_opener'] = opener_link.url if opener_link is not None else None
    if not exclude or ('expected_opener_body' not in exclude):
        result['expected_opener_body'] = expected_opener_body(fixtures, coll, wstl_builder_, default_db_manager_cls,
                                                     get_actions=get_actions, opener_link=opener_link)
    return result


def _create_template(d: DesktopObjectDict, exclude=('id',)) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    return {'template': {'data': [z for x, y in d.items() if (not exclude or x not in exclude) for z in
                                  _nvpjson_property_to_cj_part_generator(x, y)]}}


def _template_data_generator(action, desktop_object_dict, len_fixtures=1):
    targets = action['target'].split()
    for input in action['inputs']:
        section = wstl.get_section(input)
        if optionsFromUrl := wstl.get_extended_property_value('optionsFromUrl', input):
            if 'href' not in optionsFromUrl:
                optionsFromUrl['href'] = 'http://localhost:8080' + optionsFromUrl['path']
        if 'add' in targets:
            yield _new_template_data_item(input, input['value'])

        elif len_fixtures == 1:
            nm = input['name']
            if nm in ('meta'):
                continue
            val = desktop_object_dict.get(section, []) if wstl.has_section(input) else desktop_object_dict.get(nm)
            if isinstance(val, list):
                if wstl.has_section(input):
                    if val:
                        yield _new_template_data_item(input, input.get('value')) | {
                            'index': -1,
                            'section': section
                        } | _section_prompt_key_value(input)
                        for i_, v in enumerate(val):
                            yield _new_template_data_item(input, v.get(nm, input.get('value'))) | {
                                'index': i_,
                                'section': section
                            } | _section_prompt_key_value(input)
                    else:
                        yield _new_template_data_item(input, input.get('value')) | {
                            'index': -1,
                            'section': section
                        } | _section_prompt_key_value(input)
                else:
                    yield _new_template_data_item(input, val)
            elif isinstance(val, dict):
                yield _new_template_data_item(input, val.get(nm, input.get('value'))) | {
                    'section': section
                } | _section_prompt_key_value(input)
            else:
                yield _new_template_data_item(input, val if val is not None else input.get('value'))
        elif not section:
            yield _new_template_data_item(input, input.get('value'))
        else:
            yield _new_template_data_item(input, input.get('value')) | {'section': section,
                                                                        'index': -1} | _section_prompt_key_value(input)


def _section_prompt_key_value(i):
    epv = wstl.get_extended_property_value('sectionPrompt', i)
    return {'sectionPrompt': epv} if epv is not None else {}


def _new_template_data_item(i: dict[str, Any], value: Any) -> dict[str, Any]:
    rtn = {'name': i['name'],
           'value': _value_append(value),
           'prompt': i.get('prompt', i['name']),
           'required': i.get('required', False),
           'pattern': i.get('pattern'),
           'readOnly': i.get('readOnly', False)}
    add_extended_property_values(i, rtn)
    return rtn


def _set_collection_template(action, collection_doc, fixture, len_fixtures, rel):
    """
    Adds a template object to the provided Collection+JSON document.

    :param action:
    :param collection_doc:
    :param fixture:
    :param len_fixtures:
    :param rel:
    """
    targets = action['target'].split()
    if 'cj-template' in targets:
        template = {'data': [d for d in _template_data_generator(action, fixture, len_fixtures)],
                    'prompt': action.get('prompt', action['name']),
                    'rel': ' '.join(rel) if rel is not None else ''}
        collection_doc['collection']['template'] = template


def _expected_one_form(
    fixtures: Mapping[str, List[DesktopObjectDict]] | Mapping[CollectionKey, List[DesktopObjectDict]],
    coll: str | CollectionKey,
    wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
    default_db_manager_cls: Type[MicroserviceDatabaseManager],
    action_name: str,
    action_rel: Optional[List[str]] = None,
    suffix: str = None,
    actions: Optional[List[Action]] = None) -> List[Dict[str, Any]]:
    """
    Create a Collection+JSON document with the first HEAObject from the given mongodb collection in the given data test
    fixture. The returned Collection+JSON document will contain the HEAObject in the data section and a template
    containing that HEAObject's values.

    :param fixtures: mongodb collection name/key -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name or key to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param default_db_manager_cls: The database manager to use if the collection key is a string. Required.
    :param action_name: the name of the action that causes creation of the template. Required.
    :param action_rel: list of rel strings for the action. Optional.
    :return: a list of Collection+JSON templates as dicts.
    """
    action = wstl_builder.find_action(action_name)
    if action is None:
        raise ValueError(f'Action {action_name} does not exist')
    obj = query_fixture_collection(fixtures, coll, default_db_manager=default_db_manager_cls)[0]
    id_ = str(obj['id'])
    href = URL(wstl_builder.href if wstl_builder.href else '') / (id_ + (suffix if suffix else ''))

    data_ = _heaobject_dict_to_collection_plus_json_data(obj)

    def get_link(a: Action):
        action_ = wstl_builder.find_action(a.name)
        if action_ is None:
            raise ValueError(f'Action {a.name} does not exist')
        if a.url is not None:
            match = extra_tvars(route=a.url, url=str(href))
        else:
            match = {}
        return {'href': uritemplate.expand(a.url, {k: v for k, v in (match | obj).items()
                                                   if isinstance(v, (int, float, str))}) if a.url else str(href),
                'rel': ' '.join(a.rel or []),
                'prompt': action_['prompt']}

    def set_default_values_from_headata_links():
        for link in links_:
            field_name = next((r.removeprefix('headata-') for r in link['rel'].split() if r.startswith('headata-')),
                              None)
            if field_name:
                for d in template_data:
                    if d['name'] == field_name:
                        d['value'] = link['href']

    links_ = [get_link(a) for a in actions or []]
    template_data = [d for d in _template_data_generator(action, obj)]
    set_default_values_from_headata_links()

    return [{
        'collection': {
            'version': '1.0',
            'href': str(href),
            'items': [
                {
                    'data': data_,
                    'links': links_
                }],
            'template': {
                'prompt': action.get('prompt', None),
                'rel': ' '.join(action_rel if action_rel else []),
                'data': template_data}
        }}]


def _heaobject_dict_to_collection_plus_json_data(obj):
    data_: List[Dict[str, Any]] = []
    for x, y in obj.items():
        _data_append(data_, x, y)
    return data_


def _wstl_data_transform(data: HEAObjectDictValue) -> HEAObjectDictValue:
    """
    Recursively goes through HEA object dicts, lists of HEA object dicts, primitive lists, and primitives, and replaces
    any enums and dates with strings as if the dicts had been serialized to JSON and deserialized back to dicts.

    :param data: HEA object dict, list of HEA object dicts, primitive list, or primitive.
    :return: a deep copy of the same data except with enums and dates replaced with strings.
    """
    if is_heaobject_dict_list(data):
        return [cast(MemberObjectDict, _wstl_data_transform(elt)) for elt in cast(List[MemberObjectDict], data)]
    elif is_heaobject_dict(data):
        return {x: cast(Union[Primitive, List[Primitive]], _wstl_data_transform(y)) for x, y in
                cast(MemberObjectDict, data).items()}
    elif is_primitive_list(data):
        return [cast(Primitive, _wstl_data_transform(d)) for d in cast(List[Primitive], data)]
    elif is_primitive(data):
        if isinstance(data, Enum):
            return str(data)
        elif isinstance(data, date):
            return data.isoformat()
        else:
            return data
    else:
        raise ValueError(str(data))


def _data_append(data: List[Dict[str, Any]], x: str, y: HEAObjectDictValue):
    if is_heaobject_dict(y):
        for xprime, yprime in cast(HEAObjectDict, y).items():
            _data_append_part(data, xprime, yprime, {'section': x})
    elif is_heaobject_dict_list(y):
        for i, yprime_ in enumerate(cast(List[HEAObjectDict], y)):
            for xprimeprime, yprimeprime in yprime_.items():
                _data_append_part(data, xprimeprime, yprimeprime, {'section': x, 'index': i})
    elif is_primitive(y) or is_primitive_list(y):
        _data_append_part(data, x, y)
    else:
        raise ValueError(f'{x}.{y}')


def _value_append(yy: HEAObjectDictValue) -> HEAObjectDictValue:
    if isinstance(yy, Enum):
        return str(yy)
    elif isinstance(yy, (date, time)):
        return yy.isoformat()
    else:
        return yy


def _data_append_part(data_: List[Dict[str, Any]], x: str, y: HEAObjectDictValue,
                      extra: Optional[Dict[str, Any]] = None):
    if isinstance(y, list):
        y_: Any = [_value_append(yy) for yy in y]
    else:
        y_ = _value_append(y)
    if not extra:
        extra = {}
    data_.append({
        'display': False if x == 'id' else True,
        'name': x,
        'prompt': x,
        'value': y_,
        **extra
    })


def _nvpjson_property_to_cj_part_generator(section_or_name, value):
    if is_heaobject_dict(value):
        for xprime, yprime in value.items():
            yield {'name': xprime, 'value': yprime, 'section': section_or_name}
    elif is_primitive(value) or is_primitive_list(value):
        yield {'name': section_or_name, 'value': value}
    elif is_heaobject_dict_list(value):
        for i, yprime in enumerate(value):
            for xprimeprime, yprimeprime in yprime.items():
                yield {'name': xprimeprime, 'value': yprimeprime, 'section': section_or_name, 'index': i}
    else:
        raise ValueError(f'{section_or_name}.{value}')
