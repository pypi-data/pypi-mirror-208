import json
import os
import unittest
from typing import Optional

from appian_locust import AppianTaskSet
from appian_locust.helper import find_component_by_attribute_in_dict, find_component_by_index_in_dict
from appian_locust import logger
from locust import Locust, TaskSet

from .mock_client import CustomLocust
from .mock_reader import read_mock_file

log = logger.getLogger(__name__)


class TestInteractor(unittest.TestCase):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    form_content = read_mock_file("form_content_response.json")
    form_content_2 = read_mock_file("sites_record_nav.json")
    form_content_3 = read_mock_file("sites_record_recordType_resp.json")
    nested_dynamic_link_json = read_mock_file("nested_dynamic_link_response.json")
    response_with_start_process_link = read_mock_file("start_process_link_response.json")
    record_action_launch_form_before_refresh = read_mock_file("record_action_launch_form_before_refresh.json")
    record_action_refresh_response = read_mock_file("record_action_refresh_response.json")
    site_with_record_search_button = read_mock_file("site_with_record_search_button.json")
    site_with_expression_editor = read_mock_file("site_with_expression_editor.json")
    default_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    mobile_user_agent = "AppianAndroid/20.2 (Google AOSP on IA Emulator, 9; Build 0-SNAPSHOT; AppianPhone)"

    def setUpWithPath(self, base_path_override: Optional[str] = None) -> None:
        self.custom_locust = CustomLocust(Locust())
        parent_task_set = TaskSet(self.custom_locust)
        setattr(parent_task_set, "host", "")
        setattr(parent_task_set, "credentials", [["", ""]])
        setattr(parent_task_set, "auth", ["", ""])
        if base_path_override:
            setattr(parent_task_set, "base_path_override", base_path_override)

        self.task_set = AppianTaskSet(parent_task_set)

        self.task_set.on_start()

    def setUp(self) -> None:
        self.setUpWithPath()

    def test_get_primary_button_payload(self) -> None:
        output = self.task_set.appian._interactor.get_primary_button_payload(
            json.loads(self.form_content))
        self.assertIsInstance(output, dict)

    def test_unauthed_get_page(self) -> None:
        # Given
        expected_requests = self.custom_locust.get_request_list_as_method_path_tuple()
        expected_requests.append(("get", "/suite/whatever"))
        expected_requests.append(("get", "/suite/?signin=native"))
        expected_requests.append(("post", "/suite/auth?appian_environment=tempo"))
        # When
        self.task_set.appian._interactor.get_page("/suite/whatever")
        # Then
        self.assertEqual(expected_requests, self.custom_locust.get_request_list_as_method_path_tuple())

    def test_authed_get_page(self) -> None:
        # Given
        expected_requests = self.custom_locust.get_request_list_as_method_path_tuple()
        expected_requests.append(("get", "/suite/whatever"))
        cookies = {'JSESSIONID': 'abc'}
        self.custom_locust.set_response("/suite/whatever", 200, '', cookies=cookies)
        self.custom_locust.set_response("/suite/", 200, '', cookies=cookies)
        # When
        self.task_set.appian._interactor.get_page("/suite/whatever")
        # Then
        self.assertEqual(expected_requests, self.custom_locust.get_request_list_as_method_path_tuple())

    def test_500_but_still_logged_in_get_page(self) -> None:
        # Given
        expected_requests = self.custom_locust.get_request_list_as_method_path_tuple()
        expected_requests.append(("get", "/suite/500err"))
        expected_requests.append(("get", "/suite/"))
        self.custom_locust.set_response("/suite/500err", 500, '{}')
        self.custom_locust.set_response("/suite/", 200, '',
                                        cookies={'fake': 'fakeVal'})  # No appiancsrf cookie returned
        # When
        try:
            self.task_set.appian._interactor.get_page("/suite/500err")
        # Then
        except Exception as e:
            self.assertEqual(expected_requests, self.custom_locust.get_request_list_as_method_path_tuple())

    def test_base_path_override(self) -> None:
        # Given
        self.setUpWithPath('/ae')

        expected_requests = self.custom_locust.get_request_list_as_method_path_tuple()
        expected_requests.append(("get", "/ae/whatever"))
        cookies = {'JSESSIONID': 'abc'}
        self.custom_locust.set_response("/ae/whatever", 200, '', cookies=cookies)
        self.custom_locust.set_response("/ae/", 200, '', cookies=cookies)
        # When
        self.task_set.appian._interactor.get_page("/suite/whatever")
        # Then
        self.assertEqual(expected_requests, self.custom_locust.get_request_list_as_method_path_tuple())

    def test_500_and_not_logged_in_get_page(self) -> None:
        # Given
        expected_requests = self.custom_locust.get_request_list_as_method_path_tuple()
        expected_requests.append(("get", "/suite/500err"))
        expected_requests.append(("get", "/suite/"))
        expected_requests.append(("get", "/suite/?signin=native"))
        expected_requests.append(("post", "/suite/auth?appian_environment=tempo"))

        self.custom_locust.set_response("/suite/500err", 500, '{}')
        self.custom_locust.set_response("/suite/auth?appian_environment=tempo", 200, '')
        self.custom_locust.set_response("/suite/?signin=native", 200, '',
                                        cookies={'__appianCsrfToken': 'abc'})  # Default cookies when not logged in

        # When
        try:
            self.task_set.appian._interactor.get_page("/suite/500err")
        # Then
        except Exception as e:
            self.assertEqual(expected_requests, self.custom_locust.get_request_list_as_method_path_tuple())

    def test_click_record_link(self) -> None:
        record_link = find_component_by_attribute_in_dict("label", "Profile",
                                                          json.loads(self.form_content_2))
        self.custom_locust.set_response(
            "/suite/sites/record/nkB0AwAXQzsQm2O6Of7dMdydaKrNT9uUisGhgFHLyZXpnCB2kjcXoiFJRK5SlL5Bt_GvQEcqlclEadcUWUJ9fCR6GnV1GcZA0cQDe2zoojxnd4W1rs06fDnxgqf" +
            "-Pa9TcPwsNOpNrv_mvgEFfGrsSLB4BALxCD8JZ--/view/summary",
            200,
            "{}")

        output = self.task_set.appian._interactor.click_record_link(
            "/suite/sites/record/some_long_record_id/view/summary", record_link, {}, "")
        self.assertEqual(output, dict())

    def test_record_link_sites_record(self) -> None:
        record_link = find_component_by_attribute_in_dict("label", "Profile",
                                                          json.loads(self.form_content_2))

        mock = unittest.mock.Mock()
        setattr(self.task_set.appian._interactor, 'get_page', mock)

        self.task_set.appian._interactor.click_record_link(
            "/suite/sites/records/page/db/record/some-record-ref/view/summary", record_link, {}, "")

        mock.assert_called_once()
        # Assert get_page() called with first argument as the correct record link url
        recordRef = record_link.get("_recordRef")
        expected_record_link_url = f"('/suite/sites/records/page/db/record/{recordRef}/view/summary',)"

        self.assertEqual(f"{mock.call_args[0]}", expected_record_link_url)

    def test_record_link_interface_site(self) -> None:
        ui = read_mock_file("sites_page_interface.json")
        record_link = find_component_by_attribute_in_dict("testLabel", "RecordLinkTestLabel", json.loads(ui))

        mock = unittest.mock.Mock()
        setattr(self.task_set.appian._interactor, 'get_page', mock)

        self.task_set.appian._interactor.click_record_link(
            "/suite/rest/a/sites/latest/vendor-management/pages/opportunities/interface", record_link, {}, "")
        mock.assert_called_once()

        recordRef = record_link.get("_recordRef")
        expected_record_link_url = f"('/suite/rest/a/sites/latest/vendor-management/page/opportunities/record/{recordRef}/view/summary',)"
        self.assertEqual(f"{mock.call_args[0]}", expected_record_link_url)

    def test_record_link_sites_any_page(self) -> None:
        record_link = find_component_by_attribute_in_dict("label", "DA0G-P2A6",
                                                          json.loads(self.form_content_3))

        mock = unittest.mock.Mock()
        setattr(self.task_set.appian._interactor, 'get_page', mock)

        self.task_set.appian._interactor.click_record_link(
            "/suite/sites/textcolumns/page/500", record_link, {}, "")

        mock.assert_called_once()
        # Assert get_page() called with first argument as the correct record link url
        recordRef = record_link.get("_recordRef")
        expected_record_link_url = f"('/suite/sites/textcolumns/page/500/record/{recordRef}/view/summary',)"

        self.assertEqual(f"{mock.call_args[0]}", expected_record_link_url)

    def test_record_link_tempo_report(self) -> None:
        record_link = find_component_by_attribute_in_dict("label", "DA0G-P2A6",
                                                          json.loads(self.form_content_3))

        mock = unittest.mock.Mock()

        setattr(self.task_set.appian._interactor, 'get_page', mock)
        self.task_set.appian._interactor.click_record_link(
            "/suite/tempo/reports/view/oxy4ed", record_link, {}, "")

        mock.assert_called_once()
        # Assert get_page() called with first argument as the correct record link url
        recordRef = record_link.get("_recordRef")
        expected_record_link_url = f"('/suite/tempo/records/item/{recordRef}/view/summary',)"

        self.assertEqual(f"{mock.call_args[0]}", expected_record_link_url)

    def test_click_record_link_error(self) -> None:
        record_link = {"fake_component": "fake_attributes"}
        with self.assertRaises(Exception):
            self.task_set.appian._interactor.click_record_link(
                "", record_link, {}, "")

    def start_process_link_test_helper(self, is_mobile: bool = False) -> None:
        spl_component = find_component_by_attribute_in_dict("label", "Check In",
                                                            json.loads(self.response_with_start_process_link))
        mock = unittest.mock.Mock()
        process_model_opaque_id = spl_component.get("processModelOpaqueId")
        cache_key = spl_component.get("cacheKey")
        site_name = "covid-19-response-management"
        page_name = "home"

        setattr(self.task_set.appian._interactor, 'post_page', mock)
        self.task_set.appian._interactor.click_start_process_link(spl_component, process_model_opaque_id, cache_key,
                                                                  site_name, page_name, is_mobile)

        mock.assert_called_once()
        if not is_mobile:
            expected_spl_link_url = f"('/suite/rest/a/sites/latest/{site_name}/page/{page_name}/startProcess/{process_model_opaque_id}?cacheKey={cache_key}',)"
        else:
            expected_spl_link_url = f"('/suite/rest/a/model/latest/startProcess/{process_model_opaque_id}?cacheKey={cache_key}',)"
        self.assertEqual(f"{mock.call_args[0]}", expected_spl_link_url)

    def test_start_process_link(self) -> None:
        self.start_process_link_test_helper(is_mobile=False)

    def test_click_start_process_link_mobile(self) -> None:
        self.start_process_link_test_helper(is_mobile=True)

    def test_click_record_link_error_fake_uri(self) -> None:
        record_link = find_component_by_attribute_in_dict("label", "Profile",
                                                          json.loads(self.form_content_2))
        with self.assertRaises(Exception):
            self.task_set.appian._interactor.click_record_link(
                "fake_uri", record_link, {}, "")

    def test_click_dynamic_link(self) -> None:
        dyn_link = find_component_by_attribute_in_dict("label", "Settings",
                                                       json.loads(self.form_content_2))
        self.custom_locust.set_response("", 200, "{}")
        output = self.task_set.appian._interactor.click_link(
            "", dyn_link, {}, "")
        self.assertEqual(output, dict())

    def test_click_dynamic_link_error(self) -> None:
        dyn_link = {"fake_component": "fake_attributes"}
        with self.assertRaises(KeyError):
            self.task_set.appian._interactor.click_link(
                "", dyn_link, {}, "")

    def test_click_nested_dynamic_link(self) -> None:
        dyn_link = find_component_by_attribute_in_dict("label",
                                                       "I need to update my Account details",
                                                       json.loads(self.nested_dynamic_link_json))
        self.custom_locust.set_response("", 200, "{}")
        output = self.task_set.appian._interactor.click_link(
            "", dyn_link, {}, "")
        self.assertEqual(output, dict())

    def test_fill_textfield(self) -> None:
        text_title = find_component_by_attribute_in_dict("label", "Title",
                                                         json.loads(self.form_content))

        self.custom_locust.set_response("", 200, "{}")
        output = self.task_set.appian._interactor.fill_textfield(
            "", text_title, "something", {}, "", "")
        self.assertEqual(output, dict())

    def test_post_page(self) -> None:
        self.custom_locust.set_response("", 200, "{}")
        output = self.task_set.appian._interactor.post_page(
            "", payload={}, headers=None, label=None)
        self.assertEqual(output.json(), dict())

    def test_get_webapi(self) -> None:
        self.custom_locust.set_response(
            "?query=val", 200, '{"query": "result"}')
        output = self.task_set.appian._interactor.get_webapi(
            "", queryparameters={"query": "val"})
        self.assertEqual('{"query": "result"}', output.text)

    def test_change_user_to_mobile(self) -> None:
        # Given
        default_header = self.task_set.appian._interactor.setup_request_headers()
        self.assertEqual(default_header["User-Agent"], self.default_user_agent)

        # When
        self.task_set.appian._interactor.set_user_agent_to_mobile()
        new_header = self.task_set.appian._interactor.setup_request_headers()
        self.assertNotEqual(new_header, default_header)
        self.assertEqual(new_header["User-Agent"], self.mobile_user_agent)

    def test_change_default_user_to_desktop(self) -> None:
        # Given
        default_header = self.task_set.appian._interactor.setup_request_headers()
        self.assertEqual(default_header["User-Agent"], self.default_user_agent)

        # When
        self.task_set.appian._interactor.set_user_agent_to_desktop()
        new_header = self.task_set.appian._interactor.setup_request_headers()

        # Then
        self.assertEqual(new_header, default_header)

    def test_change_mobile_user_to_desktop(self) -> None:
        # Given
        default_header = self.task_set.appian._interactor.setup_request_headers()
        self.assertEqual(default_header["User-Agent"], self.default_user_agent)

        # Switch to mobile
        self.task_set.appian._interactor.set_user_agent_to_mobile()
        new_header = self.task_set.appian._interactor.setup_request_headers()
        self.assertNotEqual(new_header, default_header)
        self.assertEqual(new_header["User-Agent"], self.mobile_user_agent)

        # Switch back to desktop
        self.task_set.appian._interactor.set_user_agent_to_desktop()
        new_header = self.task_set.appian._interactor.setup_request_headers()

        # Then
        self.assertEqual(new_header, default_header)

    def test_click_record_search_button(self) -> None:
        component = find_component_by_index_in_dict("SearchBoxWidget", 1, json.loads(self.site_with_record_search_button))

        self.custom_locust.set_response("", 200, "{}")
        output = self.task_set.appian._interactor.click_record_search_button("", component, {}, "my_uuid", "")
        self.assertEqual(output, dict())

    def test_login_retry(self) -> None:
        # Given
        init_cookies = {'JSESSIONID': 'abc', '__appianCsrfToken': '123'}
        cookies_no_mcsrf = {'JSESSIONID': 'abc123',
                            '__appianCsrfToken': 'different cookie'}
        cookies_mcsrf = {'JSESSIONID': 'abc123',
                         '__appianCsrfToken': 'different cookie',
                         '__appianMultipartCsrfToken': 'these cookies'}

        self.custom_locust.set_response("/suite/", 200,
                                        '<html>A huge html blob</html>', cookies=init_cookies)
        self.custom_locust.set_response("/suite/auth?appian_environment=tempo", 200,
                                        '<html>A huge html blob</html>', cookies=cookies_no_mcsrf)
        self.custom_locust.set_response("/suite/auth?appian_environment=tempo", 200,
                                        '<html>A huge html blob</html>', cookies=cookies_mcsrf)

        # When
        self.task_set.appian.login(["", ""])

        # Then
        self.assertIn('__appianMultipartCsrfToken', self.task_set.appian.client.cookies.keys())

    def test_upload_document_to_field_bad_doc_id(self) -> None:
        bad_value = 'abc'
        with self.assertRaisesRegex(Exception,
                                    f"Bad document id or list of document ids: {bad_value}"):
            self.task_set.appian._interactor.upload_document_to_field('fake-url', {}, {}, 'uuid', 'abc')  # type: ignore

    def test_upload_document_to_field_doc_id(self) -> None:
        doc_id = 1
        upload_field = {'saveInto': 'abc', '_cId': '1123'}

        self.custom_locust.set_response("/doc-url/", 200, '{}')
        self.task_set.appian._interactor.upload_document_to_field('/doc-url/',
                                                                  upload_field, {}, 'uuid', doc_id)

        # This indexing is ridiculous, but we don't care about the rest
        last_request_body = json.loads(self.custom_locust.get_request_list().pop()['data'])
        document_update = last_request_body['updates']['#v'][0]['value']
        self.assertEqual({'#t': 'CollaborationDocument', 'id': 1}, document_update)

    def test_upload_document_to_field_list_of_doc_id(self) -> None:
        doc_ids = [1, 2, 3]
        upload_field = {'saveInto': 'abc', '_cId': '1123'}

        self.custom_locust.set_response("/doc-url/", 200, '{}')
        self.task_set.appian._interactor.upload_document_to_field('/doc-url/',
                                                                  upload_field, {}, 'uuid', doc_ids)

        # This indexing is ridiculous, but we don't care about the rest
        last_request_body = json.loads(self.custom_locust.get_request_list().pop()['data'])
        document_update = last_request_body['updates']['#v'][0]['value']
        self.assertEqual('FileMetadata?list', document_update['#t'])
        for i, doc_id in enumerate(doc_ids):
            self.assertEqual({'clientUuid': '0', 'loadedBytes': 0, 'name': 'no name',
                              'documentId': {'#t': 'CollaborationDocument', 'id': doc_id},
                              'extension': 'none', 'fileSizeBytes': 0},
                             document_update['#v'][i])
