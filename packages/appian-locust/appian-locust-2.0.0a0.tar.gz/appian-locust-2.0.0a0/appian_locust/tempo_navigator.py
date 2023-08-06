from ._interactor import _Interactor
from .news_info import NewsInfo
from .actions_info import ActionsInfo
from .records_info import RecordsInfo
from .reports_info import ReportsInfo
from .tasks_info import TasksInfo
from ._actions import _Actions
from ._interactor import _Interactor
from ._locust_error_handler import log_locust_error
from ._records import _Records
from ._reports import _Reports
from ._tasks import _Tasks


class TempoNavigator:
    """
    Used for navigating the primary tabs on tempo to provide metadata on the content available for interaction.
    """

    def __init__(self, interactor: _Interactor):
        self.__interactor = interactor
        self.__actions = _Actions(self.__interactor)
        self.__tasks = _Tasks(self.__interactor)
        self.__reports = _Reports(self.__interactor)
        self.__records = _Records(self.__interactor)

    def navigate_to_news_and_get_info(self) -> NewsInfo:
        """
        Navigate to the News tab in Tempo and gather information about available news entries
        """
        return NewsInfo(self.__interactor)

    def navigate_to_records_and_get_info(self) -> RecordsInfo:
        """
        Navigate to the records tab in Tempo and gather information about available record types
        """
        try:
            self.__records.get_records_interface(locust_request_label="Visit.Records.Tempo")
            self.__records.get_records_nav(locust_request_label="Visit.Records.Tempo")
        except Exception as e:
            log_locust_error(e, error_desc="Response Error", raise_error=False)
        return RecordsInfo(records=self.__records)

    def navigate_to_actions_and_get_info(self) -> ActionsInfo:
        """
        Navigate to the actions tab in Tempo and gather information about available actions
        """
        return ActionsInfo(self.__actions)

    def navigate_to_tasks_and_get_info(self) -> TasksInfo:
        """
        Navigate to the tasks tab in Tempo and gather information about available tasks
        """
        return TasksInfo(self.__tasks)

    def navigate_to_reports_and_get_info(self) -> ReportsInfo:
        """
        Navigate to the reports tab in Tempo and gather information about available reports
        """
        return ReportsInfo(self.__reports)
