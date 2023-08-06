from .uiform import SailUiForm
from .design_object_uiform import DesignObjectUiForm
from .application_uiform import ApplicationUiForm
from .design_uiform import DesignUiForm
from .design_object_type import DesignObjectType
from .record_uiform import RecordInstanceUiForm
from .record_list_uiform import RecordListUiForm
from .visitor import Visitor
from .appianclient import AppianClient, AppianTaskSet, AppianTaskSequence
from .actions_info import ActionsInfo
from .news_info import NewsInfo
from .reports_info import ReportsInfo
from .records_info import RecordsInfo
from .tasks_info import TasksInfo
from .tempo_navigator import TempoNavigator
from .exceptions import *
from .site_helper import SiteHelper
import locust.stats

locust.stats.CONSOLE_STATS_INTERVAL_SEC = 10
