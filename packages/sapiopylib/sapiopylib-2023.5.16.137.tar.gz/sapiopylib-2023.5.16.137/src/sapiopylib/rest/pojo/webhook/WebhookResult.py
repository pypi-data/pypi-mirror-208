from typing import Any, List, Dict, Optional

from sapiopylib.rest.pojo.reportbuilder.VeloxReportBuilder import RbTemplatePopulatorData
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import AbstractClientCallbackRequest
from sapiopylib.rest.pojo.webhook.WebhookDirective import AbstractWebhookDirective


class SapioWebhookResult:
    """
    Returned webhook result from webhook handler to sapio platform.

    passed: Whether the handler had successfully handled request. "False" value may cause transaction to be rolled back.

    display_text: If this is selection list populator handler, the possible values for user to select in selection list.

    directive: Any place we will navigate player to after receiving this request.

    client_callback_request: A popup request asking client for more information in UI.

    refresh_data: Whether forces the client to refresh existing data in the page.
    """
    passed: bool
    display_text: Optional[str]
    list_values: Optional[List[str]]
    directive: Optional[AbstractWebhookDirective]
    client_callback_request: Optional[AbstractClientCallbackRequest]
    refresh_data: bool
    report_builder_template_populator_data: Optional[RbTemplatePopulatorData]

    def __init__(self, passed: bool, display_text: Optional[str] = None,
                 list_values: Optional[List[str]] = None,
                 directive: Optional[AbstractWebhookDirective] = None,
                 client_callback_request: Optional[AbstractClientCallbackRequest] = None,
                 refresh_data: bool = False,
                 report_builder_template_populator_data: Optional[RbTemplatePopulatorData] = None):
        """
        Returned webhook result from webhook handler to sapio platform.

        :param passed: Whether the handler had successfully handled request.
        "False" value may cause transaction to be rolled back.

        :param display_text: If this is selection list populator handler, the possible values for user to select in
        selection list.

        :param directive: Any place we will navigate player to after receiving this request.

        :param client_callback_request: A popup request asking client for more information in UI.

        :param refresh_data: Whether forces the client to refresh existing data in the page.
        """
        self.passed = passed
        self.display_text = display_text
        self.list_values = list_values
        self.directive = directive
        self.client_callback_request = client_callback_request
        self.refresh_data = refresh_data
        self.report_builder_template_populator_data = report_builder_template_populator_data

    def to_json(self) -> Dict[str, Any]:
        directive_pojo = None
        if self.directive is not None:
            directive_pojo = self.directive.to_json()
        client_callback_pojo = None
        if self.client_callback_request is not None:
            client_callback_pojo = self.client_callback_request.to_json()
        report_builder_populator_pojo = None
        if self.report_builder_template_populator_data is not None:
            report_builder_populator_pojo = self.report_builder_template_populator_data.to_json()
        return {
            'passed': self.passed,
            'displayText': self.display_text,
            'listValues': self.list_values,
            'directive': directive_pojo,
            'clientCallbackRequest': client_callback_pojo,
            'refreshData': self.refresh_data,
            'rbTemplatePopulatorDataPojo': report_builder_populator_pojo
        }
