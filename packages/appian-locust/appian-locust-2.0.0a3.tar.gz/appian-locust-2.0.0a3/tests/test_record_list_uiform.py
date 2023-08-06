import json
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from appian_locust import AppianTaskSet, logger
from appian_locust.record_list_uiform import RecordListUiForm
from locust import Locust, TaskSet

from requests.exceptions import HTTPError
from tests.mock_client import CustomLocust
from tests.mock_reader import read_mock_file
from appian_locust._records import RECORDS_INTERFACE_PATH, RECORDS_NAV_PATH

log = logger.getLogger(__name__)


class TestRecordListUiForm(unittest.TestCase):

    def setUp(self) -> None:
        self.custom_locust = CustomLocust(Locust())
        parent_task_set = TaskSet(self.custom_locust)
        setattr(parent_task_set, "host", "")
        setattr(parent_task_set, "auth", ["", ""])
        self.task_set = AppianTaskSet(parent_task_set)
        self.task_set.host = ""

        # test_on_start_auth_success is covered here.
        self.custom_locust.set_response("auth?appian_environment=tempo", 200, '{}')
        if not hasattr(self.task_set, 'appian'):
            self.task_set.on_start()

    def tearDown(self) -> None:
        self.task_set.on_stop()

    @patch('appian_locust._interactor._Interactor.get_page')
    def test_filter_records_using_searchbox(self, mock_get_page: MagicMock) -> None:
        uri = '/suite/rest/a/sites/latest/D6JMim/pages/records/recordType/commit'
        record_type_list_form = RecordListUiForm(self.task_set.appian._interactor, json.loads(read_mock_file("records_response.json")))
        record_type_list_form.filter_records_using_searchbox("Actions Page")

        mock_get_page.assert_called_once()
        _, kwargs = mock_get_page.call_args_list[0]
        self.assertEqual(kwargs['uri'], f"{uri}?searchTerm=Actions%20Page")
        self.assertEqual(kwargs['headers']['Accept'], "application/vnd.appian.tv.ui+json")
