from typing import Any, Dict

from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error

ADMIN_URI_PATH: str = "/suite/rest/a/applications/latest/app/admin"


class _Admin:
    def __init__(self, interactor: _Interactor):
        self.interactor = interactor

    @raises_locust_error
    def fetch_admin_json(self) -> Dict[str, Any]:
        """
        Navigates to /admin

        Returns: The response of /admin
        """
        # Navigate to Admin Console
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'ADMIN'
        label = "Admin.MainMenu"
        response = self.interactor.get_page(ADMIN_URI_PATH, headers=headers, label=label)
        response.raise_for_status()
        return response.json()
