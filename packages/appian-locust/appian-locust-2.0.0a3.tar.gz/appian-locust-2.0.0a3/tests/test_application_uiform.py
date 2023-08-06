import unittest
import json

from locust import TaskSet, Locust
from .mock_client import CustomLocust
from .mock_reader import read_mock_file
from appian_locust import AppianTaskSet, DesignObjectUiForm


class TestApplicationUiform(unittest.TestCase):

    def setUp(self) -> None:
        self.custom_locust = CustomLocust(Locust())
        parent_task_set = TaskSet(self.custom_locust)
        setattr(parent_task_set, "host", "")
        setattr(parent_task_set, "auth", ["", ""])
        self.task_set = AppianTaskSet(parent_task_set)
        self.task_set.host = ""

        # test_on_start_auth_success is covered here.
        self.custom_locust.set_response("auth?appian_environment=tempo", 200, '{}')
        self.task_set.on_start()

    def tearDown(self) -> None:
        self.task_set.on_stop()

    def test_click_application(self) -> None:
        app_landing_page = read_mock_file("design_app_landing_page.json")
        self.custom_locust.set_response("/suite/rest/a/applications/latest/app/design/app/yh4Z0_7aQfhi2FgIUOqaca_4Vlp", 200, app_landing_page)
        application = self.task_set.appian.visitor.visit_application_by_id("yh4Z0_7aQfhi2FgIUOqaca_4Vlp")
        result_state = '{"ase": "ase"}'
        self.custom_locust.set_response(
            "/suite/rest/a/applications/latest/app/design/lIBKSzmcS2f-JBIoXdpEpcXkuLVVXxoykWGSNEqB-oPAfjLayGXYe7CkjVo53babGjVtBl2x-96-oRsUrFC3i3bZm3cF0kG7wwaG-9H6213zpNl", 200, result_state)
        application = application.click_design_object("RE_stockData")
        self.assertEqual(type(application), DesignObjectUiForm)
        self.assertEqual(application.get_latest_state(), json.loads(result_state))
