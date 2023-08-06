from looqbox.flows.reload_database_connection_flow import ReloadDatabaseConnectionFlow
from looqbox.flows.script_response_form_flow import ScriptResponseFormFlow
from looqbox.flows.test_connection_flow import TestConnectionFlow
from looqbox.flows.script_flow import ScriptFlow
from looqbox.flows.base_flow import BaseFlow
import json


class FlowFactory:

    def __init__(self, script_info: str):
        self.script_info = script_info
        self.flow_id = json.loads(script_info).get("flowId", "LOOQ_RESPONSE")

    @property
    def get_flow(self) -> BaseFlow:
        """
        Possible FES flows
            LOOQ_RESPONSE
            LOOQ_RESPONSE_SIMPLE
            LOOQ_RESPONSE_FORM
            LOOQ_TEST_CONN
            LOOQ_TEST
            LOOQ_RELOAD_DATABASE_CONNECTIONS
            LOOQ_DYNAMIC_SCRIPT
        """

        # mapped flows — non mapped flows defaults to ScriptFlow
        flow_classes = {
            "LOOQ_TEST_CONN": TestConnectionFlow,
            "LOOQ_RESPONSE": ScriptFlow,
            "LOOQ_RELOAD_DATABASE_CONNECTIONS": ReloadDatabaseConnectionFlow,
            "LOOQ_RESPONSE_FORM": ScriptResponseFormFlow,
        }

        return flow_classes[self.flow_id](self.script_info)
