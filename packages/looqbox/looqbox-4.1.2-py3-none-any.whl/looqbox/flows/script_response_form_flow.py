import importlib.util
from looqbox.flows.base_flow import BaseFlow

from looqbox.integration.integration_links import _response_json_form


class ScriptResponseFormFlow(BaseFlow):
    script_module = None

    def import_script(self) -> None:
        spec = importlib.util.spec_from_file_location("executed_script", self.script_file)
        self.script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.script_module)

    def execute_looq_response(self) -> None:
        if not self.upload_file:
            raise Exception("Upload file not found")
        self.data = _response_json_form(self.upload_file, self.data, self.script_module.looq_response)

    def run(self) -> None:
        steps = [
            self.read_response_parameters,
            self.response_enricher,
            self.define_global_variables,
            self.import_script,
            self.execute_looq_response,
            self._remove_query_from_global_list,
            self.response_writer
        ]
        self.run_steps(steps)
