import itertools
import sys
import threading
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import pyarrow.parquet as pq
from arize.utils.types import Environments
from pyarrow import flight

from ..utils.validation import Validator
from .endpoint import Endpoint
from .session import Session


class ArizeExportClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        arize_profile: Optional[str] = None,
        arize_config_path: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        self._session = Session(api_key, arize_profile, arize_config_path, host, port)
        self.done = False

    def __call__(self, query: str) -> flight.FlightStreamReader:
        arize_flight_endpoint = Endpoint(self._session)
        flight_client = arize_flight_endpoint.connect()
        reader = arize_flight_endpoint.execute_query(flight_client, query)
        return reader

    def export_model_to_df(
        self,
        space_id: str,
        model_name: str,
        environment: Environments,
        start_time: datetime,
        end_time: datetime,
        include_actual: Optional[bool] = False,
    ) -> pd.DataFrame:
        stream_reader = self.get_model_stream_reader(
            space_id, model_name, environment, start_time, end_time, include_actual
        )
        t = threading.Thread(target=self.animate)
        t.start()
        list_of_df = []
        while True:
            try:
                flight_batch = stream_reader.read_chunk()
                record_batch = flight_batch.data
                data_to_pandas = record_batch.to_pandas()
                list_of_df.append(data_to_pandas)
            except StopIteration:
                self.done = True
                break
        return pd.concat(list_of_df)

    def export_model_to_parquet(
        self,
        path: str,
        space_id: str,
        model_name: str,
        environment: str,
        start_time: datetime,
        end_time: datetime,
        include_actual: Optional[bool] = False,
    ) -> None:
        Validator.validate_input_type(path, "path", str)
        stream_reader = self.get_model_stream_reader(
            space_id, model_name, environment, start_time, end_time, include_actual
        )
        writer = pq.ParquetWriter(path, schema=stream_reader.schema)
        t = threading.Thread(target=self.animate)
        t.start()
        while True:
            try:
                flight_batch = stream_reader.read_chunk()
                record_batch = flight_batch.data
                writer.write_batch(record_batch)
            except StopIteration:
                self.done = True
                break
            finally:
                writer.close()

    def get_model_stream_reader(
        self,
        space_id: str,
        model_name: str,
        environment: str,
        start_time: datetime,
        end_time: datetime,
        include_actual: Optional[bool] = False,
    ) -> flight.FlightStreamReader:
        Validator.validate_input_type(space_id, "space_id", str)
        Validator.validate_input_type(model_name, "model_name", str)
        Validator.validate_input_type(environment, "environment", Environments)
        Validator.validate_input_type(include_actual, "include_actual", bool)
        Validator.validate_input_type(start_time, "start_time", datetime)
        Validator.validate_input_type(end_time, "end_time", datetime)

        if environment == Environments.PRODUCTION and include_actual:
            data_type = "CONCLUSIONS"
        elif environment == Environments.PRODUCTION and not include_actual:
            data_type = "PREDICTIONS"
        elif environment == Environments.TRAINING or environment == Environments.VALIDATION:
            data_type = "PREPRODUCTION"

        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        cmd = (
            f'{{"spaceId":"{space_id}","externalModelId":"{model_name}", "dataType":"{data_type.upper()}", '
            f'"startTime":"{start_time_str}", "endTime":"{end_time_str}"}}'
        )
        stream_reader = self(query=cmd)
        return stream_reader

    def animate(self) -> None:
        self.done = False
        for c in itertools.cycle(["," "/", "-", "\\"]):
            if self.done:
                break
            sys.stdout.write("\rexporting in progress " + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\rexport complete!     ")
