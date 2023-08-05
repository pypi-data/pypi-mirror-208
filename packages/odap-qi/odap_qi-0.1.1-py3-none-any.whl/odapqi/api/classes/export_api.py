import json
import uuid
from typing import List
from databricks_cli.jobs.api import JobsApi
from databricks_cli.sdk.api_client import ApiClient
from odapqi.api.functions import check_active


class ExportApi:
    def __init__(
        self,
        *,
        destinations_table: str,
        data_path: str,
        databricks_host: str,
        databrics_token: str,
        cluster_id: str,
        notebook_path: str,
        lib_version: str,
    ):
        self.active = False
        if (
            destinations_table
            and data_path
            and databricks_host
            and databrics_token
            and cluster_id
            and notebook_path
            and lib_version
        ):
            self.active = True
        self.destinations_table = destinations_table
        self.data_path = data_path
        self.databricks_host = databricks_host
        self.databrics_token = databrics_token
        self.cluster_id = cluster_id
        self.notebook_path = notebook_path
        self.lib_version = lib_version

    @check_active
    def get_destinations(self):
        return self.spark.sql(
            f"SELECT id, name, type FROM {self.destinations_table}"
        ).collect()

    @check_active
    def get_destination_by_id(self, id: str):
        return self.spark.sql(
            f"SELECT id, name, credentials, mapping, type FROM {self.destinations_table} WHERE id = '{id}'"
        ).first()

    @check_active
    def build_export_config(
        self, name: str, segment_id: str, destination_id: str, attributes: List[str]
    ):
        segment = self.get_segment_by_id(segment_id)
        destination = self.get_destination_by_id(destination_id)

        return {
            "action": "export",
            "destination_type": destination.type,
            "data_paths": self.data_path,
            "params": {"export_columns": attributes, "mapping": destination.mapping},
            "segments": [
                {
                    "segment_name": segment.name,
                    "segment_id": segment.id,
                    "definition_segment": segment.conditions,
                    "definition_base": [],
                }
            ],
            "credentials": destination.credentials,
            "export_title": name,
            "export_id": str(uuid.uuid4()),
        }

    @check_active
    def create_export_job(self, config, run_now):
        api_client = ApiClient(host=self.databricks_host, token=self.databrics_token)

        jobs_api = JobsApi(api_client)

        job_config = {
            "name": "segment-export",
            "existing_cluster_id": self.cluster_id,
            "notebook_task": {
                "notebook_path": self.notebook_path,
                "base_parameters": {
                    "config": json.dumps(config),
                    "library_version": self.lib_version,
                },
            },
        }
        create_job_result = jobs_api.create_job(job_config)
        job_id = create_job_result["job_id"]

        if run_now:
            jobs_api.run_now(
                job_id=job_id,
                jar_params=[],
                notebook_params={},
                python_params=[],
                spark_submit_params=[],
            )

        return job_id
