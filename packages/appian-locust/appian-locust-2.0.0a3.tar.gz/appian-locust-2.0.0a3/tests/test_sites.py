from locust import TaskSet, Locust
from .mock_client import CustomLocust
from .mock_reader import read_mock_file
from requests import Response
from appian_locust import AppianTaskSet
from appian_locust._interactor import _Interactor
from appian_locust._sites import _Sites, SiteNotFoundException, PageNotFoundException, PageType
from appian_locust.uiform import SailUiForm
import json
import os
import unittest


class TestSites(unittest.TestCase):

    def setUp(self) -> None:
        self.custom_locust = CustomLocust(Locust())
        setattr(self.custom_locust.client, "feature_flag", "")
        setattr(self.custom_locust.client, "feature_flag_extended", "")
        parent_task_set = TaskSet(self.custom_locust)

        setattr(parent_task_set, "host", "")
        setattr(parent_task_set, "auth", ["", ""])
        self.task_set = AppianTaskSet(parent_task_set)
        self.task_set.host = ""

        # test_on_start_auth_success is covered here.
        self.custom_locust.set_response("auth?appian_environment=tempo", 200, '{}')
        self.interactor = _Interactor(self.custom_locust.client, "")
        self.interactor.login(["", ""])
        self.sites_interactor = _Sites(self.interactor)
        self.task_set.on_start()

        all_sites_str = read_mock_file("all_sites.json")
        self.custom_locust.set_response("/suite/rest/a/sites/latest/D6JMim/page/news/nav", 200, all_sites_str)

        # Default responses are page responses
        page_resp_json = read_mock_file("page_resp.json")
        self.custom_locust.client.set_default_response(200, page_resp_json)

    def tearDown(self) -> None:
        self.task_set.on_stop()

    def test_sites_get_all(self) -> None:
        page_resp_json = read_mock_file("page_resp.json")
        site_nav_resp = read_mock_file("sites_nav_resp.json")
        all_sites_str = read_mock_file("all_sites.json")
        self.custom_locust.client.enqueue_response(200, all_sites_str)
        for i in range(136):
            self.custom_locust.client.enqueue_response(200, site_nav_resp)
            for i in range(5):
                self.custom_locust.client.enqueue_response(200, page_resp_json)

        self.sites_interactor.get_all()
        all_sites = self.sites_interactor._sites
        self.assertEqual(len(all_sites.keys()), 136)
        self.assertTrue("rla" in all_sites, "rla not found in list of sites")

        # Spot check
        rla_site = all_sites["rla"]
        self.assertEqual(len(rla_site.pages.keys()), 5)
        self.assertEqual(rla_site.pages['create-mrn'].page_type, PageType.REPORT)

    def set_sites_json(self, site_name: str) -> None:
        sites_nav_resp = read_mock_file("sites_nav_resp.json")
        self.custom_locust.set_response(f"/suite/rest/a/sites/latest/{site_name}/nav", 200, sites_nav_resp)

    def test_sites_get(self) -> None:
        site_name = 'mrn'
        self.set_sites_json(site_name)
        site = self.sites_interactor.get_site_data_by_site_name('mrn')

    def test_sites_link_type(self) -> None:
        for type_pair in [('InternalActionLink', 'action'),
                          ('InternalReportLink', 'report'),
                          ('SiteRecordTypeLink', 'recordType'),
                          ('SiteInterfaceLink', 'interface')]:
            original_link_type = type_pair[0]
            expected_link_type = type_pair[1]
            link_full = f"{{http://www.host.net/ae/types/2009}}{original_link_type}"
            link_type = self.sites_interactor._get_type_from_link_type(link_full)
            self.assertEqual(link_type.value, expected_link_type)

    def test_sites_bad_link_type(self) -> None:
        with self.assertRaises(Exception) as e:
            bad_link_type = "this is garbage"
            self.sites_interactor._get_type_from_link_type(bad_link_type)
        self.assertEqual(e.exception.args[0], f"Invalid Link Type: {bad_link_type}")

    def test_navigate_to_tab_error_cases(self) -> None:
        site_name = "abc"
        self.set_sites_json(site_name)
        with self.assertRaises(SiteNotFoundException):
            self.sites_interactor.fetch_site_tab_json("other_site", "123")
        with self.assertRaises(PageNotFoundException):
            self.sites_interactor.fetch_site_tab_json(site_name, "123")

    def test_navigate_to_tab_success(self) -> None:
        site_name = "abc"
        page_name = "create-mrn"
        link_type = "report"  # Default Page Info

        self.set_sites_json(site_name)

        self.custom_locust.set_response(f"/suite/rest/a/sites/latest/{site_name}/pages/{page_name}/{link_type}",
                                        200,
                                        '{"test":"abc"}')
        tab_resp = self.sites_interactor.fetch_site_tab_json(site_name, page_name)
        self.assertEqual({'test': 'abc'}, tab_resp)

    def test_get_sites_records(self) -> None:
        site_name = "orders"
        page_name = "orders"
        link_type = "recordType"

        nav_resp = read_mock_file("sites_record_nav.json")
        page_resp = read_mock_file("sites_record_page_resp.json")
        record_resp = read_mock_file("sites_record_recordType_resp.json")

        for endpoint in [f"/suite/rest/a/sites/latest/{site_name}/nav",
                         f"/suite/rest/a/sites/latest/{site_name}/pages/{page_name}/nav"]:
            self.custom_locust.set_response(endpoint, 200, nav_resp)

        nav_ui = json.loads(nav_resp)
        for mocked_page_name in self.sites_interactor.get_page_names_from_ui(nav_ui):
            self.custom_locust.set_response(f"/suite/rest/a/applications/latest/legacy/sites/{site_name}/page/{mocked_page_name}",
                                            200,
                                            page_resp)
        self.custom_locust.set_response(f"/suite/rest/a/sites/latest/{site_name}/pages/{page_name}/{link_type}",
                                        200,
                                        record_resp)

        self.custom_locust.set_default_response(200, record_resp)

        resp = self.sites_interactor.fetch_site_tab_record_json(site_name, page_name)

        self.assertEqual(resp, json.loads(record_resp))


if __name__ == '__main__':
    unittest.main()
