from requests.models import Response

from ._actions import _Actions
from ._interactor import _Interactor


class SiteHelper:
    def __init__(self, interactor: _Interactor):
        self.__interactor = interactor
        self.__actions = _Actions(self.__interactor)

    def start_action(self, action_name: str, skip_design_call: bool = False,
                     exact_match: bool = False) -> Response:
        """
        Perform the post operation on action's API to start specific action.
        Actions that do not have a UI can be called directly without using "GET" to retrieve the UI.
        this is controlled by the optional skip_design_call parameter

        Args:
            action_name(str): Name of the action
            skip_design_call(bool, optional): to skip the "GET" call for the action's UI. Default : False
            exact_match (bool, optional): Should action name match exactly or to be partial match. Default : False

        Returns: requests.models.Response

        Example:

            >>> self.appian.site_helper.start_action("action_name")

        """
        return self.__actions.start_action(action_name, skip_design_call, exact_match)
