from looqbox.flows.base_flow import BaseFlow
from looqbox.utils.utils import _test_connection


class TestConnectionFlow(BaseFlow):
    def test_connection(self) -> None:
        conn_name = self.input_json_file.get("connectionName")
        _test_connection(conn_name)

    def run(self):
        steps = [
            self.read_response_parameters,
            self.response_enricher,
            self.define_global_variables,
            self.test_connection
        ]
        self.run_steps(steps)
