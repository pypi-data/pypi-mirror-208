from pyspark.sql import SparkSession

from odapqi.api.classes.export_api import ExportApi
from odapqi.api.classes.segment_api import SegmentApi
from odapqi.api.classes.qi_api_preprocessing import QiApiSample, QiApiPreprocess
from odapqi.api.classes.qi_api import QiApi
from odapqi.api.qi_helpers import print_binning_overview, figures_binning_overview

class PersonaAPI(SegmentApi, ExportApi, QiApiSample, QiApiPreprocess, QiApi):
    def __init__(
        self,
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
        self.spark = SparkSession.builder.getOrCreate()
        self.print_binning_overview = print_binning_overview
        self.figures_binning_overview = figures_binning_overview
        SegmentApi.__init__(
            self,
            features_table=features_table_full,
            segments_table=segments_table,
        )
        ExportApi.__init__(
            self,
            destinations_table=destinations_table,
            data_path=data_path,
            databricks_host=databricks_host,
            databrics_token=databrics_token,
            cluster_id=cluster_id,
            notebook_path=notebook_path,
            lib_version=lib_version,
        )
        QiApiSample.__init__(
            self,
            features_table_full=features_table_full,
            features_table_sampled=features_table_sampled,
        )
        QiApiPreprocess.__init__(
            self,
            features_table_sampled=features_table_sampled,
        )
        QiApi.__init__(
            self,
            features_table_processed=features_table_processed,
            features_info_table=stats_table,
        )
