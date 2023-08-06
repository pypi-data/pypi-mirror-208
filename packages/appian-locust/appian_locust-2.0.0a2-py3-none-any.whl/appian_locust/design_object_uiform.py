from typing import Any, Dict

from ._design import _Design
from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error
from .uiform import SailUiForm


class DesignObjectUiForm(SailUiForm):

    def __init__(self, interactor: _Interactor, state: Dict[str, Any], breadcrumb: str = "DesignObjectUi"):
        super().__init__(interactor, state, breadcrumb)
        self.__design = _Design(interactor)

    @raises_locust_error
    def launch_query_editor(self) -> 'DesignObjectUiForm':
        """
        Calls the post operation to click on the LaunchVQD button in the toolbar for the ExpressionEditorWidget.
        This will launch the query editor with the expression currently in the expression editor.

        Returns (DesignObjectUiForm): UiForm updated with state representing launched query editor

        """
        query_editor_json = self.__design.click_expression_editor_toolbar_button("LaunchVQD", self.form_url, self._state, self.context, self.uuid)
        self._reconcile_state(query_editor_json)
        return self
