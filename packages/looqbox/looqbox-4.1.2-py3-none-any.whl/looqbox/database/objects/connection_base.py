import datetime
import json
import os
from abc import ABC, abstractmethod
from platform import system
from multimethod import multimethod
from pandas import DataFrame
from looqbox.class_loader.class_loader import ClassLoader
from looqbox.database.database_exceptions import TimeOutException
from looqbox.global_calling import GlobalCalling
from looqbox.utils.utils import open_file


class BaseConnection(ABC):

    def __init__(self):
        self.test_mode = GlobalCalling.looq.test_mode
        self.connection_alias = ""
        self.query = ""
        self.retrieved_data = DataFrame()
        self.query_metadata = dict()

        self.is_optimized_for_large_dataset = False

    def set_optimization_for_large_datasets(self, is_optimized: bool) -> None:
        self.is_optimized_for_large_dataset = is_optimized

    def _get_timeout_methods(self):

        timeout_configuration_file = open_file(os.path.dirname(__file__), "..", "..", "configuration", "timeout_settings_class_path.json")

        timeout_factory = json.load(timeout_configuration_file)

        class_path, class_name = timeout_factory[system().lower()].rsplit(".", 1)
        timer = ClassLoader(class_name, class_path).load_class()

        return timer

    @abstractmethod
    def set_query_script(self, sql_script):
        pass

    @abstractmethod
    def connect(self):
        pass

    def _get_response_timeout(self) -> int:
        timeout = int(GlobalCalling.looq.response_timeout) if not self.test_mode else 0
        return timeout

    def _update_response_timeout(self, consumed_time: datetime.timedelta) -> None:
        GlobalCalling.looq.response_timeout -= int(round(consumed_time.total_seconds(), 0))

    @multimethod
    def execute(self, cache_time: None) -> None:
        timer = self._get_timeout_methods()

        response_timeout = self._get_response_timeout()
        #timer.set_timeout(response_timeout)

        start_time = datetime.datetime.now()

        try:
            self._call_query_executor(start_time)
        except TimeOutException as ex:
            total_sql_time = datetime.datetime.now() - start_time
            GlobalCalling.log_query({"connection": self.connection_alias, "query": self.query,
                                     "time": str(total_sql_time), "success": False})
            raise ex
        finally:
            self.close_connection()
            timer.reset_timeout()

    @multimethod
    def execute(self, cache_time: int) -> None:
        timer = self._get_timeout_methods()

        response_timeout = self._get_response_timeout()
        timer.set_timeout(response_timeout)
        start_time = datetime.datetime.now()
        try:
            self.use_query_cache(cache_time, start_time)
        except TimeOutException as ex:
            total_sql_time = datetime.datetime.now() - start_time
            GlobalCalling.log_query({"connection": self.connection_alias, "query": self.query,
                                     "time": str(total_sql_time), "success": False})
            raise ex
        except Exception as folder_exception:
            raise folder_exception
        finally:
            self.close_connection()
            timer.reset_timeout()

    @abstractmethod
    def _call_query_executor(self, query_timer, query_mode="single"):
        """
        Method that call _get_query_result implementing the try-except statement using the connection type
        specific error handlers
        """
        pass

    @abstractmethod
    def _get_query_result(self):
        """
        Method to execute the query properly without any try-except statements
        this model allow the execution of several queries in parallel
        """
        pass

    @abstractmethod
    def close_connection(self):
        pass

    @abstractmethod
    def _generate_cache_file_name(self):
        pass

    def use_query_cache(self, cache_time, start_time, query_mode="single"):
        # since cache is saved in rds format, it's necessary
        # to load the equivalent R functions

        # data frame name used in rds file, since R and Python shared the same files,
        # no name has to be attached to the data
        DF_NAME = None
        cache_name = self._generate_cache_file_name()

        if self.test_mode:
            self.check_if_temp_folder_exists()
        cache_file = GlobalCalling.looq.temp_file(cache_name, add_hash=False)

        if self._is_cache_still_valid(cache_file, cache_time):
            self._get_cached_data(DF_NAME, cache_file, start_time, query_mode)
        else:
            self._create_new_cache_file(cache_file, start_time, query_mode)

    def _create_new_cache_file(self, cache_file: str, start_time, query_mode) -> None:
        from pyreadr import write_rds

        self._call_query_executor(start_time, query_mode)

        if self.retrieved_data.empty:
            return None

        if self.test_mode:
            print("creating cache\npath:", cache_file)

        try:
            write_rds(cache_file, self.retrieved_data)
        except Exception as error:
            raise error

    def _get_cached_data(self, DF_NAME: None, cache_file: str, start_time, query_mode="single") -> None:
        from pyreadr import read_r

        if self.test_mode:
            print("using cache\npath:", cache_file)
        try:
            cached_data = read_r(cache_file)[DF_NAME]
            self.retrieved_data = DataFrame(cached_data, columns=cached_data.keys())
            self.query_metadata = {}  # temporally disable metadata for cache
            total_sql_time = datetime.datetime.now() - start_time
            GlobalCalling.log_query({"connection": "Cache File", "query": self.query,
                                     "time": str(total_sql_time), "success": True, "mode": query_mode})

        except FileNotFoundError as file_exception:
            raise file_exception

    def _get_connection_file(self) -> dict:
        import json
        try:
            if isinstance(GlobalCalling.looq.connection_config, dict):
                file_connections = GlobalCalling.looq.connection_config
            else:
                file_connections = open(GlobalCalling.looq.connection_config)
                file_connections = json.load(file_connections)
        except FileNotFoundError:
            raise Exception("File connections.json not found")
        return file_connections

    def _is_cache_still_valid(self, cache_file, cache_time) -> bool:
        import time
        return os.path.isfile(cache_file) and (time.time() - os.stat(cache_file).st_mtime) < cache_time

    def check_if_temp_folder_exists(self) -> None:
        temp_path = GlobalCalling.looq.temp_dir
        if not os.path.isdir(temp_path):
            os.mkdir(temp_path)

    @staticmethod
    def _get_metadata_from_dataframe(dataframe: DataFrame) -> dict:
        # Mapping pandas types to SQL types
        type_mapping = {
            'object': 'VARCHAR',
            'int64': 'INT',
            'int32': 'INT',
            'float64': 'FLOAT',
            'bool': 'BOOL',
            'datetime64[ns]': 'DATETIME'
        }

        # Get types of each column in the DataFrame
        df_types = dataframe.dtypes.apply(lambda x: type_mapping[str(x)])

        # Return as dict with required format
        return {col: {'type': dtype} for col, dtype in df_types.items()}
