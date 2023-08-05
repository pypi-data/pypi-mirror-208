from abc import get_cache_token
from typing import Tuple
import math
import time
import numpy as np
from sklearn.linear_model import LogisticRegression as LogisticRegressionSklearn
from sklearn.metrics import roc_auc_score
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql import functions as F, types as T, DataFrame, SparkSession
from odapqi.api.functions import check_active
from odapqi.api.qi_helpers import (
    _get_contigency_tables,
    _categorise_metric,
    _transpose_df,
    WOE_IV,
)


PSI_CATEGORIES_FEATURE_SELECTION = {
    "Suspicious Predictive Power": 0.5,
    "Strong predictive Power": 0.3,
    "Medium predictive Power": 0.1,
    "Weak predictive Power": 0.02,
    "Not useful for prediction": 0.0,
}

PSI_CATEGORIES_FEATURE_MONITORING = {
    "Significant change": 0.2,
    "Slight change": 0.1,
    "No significant change": 0.0,
}


@F.udf(returnType=T.DoubleType())
def ith(v, i):
    try:
        return float(v[i])
    except ValueError:
        return None


class QiApi:
    """Run Quick Insights

    Details:
    - analysed sample is splitted into two subsamples - OBS (target) vs. BASE
    - differences between these samples are analysed for individual variables/features

    To use Quick Insights you can use following classes (see ./qi_runners.py):
    - features selection: QiFeaturesSelection
    - features monitoring: QiFeaturesMonitoring
    It is expected that this class would be called via the classes mentioned above.

    """

    def __init__(
        self,
        spark: SparkSession,
        features_table_processed: str,
        feature_store_stats: str,
        obs_cond: str,
        base_cond: str = None,
        features_list: list = None,
        features_to_exclude_list: list = None,
        run_missings_rate: bool = False,
        run_logistic_regression: bool = False,
        run_analysis_without_missings: bool = False,
        save_qi_results: bool = False,
        qi_results_table_name: str = None,
        save_binning_overview: bool = False,
        binning_overview_table_name: str = None,
        regression_estimator: str = "spark",
        analysis_mode: str = "FEATURES_SELECTION",
        base_name: str = "BASE",
        obs_name: str = "TARGET",
    ) -> None:
        """_summary_

        Args:
            spark (SparkSession): spark session
            feature_store_processed (str, optional): name of processed feature store table. Defaults to None.
            feature_store_stats (str, optional): name of table with summary of features Defaults to None.
            obs_cond (str): condition to select observations for OBS sample
            base_cond (str, optional): condition to select observations for BASE sample. Defaults to None.
            features_list (list, optional): list of features to consider (if not specified all features considered). Defaults to None.
            run_missings_rate (bool, optional): flag whetehr to run missing rate analysis. Defaults to False.
            run_logistic_regression (bool, optional): flag whether to run logistic regression analysis. Defaults to False.
            run_analysis_without_missings (bool, optional): flag whether to perform analysis without missing values. Defaults to False.
            save_qi_results (bool, optional): flag whether to save QI results. Defaults to False.
            qi_results_table_name (str, optional): name of output table with QI results. Defaults to None.
            save_binning_overview (bool, optional): flag whether to save binning overview. Defaults to False.
            binning_overview_table_name (str, optional): name of table with binning overview. Defaults to None.
            regression_estimator (str, optional): method to estimate logistic regression: spark vs sklearn. Defaults to "spark".
            analysis_mode (str, optional): usecase identifiactor: FEATURES_SELECTION vs. FEATURES_MONITORING. Defaults to "FEATURES_SELECTION".
            base_name (str, optional): label for BASE sample. Defaults to "BASE".
            obs_name (str, optional): label for OBS sample. Defaults to "TARGET".
        """
        self.features_table_processed = features_table_processed
        self.feature_store_stats = feature_store_stats
        self.active = True
        self.spark = spark

        self.base_cond = base_cond
        self.obs_cond = obs_cond
        self.run_missings_rate = run_missings_rate
        self.run_logistic_regression = run_logistic_regression
        self.run_analysis_without_missings = run_analysis_without_missings
        self.regression_estimator = regression_estimator
        self.analysis_mode = analysis_mode
        self.base_name = base_name
        self.obs_name = obs_name
        self.save_binning_overview = save_binning_overview
        self.binning_overview_table_name = binning_overview_table_name

        if isinstance(features_list, str):
            self.vars_list = [features_list]
        else:
            self.vars_list = features_list

        if isinstance(features_to_exclude_list, str):
            self.features_to_exclude_list = [features_to_exclude_list]
        else:
            self.features_to_exclude_list = features_to_exclude_list

        if self.analysis_mode == "FEATURES_SELECTION":
            self.psi_thresholds = PSI_CATEGORIES_FEATURE_SELECTION
        else:
            self.psi_thresholds = PSI_CATEGORIES_FEATURE_MONITORING

        # validate inputs
        if self.save_binning_overview:
            if self.binning_overview_table_name:
                self.binning_overview_wide_table_name = (
                    f"{self.binning_overview_table_name}_wide"
                )
                self.binning_overview_long_table_name = (
                    f"{self.binning_overview_table_name}_long"
                )
            else:
                self.save_binning_overview = False
                print(
                    "Name of output table for binning overview wasn't specified. Hence, binning overview wouldn't be saved."
                )

        if save_qi_results and not qi_results_table_name:
            self.save_qi_results = False
            self.qi_results_table_name = None
            print(
                "Name of output table for QI results wasn't specified. Hence, QI results wouldn't be saved."
            )
        else:
            self.save_qi_results = save_qi_results
            self.qi_results_table_name = qi_results_table_name

    @check_active
    def _set_condition(self) -> None:
        """Process base condition and define condition for whole sample (i.e. OBS + BASE)"""
        if self.base_cond:
            self.total_cond = " OR ".join(
                [cond for cond in [self.base_cond, self.obs_cond] if cond]
            )
        else:
            self.total_cond = None
            print(
                "Base condition (base_cond) not specified. Whole sample would be loaded and records not fulfiling obs_cond are considered as base sample."
            )

    @check_active
    def _load_processed_sample(self) -> DataFrame:
        """load processed feature store.

        Processed feature store is loaded and flag determining BASE and OBS sample is constructed.
        Moreover, TARGET flag is added (TARGET = 1 for OBS sample and TARGET = 0 for BASE sample).

        Returns:
            DataFrame: loaded dataframe
        """
        if self.total_cond:
            df = self.spark.read.table(self.features_table_processed).filter(
                F.expr(f"({self.total_cond}) OR ({self.obs_cond})")
            )
        else:
            df = self.spark.read.table(
                self.features_table_processed
            )  # load whole sample if base condition is not specified

        # add sample flag
        df = df.withColumn(
            "SAMPLE_NAME",
            F.when(F.expr(self.obs_cond), F.lit("OBS")).otherwise(F.lit("BASE")),
        ).withColumn(
            "TARGET",
            F.when(F.col("SAMPLE_NAME") == "OBS", F.lit(1)).otherwise(F.lit(0)),
        )

        return df

    @check_active
    def _feature_store_stats(self) -> DataFrame:
        """Load feature store stats table that was created during pre-processing

        Returns:
            DataFrame: laoded feature store stats table.
        """
        return self.spark.read.table(self.feature_store_stats)

    @check_active
    def _get_counts(self, df: DataFrame) -> None:
        """Get number of observations in individual samples.

        Args:
            df (DataFrame): loaded feature store sample
        """
        cts_base = df.filter(F.col("SAMPLE_NAME") == "BASE").count()
        cts_obs = df.filter(F.col("SAMPLE_NAME") == "OBS").count()
        cts_all = cts_base + cts_obs

        self.cts_base = cts_base
        self.cts_obs = cts_obs
        self.cts_all = cts_all

        print(
            f"Number of observations in {self.base_name} (BASE) sample: {cts_base} and {self.obs_name} (OBS) sample: {cts_obs}"
        )

    @check_active
    def _get_relevant_variables(self, df_var_info: DataFrame) -> DataFrame:
        """Helper to select relevant variables from df_var_info

        Optionally, vars_list can be used to specify only subset of variables/features.

        Args:
            df_var_info (DataFrame): data frame with information about variables

        Returns:
            DataFrame: df_var_info with only relevant features
        """

        if self.vars_list:
            df_var_info = df_var_info.filter(F.col("id").isin(self.vars_list))

        if self.features_to_exclude_list:
            df_var_info = df_var_info.filter(
                ~F.col("id").isin(self.features_to_exclude_list)
            )

        var_info = df_var_info.filter(F.col("variable_status") == "ok").collect()

        relevant_vars = [var.id_output_name for var in var_info]

        if not relevant_vars:
            raise ValueError(
                "No features selected. Please check that 'feature_stats' contains features available in 'feature_store' sample. Moreover, please also check parameters: features_list and features_to_exclude_list"
            )

        self.relevant_vars = relevant_vars

        return df_var_info

    @check_active
    def _keep_only_relevant_variables(self, df: DataFrame) -> DataFrame:
        """Helper used to keep only relevant variables for analysis

        The following features are kept:
        - TARGET (sample identification)
        - SAMPLE_NAME (sample identification)
        - self.relevant_vars (relevant features)

        Args:
            df (DataFrame): sample to be analysed

        Returns:
            DataFrame: sample with the relevant variables
        """
        not_available_vars = [
            col for col in self.relevant_vars if col not in df.columns
        ]
        if len(not_available_vars) > 0:
            print(
                f"The following variables are not available in the sample: {not_available_vars}"
            )

        self.relevant_vars = [col for col in self.relevant_vars if col in df.columns]

        return df.select(
            "TARGET",
            "SAMPLE_NAME",
            *self.relevant_vars,
        )

    @check_active
    def _analyse_categorical_vars(
        self, df: DataFrame, vars_list: list, keep_missings: bool = True
    ) -> DataFrame:
        """Analyse categorical variables

        The goal is to compare whether distribution of feature in BASE and OBS sample is similar or different.

        The following statistics are calculated:
        - distance - sum of differences (in absolute values) between shares for individual categories
        - JLH - maximum value of differences (in absolute values) between shares for individual categories
        - JLH scaled - maximum value of differences (in absolute values) between shares for individual categories multipled by lift
        - PSI - population stability index

        Moreover, PSI values are categorised using splits specified by self.psi_thresholds.

        Args:
            df (DataFrame): considered sample
            vars_list (list): list of variables to be considered
            keep_missings (bool, optional): flag whether missings should be considered for analysis. Defaults to True.

        Returns:
            DataFrame: df with results of analysis
        """

        cat_var_test_results = []

        cont_cts = _get_contigency_tables(
            df=df, vars_list=vars_list, keep_missings=keep_missings
        )

        for var in cont_cts:
            cont_cts_var = [
                [val["BASE"] for val in cont_cts[var]],
                [val["OBS"] for val in cont_cts[var]],
            ]

            N = np.sum(cont_cts_var, axis=1)

            if N[0] == 0 or N[1] == 0:
                _problematic_samples = []
                if N[0] == 0:
                    _problematic_samples.append(self.base_name)
                if N[1] == 0:
                    _problematic_samples.append(self.obs_name)
                # if sum of observations for one sample is 0 then skip this variable
                print(
                    f"Zero number of observations in sample: {_problematic_samples} for feature: {var}. Most likely no non-missing values in given sample"
                )
                continue

            props = [cont_cts_var[0] / N[0], cont_cts_var[1] / N[1]]
            distance_k = sum([abs(x - y) for x, y in zip(props[0], props[1])])

            jlh_k = max([abs(x - y) for x, y in zip(props[0], props[1])])

            try:
                jlh_scaled_k = max(
                    [
                        abs(x - y) / max(abs(x / y), abs(y / x))
                        for x, y in zip(props[0], props[1])
                        if x > 0 and y > 0
                    ]
                )
            except Exception as e:
                jlh_scaled_k = None
                print(f"Can not calculate scaled JLH for: {var}, {e}")

            try:
                psi_k = sum(
                    [
                        (x - y) * math.log(x / y)
                        for x, y in zip(props[0], props[1])
                        if x > 0 and y > 0
                    ]
                )
            except Exception as e:
                psi_k = None
                print(f"Can not calculate PSI for: {var}, {e}")

            cat_var_test_results.append(
                {
                    "id": var.replace("_binned", ""),
                    "jlh": float(jlh_k) if jlh_k is not None else None,
                    "jlh_scaled": float(jlh_scaled_k)
                    if jlh_scaled_k is not None
                    else None,
                    "distance": float(distance_k) if distance_k is not None else None,
                    "psi": float(psi_k) if psi_k is not None else None,
                }
            )

        schema = T.StructType(
            [
                T.StructField("id", T.StringType(), True),
                T.StructField("jlh", T.DoubleType(), True),
                T.StructField("jlh_scaled", T.DoubleType(), True),
                T.StructField("distance", T.DoubleType(), True),
                T.StructField("psi", T.DoubleType(), True),
            ]
        )

        cat_var_test_results_df = self.spark.createDataFrame(
            cat_var_test_results, schema=schema
        )

        cat_var_test_results_df = _categorise_metric(
            df=cat_var_test_results_df,
            categories=self.psi_thresholds,
            input_col_name="psi",
            output_col_name="psi_category",
        )

        return cat_var_test_results_df

    @check_active
    def _estimate_regression(
        self,
        df: DataFrame,
        vars_list: list,
        regression_estimator: str,
    ) -> list:
        """Runner to estimate univariate logistic regression

        It is possible to specify regression estimator:
        - sklearn
            - using standard sklearn logistic regression estimator
            - spark data frame is collected into pandas dataframe (not suitable for large samples)
            - for smaller samples tends to be faster than mlflow estimator
        - spark
            - unsing mlflow
            - it is not needed to collect dataframe to pandas

        Args:
            df (DataFrame): considered feature store
            vars_list (list): list of variables to be considered
            regression_estimator (str): type of regression estimator - sklearn vs. spark

        Returns:
            list: list with dicts containing regression results
        """
        results_list = []

        if regression_estimator == "sklearn":
            # using sklearn

            df_pd = df.select("TARGET", *vars_list).toPandas()

            y = df_pd["TARGET"]
            logreg = LogisticRegressionSklearn()

            for var in vars_list:
                try:
                    x = df_pd[[var]]

                    clf = logreg.fit(X=x, y=y)
                    score = clf.score(X=x, y=y)
                    roc = roc_auc_score(y, clf.predict_proba(x)[:, 1])

                    # save results
                    results_list.append(
                        {
                            "id": var.replace("_binned", "").replace("_WOE", ""),
                            "area_under_roc": float(roc),
                            "gini": float(2 * roc - 1),
                            "r2": float(score),
                        }
                    )
                except Exception as e:
                    print(
                        f"Cannot estimate logistic regression for: {var.replace('_binned', '').replace('_WOE', '')}, {e}"
                    )
        else:
            # using spark
            lr = LogisticRegression().setLabelCol("TARGET").setFeaturesCol("features")
            r2 = RegressionEvaluator(
                labelCol="TARGET", predictionCol="score2", metricName="r2"
            )

            for var in vars_list:
                try:
                    # assembler
                    assembler = VectorAssembler(
                        inputCols=[var],
                        outputCol="features",
                        handleInvalid="skip",
                    )
                    df_model = assembler.transform(df).select("TARGET", "features")

                    # fit model
                    lr_model = lr.fit(df_model)

                    df_pred = (
                        lr_model.transform(df_model)
                        .withColumn("score1", ith("probability", F.lit(0)))
                        .withColumn("score2", ith("probability", F.lit(1)))
                    )

                    # save results
                    results_list.append(
                        {
                            "id": var.replace("_binned", "").replace("_WOE", ""),
                            "area_under_roc": float(lr_model.summary.areaUnderROC),
                            "gini": float(2 * lr_model.summary.areaUnderROC - 1),
                            "r2": float(r2.evaluate(df_pred)),
                        }
                    )
                except Exception as e:
                    print(
                        f"Cannot estimate logistic regression for: {var.replace('_binned', '').replace('_WOE', '')}, {e}"
                    )

        return results_list

    @check_active
    def _woe_transform(
        self, df: DataFrame, input_cols_list: list, keep_missings: bool = True
    ) -> DataFrame:
        """Perform WoE transformation.

        WoE means Weight of Evidence transformation.
        Details: https://www.listendata.com/2015/03/weight-of-evidence-woe-and-information.html

        Suffix _WOE is added to features names.

        Args:
            df (DataFrame): considered table.
            input_cols_list (list): list of features to be considered.
            keep_missings (bool, optional): flag whether missings should be considered for analysis. Defaults to True.

        Returns:
            DataFrame: dataframe with transformed features.
        """
        output_cols = [f"{var}_WOE" for var in input_cols_list]

        if keep_missings:
            woe = WOE_IV(df, input_cols_list, "TARGET", 1)

            woe.fit()
            encoded_df = woe.transform(df)
        else:
            # we need to loop over variables
            for var in input_cols_list:
                df_var = df.filter(F.col(var) != "__missing__")

                woe = WOE_IV(df_var, [var], "TARGET", 1)

                woe.fit()
                df = woe.transform(df)

            encoded_df = df

        return encoded_df.select("TARGET", *output_cols), output_cols

    @check_active
    def _perform_univariate_logistic_regression(
        self,
        df: DataFrame,
        vars_list: list,
        regression_estimator: str = "spark",
        keep_missings: bool = True,
    ) -> DataFrame:
        """Perform univariate logistic regression to analyse individual features.

        Args:
            df (DataFrame): considered sample
            vars_list (list): list of variables to be considered
            regression_estimator (str, optional): type of regression estimator. Defaults to "spark".
            keep_missings (bool, optional): flag whether missings should be considered for analysis. Defaults to True.

        Returns:
            DataFrame: df with results of this analysis
        """
        results_list = []

        # WoE transformation
        print(f"{'':<2} Running WoE transformation:")
        start_time = time.time()
        df, input_cols_relevant_list = self._woe_transform(
            df=df, input_cols_list=vars_list, keep_missings=keep_missings
        )
        end_time = time.time()
        print(f"{'':<4} code execution: {round(end_time - start_time, 1)}s.", "\n")

        # Logistic regression
        print(f"{'':<2} Running univariate logistic regression:")
        start_time = time.time()
        results_list = self._estimate_regression(
            df=df,
            vars_list=input_cols_relevant_list,
            regression_estimator=regression_estimator,
        )
        end_time = time.time()
        print(f"{'':<4} code execution: {round(end_time - start_time, 1)}s.", "\n")

        schema = T.StructType(
            [
                T.StructField("id", T.StringType(), True),
                T.StructField("area_under_roc", T.DoubleType(), True),
                T.StructField("gini", T.DoubleType(), True),
                T.StructField("r2", T.DoubleType(), True),
            ]
        )

        reg_results_df = self.spark.createDataFrame(results_list, schema=schema)

        return reg_results_df

    @check_active
    def _prepare_binning_overview(
        self, df: DataFrame, vars_list: list, keep_missings: bool = True
    ) -> Tuple[DataFrame, DataFrame]:
        """Prepare overview of binning (e.g. distribution of individual bins between samples)

        - long format is useful to prepare bar plots summarizing bin distribution
        - wide format is relevant for showing table providing information about individual bins

        Args:
            df (DataFrame): sample with binned variable
            vars_list (list): list of variables to be considered

        Returns:
            Tuple[DataFrame, DataFrame]: binning overview in long format, binning overview in wide format
        """
        # TODO: try to reuse _get_contigency_tables to make code quicker
        df_binning_ov = self.spark.createDataFrame([], T.StructType([]))
        df_binning_ov_wide = self.spark.createDataFrame([], T.StructType([]))

        if keep_missings:
            cts_obs_var = self.cts_obs
            cts_base_var = self.cts_base
            cts_all_var = self.cts_all

        for var in vars_list:
            if keep_missings:
                df_var = df
            else:
                df_var = df.filter(F.col(var) != "__missing__")
                cts_base_var = df_var.filter(F.col("SAMPLE_NAME") == "BASE").count()
                cts_obs_var = df_var.filter(F.col("SAMPLE_NAME") == "OBS").count()
                cts_all_var = cts_base_var + cts_obs_var

            binning_ov = (
                df_var.groupBy("SAMPLE_NAME", var)
                .agg(
                    F.count(F.lit(1)).alias("N"),
                )
                .withColumn(
                    "N_SAMPLE",
                    F.when(F.col("SAMPLE_NAME") == "OBS", F.lit(cts_obs_var)).otherwise(
                        F.lit(cts_base_var)
                    ),
                )
                .withColumn("SHARE_SAMPLE", F.col("N") / F.col("N_SAMPLE"))
                .fillna(0)
                .orderBy("SAMPLE_NAME", var)
            )

            binning_ov_wide = (
                binning_ov.groupBy(var)
                .pivot("SAMPLE_NAME", ["OBS", "BASE"])
                .agg(
                    F.first("N").alias("N"),
                    F.first("N_SAMPLE").alias("N_SAMPLE"),
                    F.first("SHARE_SAMPLE").alias("SHARE_SAMPLE"),
                )
                .withColumn(
                    "SHARE_OBS_SAMPLE_TOTAL",
                    F.round(F.lit(cts_obs_var) / F.lit(cts_all_var), 2),
                )
                .withColumn(
                    "SHARE_OBS_SAMPLE_PER_BIN",
                    F.round(F.col("OBS_N") / (F.col("BASE_N") + F.col("OBS_N")), 2),
                )
                .fillna(0)
                .withColumn(
                    "PSI",
                    (F.col("BASE_SHARE_SAMPLE") - F.col("OBS_SHARE_SAMPLE"))
                    * (F.log(F.col("BASE_SHARE_SAMPLE") / F.col("OBS_SHARE_SAMPLE"))),
                )
                .orderBy(var)
                .select(
                    var,
                    F.col("BASE_N").alias(f"N_{self.base_name}"),
                    F.col("OBS_N").alias(f"N_{self.obs_name}"),
                    F.round(F.col("BASE_SHARE_SAMPLE"), 2).alias(
                        f"Share_{self.base_name}"
                    ),
                    F.round(F.col("OBS_SHARE_SAMPLE"), 2).alias(
                        f"Share_{self.obs_name}"
                    ),
                    F.col("SHARE_OBS_SAMPLE_PER_BIN").alias(
                        f"Share_of_{self.obs_name}_sample_per_bin"
                    ),
                    F.round(
                        F.col("SHARE_OBS_SAMPLE_PER_BIN")
                        - F.col("SHARE_OBS_SAMPLE_TOTAL"),
                        2,
                    ).alias(f"Share_of_{self.obs_name}_sample_per_bin_vs_total_share"),
                    F.round(F.col("PSI"), 3).alias("PSI"),
                )
            )

            # nicer names
            binning_ov = (
                binning_ov.withColumn(
                    "SAMPLE_NAME",
                    F.when(
                        F.col("SAMPLE_NAME") == "BASE", F.lit(self.base_name)
                    ).otherwise(F.lit(self.obs_name)),
                )
                .withColumnRenamed("SAMPLE_NAME", "Sample_name")
                .withColumnRenamed("SHARE_SAMPLE", "Share_per_sample")
            )

            # remove binned suffix
            binning_ov = binning_ov.withColumn(
                "feature", F.lit(var.replace("_binned", ""))
            ).withColumnRenamed(var, "Bin")
            binning_ov_wide = binning_ov_wide.withColumn(
                "feature", F.lit(var.replace("_binned", ""))
            ).withColumnRenamed(var, "Bin")

            df_binning_ov = df_binning_ov.unionByName(
                binning_ov, allowMissingColumns=True
            )
            df_binning_ov_wide = df_binning_ov_wide.unionByName(
                binning_ov_wide, allowMissingColumns=True
            )

        return df_binning_ov, df_binning_ov_wide

    @check_active
    def _missings_overview(
        self,
        df: DataFrame,
        vars_list: list,
    ) -> DataFrame:
        """Summary of missing rates per OBS and BASE sample

        Args:
            df (DataFrame): considered sample
            vars_list (list): list of features to analyse

        Returns:
            DataFrame: table with missing rate summary
        """

        def _helper_missing_rate(df: DataFrame, vars_list: list) -> DataFrame:
            """Helper to calculate missing rate"""
            n_obs_sample = df.groupBy().count().collect()[0][0]
            counts_spec = [
                F.sum(
                    F.when(
                        (F.col(col) == "__missing__") | (F.col(col).isNull()), F.lit(1)
                    ).otherwise(F.lit(0))
                ).alias(col)
                for col in vars_list
            ]

            df_counts = df.select(F.lit("count_missing").alias("summary"), *counts_spec)

            df_counts = _transpose_df(df=df_counts)

            df_counts = df_counts.withColumn("n", F.lit(n_obs_sample)).withColumn(
                "missing_rate", F.col("count_missing") / F.col("n")
            )

            return df_counts

        # BASE sample
        df_missing_base = _helper_missing_rate(
            df=df.filter(F.col("SAMPLE_NAME") == "BASE"), vars_list=vars_list
        ).select(
            F.regexp_replace("summary", "_binned", "").alias("id"),
            F.col("missing_rate").alias(f"missing_rate_{self.base_name}"),
        )

        df_missing_obs = _helper_missing_rate(
            df=df.filter(F.col("SAMPLE_NAME") == "OBS"), vars_list=vars_list
        ).select(
            F.regexp_replace("summary", "_binned", "").alias("id"),
            F.col("missing_rate").alias(f"missing_rate_{self.obs_name}"),
        )

        return df_missing_base.join(df_missing_obs, how="left", on="id")

    @staticmethod
    def _order_results_by_psi(
        qi_results_df: DataFrame,
        qi_results_without_missings_df: DataFrame,
        binning_overview_wide: DataFrame,
        binning_overview_wide_without_missings: DataFrame,
        binning_overview_long: DataFrame,
    ):
        def _order_with_mapping(df: DataFrame, order_mapping: dict, id_col: str) -> DataFrame:
            return (
                df.withColumn("order_psi", F.expr(order_mapping))
                .orderBy("order_psi", id_col)
            )

        # order by PSI
        qi_results_df = qi_results_df.orderBy(F.desc("psi"))

        # create mapping between feature name and order
        vars_order = [row["id"] for row in qi_results_df.collect()]
        vars_order_feature = (
            "CASE "
            + " ".join(
                [f"WHEN feature = '{var}' THEN {i}" for i, var in enumerate(vars_order)]
            )
            + " END"
        )

        # reorder other outputs
        qi_results_without_missings_df = qi_results_without_missings_df.orderBy(F.desc("psi"))
        binning_overview_wide = _order_with_mapping(
            df=binning_overview_wide, order_mapping=vars_order_feature, id_col="Bin",
        )
        binning_overview_wide_without_missings = binning_overview_wide_without_missings.orderBy(F.desc("psi"))
        binning_overview_long = _order_with_mapping(
            df=binning_overview_long, order_mapping=vars_order_feature, id_col="Bin",
        )

        return (
            qi_results_df,
            qi_results_without_missings_df,
            binning_overview_wide,
            binning_overview_wide_without_missings,
            binning_overview_long,
        )

    @check_active
    def get_qi(self) -> dict:
        """Runner to calculate Quick Insights (QI)

        This running performas the followings steps:
        - load sample
        - load information about features to determine what features are relevant
        - analysis of features (categorical features and categorised numerical features)
        - univariate logistic regression (calculation of IV, Gini, R2)
            - IV is always calculated
            - logistic regression and corresponding statistics is optional

        The output structure:
         {
            "analysed features": df with results of analysis of numerical and categorical variables,
            "analysed features - without missings": same as "analysed features" but with excluded missing values,
            "problematic features": df describing problematic features,
            "binning overview - long": overview of binning - long version of table,
            "binning overview - wide": overview of binning - wide version of table,
        }

        Returns:
            dict: Qucik Insights results
        """
        # load inputs
        print("Loading inputs")
        start_time = time.time()
        self._set_condition()

        df = self._load_processed_sample()

        self._get_counts(df)

        df_var_info = self._feature_store_stats()

        df_var_info = self._get_relevant_variables(df_var_info=df_var_info)

        df = self._keep_only_relevant_variables(df=df)
        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        # intialize output
        qi_results_df = df_var_info.select(
            "id",
            F.round("missing_rate_all", 2).alias("missing_rate_all"),
            F.round("share_most_common_all", 2).alias("share_most_common_all"),
            F.round("share_most_common_without_missings_all", 2).alias(
                "share_most_common_without_missings_all"
            ),
            "var_type",
            "variable_status",
            "variable_status_details",
        )

        # missings analysis
        if self.run_missings_rate:
            print("Running missings analysis")
            start_time = time.time()
            qi_missings_df = self._missings_overview(
                df=df, vars_list=self.relevant_vars
            )

            qi_results_df = qi_results_df.join(
                qi_missings_df.select(
                    "id",
                    F.round(f"missing_rate_{self.base_name}", 2).alias(
                        f"missing_rate_{self.base_name}"
                    ),
                    F.round(f"missing_rate_{self.obs_name}", 2).alias(
                        f"missing_rate_{self.obs_name}"
                    ),
                ),
                how="left",
                on="id",
            )

            end_time = time.time()
            print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        # categorical tests
        print("Runnning basic tests (distance, JLH, PSI)")
        start_time = time.time()
        qi_test_results_df = self._analyse_categorical_vars(
            df=df, vars_list=self.relevant_vars, keep_missings=True
        )
        qi_results_df = qi_results_df.join(
            qi_test_results_df.select(
                "id",
                F.round(F.col("jlh"), 2).alias("jlh"),
                F.round(F.col("jlh_scaled"), 2).alias("jlh_scaled"),
                F.round(F.col("distance"), 2).alias("distance"),
                F.round(F.col("psi"), 2).alias("psi"),
                "psi_category",
            ),
            how="left",
            on="id",
        )
        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        if self.run_logistic_regression:
            print("Running WoE transformation + univariate regression")
            start_time = time.time()
            qi_reg_results_df = self._perform_univariate_logistic_regression(
                df=df,
                vars_list=self.relevant_vars,
                regression_estimator=self.regression_estimator,
                keep_missings=True,
            )

            qi_results_df = qi_results_df.join(
                qi_reg_results_df.select(
                    "id",
                    F.round(F.col("area_under_roc"), 2).alias("area_under_roc"),
                    F.round(F.col("gini"), 2).alias("gini"),
                    F.round(F.col("r2"), 2).alias("r2"),
                ),
                how="left",
                on="id",
            )
            end_time = time.time()
            print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        # run analysis without missing values
        if self.run_analysis_without_missings:
            # intialize output
            qi_results_without_missings_df = df_var_info.select(
                "id",
                F.round("missing_rate_all", 2).alias("missing_rate_all"),
                F.round("share_most_common_all", 2).alias("share_most_common_all"),
                F.round("share_most_common_without_missings_all", 2).alias(
                    "share_most_common_without_missings_all"
                ),
                "var_type",
                "variable_status",
                "variable_status_details",
            )

            print("Runnning basic tests (distance, JLH, PSI) - without missings")
            start_time = time.time()
            qi_test_results_without_missings_df = self._analyse_categorical_vars(
                df=df, vars_list=self.relevant_vars, keep_missings=False
            )

            qi_results_without_missings_df = qi_results_without_missings_df.join(
                qi_test_results_without_missings_df.select(
                    "id",
                    F.round(F.col("jlh"), 2).alias("jlh"),
                    F.round(F.col("jlh_scaled"), 2).alias("jlh_scaled"),
                    F.round(F.col("distance"), 2).alias("distance"),
                    F.round(F.col("psi"), 2).alias("psi"),
                    "psi_category",
                ),
                how="left",
                on="id",
            )
            end_time = time.time()
            print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

            if self.run_logistic_regression:

                print(
                    "Running WoE transformation + univariate regression - without missings"
                )
                start_time = time.time()
                qi_reg_results_without_missings_df = (
                    self._perform_univariate_logistic_regression(
                        df=df,
                        vars_list=self.relevant_vars,
                        regression_estimator=self.regression_estimator,
                        keep_missings=False,
                    )
                )

                qi_results_without_missings_df = qi_results_without_missings_df.join(
                    qi_reg_results_without_missings_df.select(
                        "id",
                        F.round(F.col("area_under_roc"), 2).alias("area_under_roc"),
                        F.round(F.col("gini"), 2).alias("gini"),
                        F.round(F.col("r2"), 2).alias("r2"),
                    ),
                    how="left",
                    on="id",
                )
                end_time = time.time()
                print(
                    f"{'':<2} code execution: {round(end_time - start_time, 1)}s.",
                    "\n",
                )
        else:
            qi_results_without_missings_df = self.spark.createDataFrame(
                [], schema=qi_results_df.schema
            )

        # summary of binning
        print("Preparing binning overview")
        start_time = time.time()
        binning_overview_long, binning_overview_wide = self._prepare_binning_overview(
            df=df,
            vars_list=self.relevant_vars,
            keep_missings=True,
        )

        if self.run_analysis_without_missings:
            _, binning_overview_wide_without_missings = self._prepare_binning_overview(
                df=df,
                vars_list=self.relevant_vars,
                keep_missings=False,
            )
        else:
            binning_overview_wide_without_missings = self.spark.createDataFrame(
                [], schema=binning_overview_wide.schema
            )

        # order output tables
        (
            qi_results_df,
            qi_results_without_missings_df,
            binning_overview_wide,
            binning_overview_wide_without_missings,
            binning_overview_long,
        ) = self._order_results_by_psi(
            qi_results_df=qi_results_df,
            qi_results_without_missings_df=qi_results_without_missings_df,
            binning_overview_wide=binning_overview_wide,
            binning_overview_wide_without_missings=binning_overview_wide_without_missings,
            binning_overview_long=binning_overview_long,
        )

        # save outputs
        if self.save_binning_overview:
            print(
                f"Saving binning overview into tables: '{self.binning_overview_long_table_name}' and '{self.binning_overview_wide_table_name}'"
            )
            binning_overview_long.write.mode("overwrite").option(
                "overwriteSchema", "true"
            ).saveAsTable(self.binning_overview_long_table_name)

            binning_overview_wide.write.mode("overwrite").option(
                "overwriteSchema", "true"
            ).saveAsTable(self.binning_overview_wide_table_name)

            if self.run_analysis_without_missings:
                print(
                    f"Saving binning overview (with missing values excluded) into table: '{f'{self.binning_overview_wide_table_name}_without_missings'}'"
                )
                binning_overview_wide_without_missings.write.mode("overwrite").option(
                    "overwriteSchema", "true"
                ).saveAsTable(
                    f"{self.binning_overview_wide_table_name}_without_missings"
                )

        end_time = time.time()
        print(f"{'':<2} code execution: {round(end_time - start_time, 1)}s.", "\n")

        if self.save_qi_results:
            qi_results_df.write.mode("overwrite").option(
                "overwriteSchema", "true"
            ).saveAsTable(self.qi_results_table_name)

            if self.run_analysis_without_missings:
                qi_results_without_missings_df.write.mode("overwrite").option(
                    "overwriteSchema", "true"
                ).saveAsTable(f"{self.qi_results_table_name}_without_missings")

        return {
            "features analysis": qi_results_df,
            "features analysis missings excluded": qi_results_without_missings_df.drop("order_psi"),
            "binning overview input": binning_overview_wide,
            "binning overview input missings excluded": binning_overview_wide_without_missings,
            "binning plots input": binning_overview_long,
        }
