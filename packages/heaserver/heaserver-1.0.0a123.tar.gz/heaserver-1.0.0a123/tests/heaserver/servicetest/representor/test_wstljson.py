from heaserver.service.testcase.simpleaiohttptestcase import SimpleAioHTTPTestCase
from heaserver.service import wstl
from heaserver.service.representor import wstljson
from heaobject import user
from unittest import mock


class TestWstlJson(SimpleAioHTTPTestCase):

    async def setUpAsync(self):
        await super().setUpAsync()
        self.__body = {
            'items': [],
            'created': None,
            'derived_by_uri': None,
            'derived_from_uris': [],
            'description': None,
            'display_name': 'Reximus',
            'id': None,
            'invites': [],
            'modified': None,
            'name': 'reximus',
            'owner': user.NONE_USER,
            'shares': [],
            'source_uri': None,
            'type': 'heaobject.folder.Folder',
            'version': None
        }
        self.__request = mock.MagicMock()
        self.__request.match_info = {}
        self.maxDiff = None

    async def test_formats_default(self):
        wstl_builder = wstl.builder('servicetest', resource='representor/all.json')
        wstl_builder.href = 'http://localhost/test'
        actual = await wstljson.WeSTLJSON().formats(self.__request, wstl_builder())
        self._assert_json_string_equals('[{"wstl": {"hea": {"href": "http://localhost/test"}, "actions": []}}]', actual)

    async def test_formats_actions_but_no_data(self):
        wstl_builder = wstl.builder('servicetest', resource='representor/all.json')
        wstl_builder.href = 'http://localhost/test'
        wstl_builder.add_run_time_action(name='data-adapter-list', path='/folders/{folder_id}/items/{id}')
        actual = await wstljson.WeSTLJSON().formats(self.__request, wstl_builder())
        self._assert_json_string_equals('[{"wstl": {"hea": {"href": "http://localhost/test"}, "actions": [{"name": "data-adapter-list", "type": "safe", "target": "list", "prompt": "Data adapters", "href": "/folders/{folder_id}/items/{id}", "rel": []}]}}]', actual)

    async def test_formats_data_but_no_actions(self):
        wstl_builder = wstl.builder('servicetest', resource='representor/all.json')
        wstl_builder.data = self.__body
        wstl_builder.href = 'http://localhost/test'
        actual = await wstljson.WeSTLJSON().formats(self.__request, wstl_builder())
        self._assert_json_string_equals(
            '[{"wstl": {"hea": {"href": "http://localhost/test"}, "data": [{"items": [], "created": null, "derived_by_uri": null, "derived_from_uris": [], "description": null, "display_name": "Reximus", "id": null, "invites": [], "modified": null, "name": "reximus", "owner": "system|none", "shares": [], "source_uri": null, "type": "heaobject.folder.Folder", "version": null}], "actions": []}}]',
            actual)

    async def test_formats(self):
        wstl_builder = wstl.builder('servicetest', resource='representor/all.json')
        wstl_builder.add_run_time_action(name='data-adapter-list', path='/folders/{folder_id}/items/{id}')
        wstl_builder.data = self.__body
        wstl_builder.href = 'http://localhost/test'
        actual = await wstljson.WeSTLJSON().formats(self.__request, wstl_builder())
        self._assert_json_string_equals(
            '[{"wstl": {"hea": {"href": "http://localhost/test"}, "data": [{"items": [], "created": null, "derived_by_uri": null, "derived_from_uris": [], "description": null, "display_name": "Reximus", "id": null, "invites": [], "modified": null, "name": "reximus", "owner": "system|none", "shares": [], "source_uri": null, "type": "heaobject.folder.Folder", "version": null}], "actions": [{"name": "data-adapter-list", "type": "safe", "target": "list", "prompt": "Data adapters", "href": "/folders/{folder_id}/items/{id}", "rel": []}]}}]',
            actual)

    async def test_formats_nothing(self):
        wstl_builder = wstl.builder('servicetest', resource='representor/all.json')
        wstl_builder.href = 'http://localhost/test'
        actual = await wstljson.WeSTLJSON().formats(self.__request, wstl_builder())
        self._assert_json_string_equals(
            '[{"wstl": {"actions": [], "hea": {"href": "http://localhost/test"}}}]',
            actual)
