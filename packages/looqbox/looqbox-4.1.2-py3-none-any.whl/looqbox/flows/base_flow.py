import json
import uuid
import os.path

from abc import abstractmethod
from typing import Any, Callable, Dict, List

from looqbox.global_calling import GlobalCalling
from looqbox.utils.utils import _format_quotes, load_json_from_relative_path


class BaseFlow:
    def __init__(self, script_info: str):
        script_data = json.loads(script_info)
        self.input_json_file = script_data.get("responseParameters", {})
        self.script_file = script_data.get("vars", {}).get("response_path", "")
        self.output_json_file = script_data.get("resultPath", "")
        self.upload_file = script_data.get("UploadFile", "")
        self.vars = script_data.get("vars", {})
        self.data: Dict[str, Any] | str = {}
        self.global_variables = GlobalCalling().looq
        GlobalCalling().looq.session_id = uuid.uuid4()
        GlobalCalling().looq.query_list[GlobalCalling().looq.session_id] = []

    def read_response_parameters(self) -> None:
        raw_file = open(self.input_json_file, 'r', encoding='utf-8').read()
        self.data = _format_quotes(raw_file)
        self.data = json.loads(self.data)

    def response_enricher(self) -> None:
        self.data.update(self.vars)

    def define_global_variables(self) -> None:
        for key, value in self.vars.items():
            setattr(self.global_variables, key, value)

    def response_writer(self) -> None:
        with open(self.output_json_file, 'w') as file:
            file.write(self.data)
            file.close()

    def _set_stack_trace_level(self) -> None:

        import sys
        flow_settings_path = os.path.join(os.path.dirname(__file__), "..", "..",
                                          "configuration", "flow_settings.json")

        if self.global_variables.test_mode:
            flow_setting = load_json_from_relative_path(flow_settings_path)
            sys.tracebacklimit = flow_setting.stackTraceLevel
        else:
            sys.tracebacklimit = None

    @staticmethod
    def _remove_query_from_global_list() -> None:
        try:
            del GlobalCalling.looq.query_list[GlobalCalling.looq.session_id]
        except KeyError as error:
            print(KeyError("Could not find session id in queries list"))

    @staticmethod
    def run_steps(steps: List[Callable]) -> None:
        [step() for step in steps]

    @abstractmethod
    def run(self) -> None:
        ...
