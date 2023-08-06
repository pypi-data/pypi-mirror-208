from typing import Any, Dict

from ._design import _Design
from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error
from .design_object_uiform import DesignObjectUiForm
from .uiform import SailUiForm


class ApplicationUiForm(SailUiForm):

    def __init__(self, interactor: _Interactor, state: Dict[str, Any], breadcrumb: str = "ApplicationUi"):
        super().__init__(interactor, state, breadcrumb)
        self.__design = _Design(interactor)

    @raises_locust_error
    def click_design_object(self, design_object_name: str) -> DesignObjectUiForm:
        """
        Click on a design object in the design object grid. The current view of the grid must contain the object you wish
        to click.
        Args:
            design_object_name: The name of the design object to click on

        Returns (DesignObjectUiForm): UiForm representing UI of design object

        """
        opaque_id = self.__design.find_design_object_opaque_id_in_grid(design_object_name, self._state)
        breadcrumb = "Design.SelectedObject." + opaque_id[0:10] + ".SailUi"
        return DesignObjectUiForm(self._interactor, self.__design.fetch_design_object_json(opaque_id), breadcrumb)

    @raises_locust_error
    def create_record_type(self, record_type_name: str) -> 'ApplicationUiForm':
        """
        Takes an application form and creates a record type with the given name

        Returns: The SAIL UI Form after the record type is created

        """
        self.__design._create_object(self, link_name='Record Type', object_name=record_type_name)
        return self

    @raises_locust_error
    def create_report(self, report_name: str) -> 'ApplicationUiForm':
        """
        Takes an application form and creates a report with the given name

        Returns: The SAIL UI Form after the report is created

        """
        self.__design._create_object(self, link_name='Report', object_name=report_name)
        return self
