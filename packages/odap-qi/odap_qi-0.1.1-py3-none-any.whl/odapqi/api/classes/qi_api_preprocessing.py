from abc import get_cache_token
import time
from itertools import chain
from typing import Tuple
from pyspark.sql import functions as F, DataFrame, SparkSession
from pyspark.ml.feature import Bucketizer
from odapqi.api.functions import check_active
from odapqi.api.qi_helpers import (
    _get_info_per_sample,
    _get_n_of_most_common,
    _round_binning_splits,
    CategoricalBinsReducer,
    IntegralBinsGenerator,
    FloatingPointBinsGenerator,
)


class QiApiSample:
    """Prepare sample for quick insights.

    The reason to sample full feature store might is that it might be too large to run Quick Insights efficiently.
    """

    def __init__(
        self,
        spark: SparkSession,
        features_table_full: str,
        features_table_sampled: str,
        main_filter_condition: str = None,
        method: str = "basic",
        sample_rate: float = 0.1,
        date_column: str = None,
        list_of_dates: list = None,
    ) -> None:
        """

        parameter method determines how sampling should be performed:
        - basic - simple sampling using sample method
        - dates - using sampleBy method for stratified sample, for this method the following arguments needs to be specified:
            - date_column - column name with strartification variable (date, snapshot)
            - list_of_dates - list of dates to be considered

        Args:
            spark (SparkSession): _description_
            feature_store (str, optional): name of feature store table, i.e. input for sampling. Defaults to None.
            feature_store_sampled (str, optional): name of sampled feature store table, i.e. output for sampling. Defaults to None.
            main_filter_condition (str, optional): optional condition to filter relevant part of feature_store priod sampling. Defaults to None.
            method (str, optional): method for sampling: basic vs. dates. Defaults to "basic".
            sample_rate (float, optional): sampling rate. Defaults to 0.1.
            date_column (str, optional): column with date variable (relevant for method='dates'). Defaults to None.
            list_of_dates (list, optional): list of dates to be considered (relevant for method='dates') Defaults to None.
        """
        self.spark = spark
        self.features_table_full = features_table_full
        self.features_table_sampled = features_table_sampled
        self.main_filter_condition = main_filter_condition
        self.method = method
        self.sample_rate = sample_rate
        self.date_column = date_column
        self.list_of_dates = list_of_dates

    def _load_feature_store_basic_method(self) -> DataFrame:
        """Helper to load full feature store

        Returns:
            DataFrame: loaded feature store table
        """
        if self.main_filter_condition:
            return self.spark.read.table(self.features_table_full).filter(
                self.main_filter_condition
            )
        return self.spark.read.table(self.features_table_full)

    def _load_feature_store_dates_method(self) -> DataFrame:
        """Load feature store using dates method.

        Returns:
            DataFrame: loaded feature store table
        """
        if self.main_filter_condition:
            return (
                self.spark.read.table(self.features_table_full)
                .filter(F.col(self.date_column).isin(self.list_of_dates))
                .filter(self.main_filter_condition)
                .withColumn(
                    f"{self.date_column}_tmp", F.col(self.date_column).cast("string")
                )
            )
        return (
            self.spark.read.table(self.features_table_full)
            .filter(F.col(self.date_column).isin(self.list_of_dates))
            .withColumn(
                f"{self.date_column}_tmp", F.col(self.date_column).cast("string")
            )
        )

    def save_sample(self) -> None:
        """Load full feature store and save sampled version.

        Args:
            sample_rate (float, optional): sampling rate. Defaults to 0.1.
        """
        print("Perfroming sampling")
        start_time = time.time()

        if self.method == "basic":
            df = self._load_feature_store_basic_method()
            df_sampled = df.sample(self.sample_rate, seed=42)
        elif self.method == "dates":
            df = self._load_feature_store_dates_method()
            df_sampled = df.sampleBy(
                col=f"{self.date_column}_tmp",
                fractions={d: self.sample_rate for d in self.list_of_dates},
                seed=42,
            ).drop(f"{self.date_column}_tmp")
        else:
            raise ValueError(
                f"Unsupported method: {self.method}. The supported methods are: basic, dates."
            )

        df_sampled.write.mode("overwrite").saveAsTable(self.features_table_sampled)

        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")


