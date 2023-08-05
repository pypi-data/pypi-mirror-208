from IPython.display import display
from odapqi.api import PersonaAPI, QiFeaturesSelection
from odapqi.display import WidgetTab
from pyspark.dbutils import DBUtils
import databricks_cli


def resolve_dbutils() -> DBUtils:
    import IPython

    ipython = IPython.get_ipython()

    if not hasattr(ipython, "user_ns") or "dbutils" not in ipython.user_ns:
        raise Exception("dbutils cannot be resolved")

    return ipython.user_ns["dbutils"]


def show(
    *,
    features_table_full: str = "",
    features_table_sampled: str = "",
    features_table_processed: str = "",
    segments_table: str = "",
    destinations_table: str = "",
    data_path: str = "",
    databricks_host: str = "",
    databrics_token: str = "",
    cluster_id: str = "",
    notebook_path: str = "",
    lib_version: str = "",
    stats_table: str="",
):
    api = PersonaAPI(
        features_table_full=features_table_full,
        features_table_sampled=features_table_sampled,
        features_table_processed=features_table_processed,
        segments_table=segments_table,
        destinations_table=destinations_table,
        data_path=data_path,
        databricks_host=databricks_host,
        databrics_token=databrics_token,
        cluster_id=cluster_id,
        notebook_path=notebook_path,
        lib_version=lib_version,
        stats_table=stats_table,
    )

    return api

