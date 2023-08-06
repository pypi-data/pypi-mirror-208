from typing import Any, Dict

from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error

PAGE_URL_PREFIX = "/_/ui/page/"


class _Portals:

    def __init__(self, interactor: _Interactor):
        self.interactor = interactor

    @raises_locust_error
    def fetch_page_json(self, portal_unique_identifier: str, portal_page__unique_identifier: str) -> Dict[str, Any]:
        """
        Navigates to specific portal's page

        Returns: The response of portal's page
        """
        label = "Portals.Page"
        portal_uri_path = self.get_full_url(portal_unique_identifier, portal_page__unique_identifier)
        response = self.interactor.get_page(portal_uri_path, label=label, check_login=False)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_full_url(portal_unique_identifier: str, portal_page__unique_identifier: str) -> str:
        return "/" + portal_unique_identifier + PAGE_URL_PREFIX + portal_page__unique_identifier