class QiApiPreprocess:
    """Preprocess feature store for Quick Insights.

    Details:
    - pre processing is done to enable quicker calculation of quick insights
    - the following steps are performed
        - summary about features is prepared
        - non-problematic variables are determined
        - non-problematic (or all, see argument analyse_all_features) variables are processed

    For further details see docstring of get_preprocessed_table method.
    Remark: by problematic features we mean features with high missing rate or very low/high share of the most dominant value.

    Example usage:

        qi_preprocess = QiApiPreprocess(
            spark=spark,
            features_store_sampled="hive_metastore.jan_petrik.mancity_fs_sampled_001",
            features_store_processed="hive_metastore.jan_petrik.mancity_fs_sampled_001_processed",
            stats_output_table_name="hive_metastore.jan_petrik.mancity_fs_sampled_001_stats",
            missing_rate_th=0.75,
            max_share_single_value=0.75,
            min_share_single_value=0.05,
            features_list=["Profile_Demographic_Age", "Profile_Demographic_HouseholdIncome", "Profile_Demographic_AgeGroup", "Profile_Demographic_Gender", "Profile_Contact_HashedEmail"],
            process_all_features=False,
        )

        or pre-rpocessing can be done within classes: QiFeaturesSelection and QiFeaturesMonitoring

    """

    def __init__(
        self,
        spark: SparkSession,
        features_store_sampled: str,
        features_store_processed: str,
        stats_output_table_name: str,
        main_filter_condition: str = None,
        missing_rate_th: float = 0.75,
        max_share_single_value: float = 0.75,
        min_share_single_value: float = 0.05,
        features_list: list = None,
        features_to_exclude_list: list = None,
        analyse_all_features: bool = False,
    ) -> None:
        """

        Args:
            features_table_sampled (str): name of features table, i.e. sample to be analysed
        """
        self.spark = spark
        self.features_table_sampled = features_store_sampled
        self.features_table_processed = features_store_processed
        self.stats_output_table_name = stats_output_table_name
        self.main_filter_condition = main_filter_condition

        if isinstance(features_list, str):
            self.vars_list = [features_list]
        else:
            self.vars_list = features_list

        if isinstance(features_to_exclude_list, str):
            self.features_to_exclude_list = [features_to_exclude_list]
        else:
            self.features_to_exclude_list = features_to_exclude_list

        self.missing_rate_th = missing_rate_th
        self.max_share_single_value = max_share_single_value
        self.min_share_single_value = min_share_single_value
        self.reduction_percentage = 0.1
        self.cat_var_max_bins = 15
        self.cat_var_min_bins = 8
        self.cat_var_min_bin_share = 0.01
        self.lower_percentile_percentage = 0.05
        self.higher_percentile_percentage = 0.95
        self.accuracy = 100
        self.bin_count = 8
        self.analyse_all_features = analyse_all_features
        self.active = True

    @check_active
    def _load_raw_sample(self) -> DataFrame:
        if self.main_filter_condition:
            return self.spark.read.table(self.features_table_sampled).filter(
                self.main_filter_condition
            )
        return self.spark.read.table(self.features_table_sampled)

    @check_active
    def _get_variables(self) -> Tuple[list, list, list]:
        """Helper to get categories of features.

        3 different categories of features are considered based on data types:
        - numerical variables - data type needs to be double, float or int (any integer representations)
        - categorical vairables - data type needs to be string
        - binary variables - data type needs to be boolean

        Please note that date and datetime variables are not considered.

        Returns:
            Tuple[list, list, list]: list of numerical, list of categorical, list of binary variables/features
        """
        vars_ = self.spark.sql(
            f"describe table {self.features_table_sampled}"
        ).collect()

        vars_list = self.vars_list
        vars_exclude_list = self.features_to_exclude_list

        # numerical vars
        numerical_vars = [
            var.col_name
            for var in vars_
            if var.data_type
            in ["double", "float", "tinyint", "smallint", "int", "bigint"]
        ]

        # Categorical variables - string or boolean
        categorical_vars = [
            var.col_name for var in vars_ if var.data_type in ["string"]
        ]

        # Categorical variables - string or boolean
        binary_vars = [var.col_name for var in vars_ if var.data_type in ["boolean"]]

        if vars_list:
            numerical_vars = [var for var in numerical_vars if var in vars_list]
            categorical_vars = [var for var in categorical_vars if var in vars_list]
            binary_vars = [var for var in binary_vars if var in vars_list]

        if vars_exclude_list:
            numerical_vars = [
                var for var in numerical_vars if var not in vars_exclude_list
            ]
            categorical_vars = [
                var for var in categorical_vars if var not in vars_exclude_list
            ]
            binary_vars = [var for var in binary_vars if var in vars_exclude_list]

        if not numerical_vars and not categorical_vars and not binary_vars:
            raise ValueError(
                "No features selected. Please check parameters: features_list and features_to_exclude_list"
            )

        return numerical_vars, categorical_vars, binary_vars

    @check_active
    def _get_variables_info(self, df: DataFrame) -> DataFrame:
        """Get summary information about individual predictors/features on whole sample.

        The following characteristics are calculated:
        - min, max and average value (only for numerical features)
        - missing rate
        - share of most common value
        - share of most common value (with missing values excluded)

        Args:
            df (DataFrame): sample to be analysed

        Returns:
            DataFrame: df with summary information about individual predictors/features
        """

        (numerical_vars, categorical_vars, binary_vars) = self._get_variables()

        all_vars = numerical_vars + categorical_vars + binary_vars

        # statistics per different samples and share of most common value
        stats_all = _get_info_per_sample(
            df,
            numerical_vars,
            categorical_vars,
            binary_vars,
            spark=self.spark,
            suffix="all",
        )

        most_common_all = _get_n_of_most_common(
            df=df, vars_list=all_vars, spark=self.spark, suffix="all"
        )

        # combine together
        combined = (
            stats_all.join(most_common_all, on="id", how="left")
            .withColumn(
                "var_type",
                F.when(F.col("id").isin(numerical_vars), F.lit("numerical"))
                .when(F.col("id").isin(categorical_vars), F.lit("categorical"))
                .when(F.col("id").isin(binary_vars), F.lit("binary")),
            )
            .withColumn(
                "share_most_common_all", F.col("n_most_common_all") / F.col("n_all")
            )
            .withColumn(
                "share_most_common_without_missings_all",
                F.col("n_most_common_without_missings_all")
                / F.col("n_not_missing_all"),
            )
        )

        self.numerical_vars = numerical_vars.copy()
        self.categorical_vars = categorical_vars.copy()
        self.binary_vars = binary_vars.copy()

        return combined

    @check_active
    def _update_variables_categories(
        self, df_var_info: DataFrame, analyse_all_features: bool = False
    ) -> DataFrame:
        """Enhance variable categorisation.

        Originally, predictors are categories into 3 categories: numerical, categorical and binary.
        It's checked whether it makes sense to analyse individual variable.
        If not, this variable is categorised as not relevant.
        Not relevant variables are further categories into following sub-categories:
        - high missing rate
        - one distinct value
        - low share of most common value
        - high share of most common value

        Two additional columns are added to df_var_info:
        - variable_status - 'ok' vs. 'not ok', flag that determines whether feature should be later considered for Quick Insights
        - variable_status_details - 'ok' vs. 'high missing rate', 'high share of dominant value', 'low share of dominant value' or 'one distinct value'

        Role of analyse_all_features flag:
        - If analyse_all_features = True then all features are considered as relevant (i.e. variable_status = 'ok').
        - Otherwise, only features with variable_status_details = 'ok' are considered as relevant (i.e. variable_status = 'ok').

        Args:
            df_var_info (DataFrame): df with summary information about individual predictors/features
            analyse_all_features (bool): flag whether all features should be considered as relevant. Defaults to False.

        Returns:
            DataFrame: updated df with summary information about individual predictors/features
        """

        df_var_info = df_var_info.withColumn(
            "variable_status_details",
            F.when(
                F.col("missing_rate_all") >= self.missing_rate_th,
                F.lit("high missing rate"),
            )
            .when(
                (F.col("share_most_common_all") >= self.max_share_single_value)
                | (
                    F.col("share_most_common_without_missings_all")
                    >= self.max_share_single_value
                ),
                F.lit("high share of dominant value"),
            )
            .when(
                (F.col("share_most_common_all") <= self.min_share_single_value)
                | (
                    F.col("share_most_common_without_missings_all")
                    <= self.min_share_single_value
                ),
                F.lit("low share of dominant value"),
            )
            .when(F.col("n_distinct_all") <= 1, F.lit("one distinct value"))
            .otherwise(F.lit("ok")),
        )

        if analyse_all_features:
            df_var_info = df_var_info.withColumn("variable_status", F.lit("ok"))
        else:
            df_var_info = df_var_info.withColumn(
                "variable_status",
                F.when(F.col("variable_status_details") == "ok", F.lit("ok")).otherwise(
                    "not ok"
                ),
            )

        df_var_info = df_var_info.withColumn(
            "id_output_name",
            F.when(
                (F.col("variable_status") == "ok") & (F.col("var_type") != "numerical"),
                F.col("id"),
            ).when(
                (F.col("variable_status") == "ok") & (F.col("var_type") == "numerical"),
                F.concat(F.col("id"), F.lit("_binned")),
            ),
        )

        rel_vars_list = [
            row["id"] for row in df_var_info.collect() if row["variable_status"] == "ok"
        ]
        not_rel_vars_list = [
            row["id"] for row in df_var_info.collect() if row["variable_status"] != "ok"
        ]

        # update categories of variables
        self.numerical_vars = [
            var for var in self.numerical_vars.copy() if var in rel_vars_list
        ]
        self.categorical_vars = [
            var for var in self.categorical_vars.copy() if var in rel_vars_list
        ]
        self.binary_vars = [
            var for var in self.binary_vars.copy() if var in rel_vars_list
        ]
        self.not_relevant_vars = not_rel_vars_list

        return df_var_info

    @check_active
    def _missings_treatment(self, df: DataFrame) -> DataFrame:
        """Perform treatment of missings

        Null values are replaced by '__missing__' placeholder.

        Args:
            df (DataFrame): considered sample

        Returns:
            DataFrame: updated sample with replaced null values
        """
        df = df.select(
            *[F.col(col) for col in df.columns if col not in self.binary_vars],
            *[F.col(col).cast("string").alias(col) for col in self.binary_vars],
        )

        return df.fillna("__missing__", subset=self.categorical_vars).fillna(
            "__missing__", subset=self.binary_vars
        )

    @check_active
    def _reduce_number_of_categories(self, df: DataFrame) -> DataFrame:
        """Runner used to reduce number of distinct categories for categorial variables.

        Args:
            df (DataFrame): sample to be analysed

        Returns:
            DataFrame: sample with updated (reduced) categories
        """
        cat_bin_reducer = CategoricalBinsReducer()
        cat_bin_vars = self.categorical_vars.copy()

        bin_params = {
            "reduction_percentage": self.reduction_percentage,
            "cat_var_max_bins": self.cat_var_max_bins,
            "cat_var_min_bins": self.cat_var_min_bins,
            "cat_var_min_bin_share": self.cat_var_min_bin_share,
        }

        return cat_bin_reducer.reduce(
            df=df, columns=cat_bin_vars, bin_params=bin_params
        )

    @check_active
    def _perform_binning(self, df: DataFrame, vars_list: list = None) -> DataFrame:
        """Perform binning of numerical variables.

        If vars_list is not specified, then all numerical columns are considered.

        Args:
            df (DataFrame): considered sample
            vars_list (list, optional): list of variables to be considered. Defaults to None.

        Returns:
            DataFrame: df with binned variables
        """
        bin_params = {
            "lower_percentile_percentage": self.lower_percentile_percentage,
            "higher_percentile_percentage": self.higher_percentile_percentage,
            "accuracy": self.accuracy,
            "bin_count": self.bin_count,
        }

        int_binning = IntegralBinsGenerator().generate(
            df=df, vars_list=vars_list, bin_params=bin_params
        )
        float_binning = FloatingPointBinsGenerator().generate(
            df=df, vars_list=vars_list, bin_params=bin_params
        )

        binning_rules = {
            **int_binning.collect()[0].asDict(),
            **float_binning.collect()[0].asDict(),
        }

        splits = []
        binning_input_cols = []
        problematic_cols = []
        mapping = {}

        for col in binning_rules:
            if len(binning_rules[col]) > 1 and col != "TARGET":
                binning_rules_loc = (
                    [-float("inf")] + binning_rules[col] + [float("inf")]
                )
                splits.append(binning_rules_loc.copy())
                binning_input_cols.append(col)

                # make binning plots nicer (only for labels)
                binning_rules_loc = _round_binning_splits(binning_rules_loc)
                # prepare mapping to convert bin number to label
                mapping_loc = {
                    i: f"[{binning_rules_loc[i]}, {binning_rules_loc[i+1]})"
                    for i, split in enumerate(binning_rules_loc)
                    if i < len(binning_rules_loc) - 1
                }

                mapping[col] = F.create_map(
                    [F.lit(x) for x in chain(*mapping_loc.items())]
                )
            elif col != "TARGET":
                problematic_cols.append(col)

        binning_output_cols = [f"{col}_binned" for col in binning_input_cols]

        bucketizer = Bucketizer(
            splitsArray=splits,
            inputCols=binning_input_cols,
            outputCols=binning_output_cols,
            handleInvalid="keep",
        )

        df_binned = bucketizer.transform(df)

        for var in mapping:
            df_binned = df_binned.withColumn(
                f"{var}_binned", mapping[var][df_binned[f"{var}_binned"].cast("string")]
            )

        df_binned = df_binned.fillna("__missing__", subset=binning_output_cols)

        # treat variables with problematic binning - no or one split only
        df_binned = self._treat_problematic_binning(
            df=df_binned, vars_list=problematic_cols
        )

        return df_binned

    @check_active
    def _treat_problematic_binning(
        self, df: DataFrame, vars_list: list, max_cat_th: int = 10
    ) -> DataFrame:
        counts_distinct_spec = [
            F.approx_count_distinct(F.col(c)).alias(c) for c in vars_list
        ]

        n_distinct = df.select(*counts_distinct_spec).collect()[0].asDict()

        df = df.select(
            "*",
            *[F.col(var).cast("string").alias(f"{var}_binned") for var in vars_list],
        )

        df = df.fillna("__missing__", subset=[f"{var}_binned" for var in vars_list])

        # reduce categories (if needed)
        vars_list_too_many_cats = [
            f"{var}_binned" for var in n_distinct if n_distinct[var] >= max_cat_th
        ]

        if len(vars_list_too_many_cats) > 0:
            cat_bin_reducer = CategoricalBinsReducer()

            bin_params = {
                "reduction_percentage": self.reduction_percentage,
                "cat_var_max_bins": self.cat_var_max_bins,
                "cat_var_min_bins": self.cat_var_min_bins,
                "cat_var_min_bin_share": self.cat_var_min_bin_share,
            }

            df = cat_bin_reducer.reduce(
                df=df, columns=vars_list_too_many_cats, bin_params=bin_params
            )

        return df

    @check_active
    def get_preprocessed_table(self):
        """Runner to preprocess feature store table

        Dataframe with summary per individual features.

        Moreover, relevant features (variable status == "ok") are processed as follows:
        - for numerical variables binning is performed
        - for categorical variables
            - categories are reduced to achieve reasonable number of categories
            - small categories are grouped into category __other__
        - missing values are replaced by category __missing__

        """

        df = self._load_raw_sample()

        print("Running summary of features")
        start_time = time.time()
        df_var_info = self._get_variables_info(df=df)

        df_var_info = self._update_variables_categories(
            df_var_info=df_var_info, analyse_all_features=self.analyse_all_features
        )
        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        print("Running treatment of missings")
        start_time = time.time()
        df = self._missings_treatment(df=df)
        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        print("Reducing number of categories")
        start_time = time.time()
        df = self._reduce_number_of_categories(df=df)
        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        print("Performing binning")
        start_time = time.time()
        if len(self.numerical_vars):
            df = self._perform_binning(df=df, vars_list=self.numerical_vars)
        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        # save outputs
        print(
            "Saving outputs (processed feature store and table with features's summary)"
        )
        start_time = time.time()

        df_var_info.write.mode("overwrite").option(
            "overwriteSchema", "true"
        ).saveAsTable(self.stats_output_table_name)

        df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
            self.features_table_processed
        )
        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")
