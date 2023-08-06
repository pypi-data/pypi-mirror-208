from looqbox.flows.base_flow import BaseFlow
from looqbox.database.database_functions import reload_database_connection


class ReloadDatabaseConnectionFlow(BaseFlow):

    @staticmethod
    def reload_conn():
        reload_database_connection()

    def run(self) -> None:
        steps = [
            self.read_response_parameters,
            self.response_enricher,
            self.define_global_variables,
            self.reload_conn,
            self.response_writer
        ]
        self.run_steps(steps)
