from enum import Enum
from typing import Any, Dict, Optional

from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error
from ._save_request_builder import save_builder
from .helper import find_component_by_type_and_attribute_and_index_in_dict, find_component_by_type_and_attribute_and_index_in_dict, find_component_by_attribute_in_dict
from .uiform import SailUiForm

DESIGN_URI_PATH: str = "/suite/rest/a/applications/latest/app/design"


class _Design:
    def __init__(self, interactor: _Interactor):
        self.interactor = interactor

    @raises_locust_error
    def fetch_design_json(self) -> Dict[str, Any]:
        """
        Fetches the JSON of /design UI

        Returns: JSON Dictionary

        Example:

            >>> design.fetch_design_json()

        """
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'DESIGN'
        label = "Design.ApplicationList"
        response = self.interactor.get_page(DESIGN_URI_PATH, headers=headers, label=label)
        response.raise_for_status()
        return response.json()

    @raises_locust_error
    def fetch_application_json(self, app_id: str) -> Dict[str, Any]:
        """
        Fetches the JSON of the UI for a specific application within the /design environment

        Returns: JSON Dictionary

        Example:

            >>> design.fetch_application_json("AADZeglVgAAgfpsAAJsAAAAAAdA")

        """
        application_uri = f"{DESIGN_URI_PATH}/app/{app_id}"
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'DESIGN'
        label = f"Design.SelectedApplication.{app_id}"
        response = self.interactor.get_page(application_uri, headers=headers, label=label)
        response.raise_for_status()
        return response.json()

    @raises_locust_error
    def fetch_design_object_json(self, opaque_id: str) -> Dict[str, Any]:
        """
        Fetches the JSON of the UI for a specific object within the /design environment

        Returns: JSON Dictionary

        Example:

             >>> design.fetch_design_object_json("lABD1iTIu_lxy_3T_90Is2fs63uh52xESYi6-fun7FBWshlrBQ0EptlFUdGyIRzSSluPyVdvOhvGgL6aBlnjlkWfQlALYR2aRZ_AIliJ4lc3g")

        """
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'DESIGN'
        uri = DESIGN_URI_PATH + '/' + opaque_id
        label = "Design.SelectedObject." + opaque_id[0:10]
        response = self.interactor.get_page(uri, headers=headers, label=label)
        response.raise_for_status()
        return response.json()

    @raises_locust_error
    def find_design_grid(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return find_component_by_type_and_attribute_and_index_in_dict(state, "GridField", "testLabel", "GRID-LABEL")

    def click_expression_editor_toolbar_button(self, button_action: str, post_url: str, state: Dict[str, Any], context: Dict[str, Any], uuid: str,
                                               label: Optional[str] = None) -> Dict[str, Any]:

        expression_editor_component = find_component_by_type_and_attribute_and_index_in_dict(state, type="ExpressionInfoPanel")["editorWidget"]
        expression = expression_editor_component["value"]

        new_value = {
            "#t": "Dictionary",
            "#v": {
                "actionType": button_action,
                "hasMatchingBracketError": False,
                "launchOrigin": "toolbarButton",
                "queryFnType": "queryRecordType",
                "queryFnStartIndex": 0,
                "queryFnEndIndex": len(expression),
                "value": {
                    "#t": "Text",
                    "#v": expression
                }
            }
        }

        locust_label = label or f'Click \'{button_action}\' Expression Editor Widget Button'
        return self.interactor.click_generic_element(post_url, expression_editor_component, context, uuid, new_value, locust_label)

    def search_design_grid(self, search_str: str, reeval_url: str,
                           state: Dict[str, Any], context: Dict[str, Any], uuid: str, locust_label: str = "Design.Search") -> Dict[str, Any]:
        """
        Search a grid in /design
        Args:
            search_str (str): string to search
            reeval_url (str): url to send request to
            state (str): current state of UI, which contains the search bar
            context (str): current context
            uuid (str): UUID of search component
            locust_label (str): label to associate request with

        Returns:

        """
        search_component = find_component_by_attribute_in_dict(attribute="#t", value="SearchBoxWidget",
                                                               component_tree=state)
        search_component["#t"] = "TextWidget"
        return self.interactor.click_generic_element(
            reeval_url, search_component, context, uuid, new_value={"#t": "Text", "#v": search_str},
            label=locust_label)

    def find_design_object_opaque_id_in_grid(self, design_object_name: str, current_state: Dict[str, Any]) -> str:
        grid_component = self.find_design_grid(current_state)
        link_component = find_component_by_attribute_in_dict('testLabel', design_object_name, grid_component, throw_attribute_exception=True)
        return link_component.get("uri").split('/')[-1]

    def _create_object(self, ui_form: SailUiForm, link_name: str, object_name: str) -> 'SailUiForm':
        return ui_form.click(link_name)\
            .fill_text_field('Name', object_name)\
            .click('Create')\
            .assert_no_validations_present()\
            .click('Save')
