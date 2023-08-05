import textwrap
import math
from math import log10, floor
from typing import List, Dict
from pyspark.sql import functions as F, types as T, DataFrame, Column, SparkSession
from pyspark.sql.window import Window
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class CategoricalBinsReducer:
    """Class performing reduction of number of categories/bins for categorical features."""

    def reduce(self, df: DataFrame, columns: List[str], bin_params: dict) -> DataFrame:
        threshold = 1 - bin_params["reduction_percentage"]

        for col in columns:
            category_counts, n_categories = self.__get_categories_counts(
                df, col, bin_params
            )

            category_counts = category_counts.withColumn(
                "cat_status",
                F.when(
                    (
                        (F.col("rank") > bin_params["cat_var_max_bins"])
                        | (
                            (F.col("rank") > bin_params["cat_var_min_bins"])
                            & (F.col("rank") <= bin_params["cat_var_max_bins"])
                            & (
                                (F.col("cumm_share") >= threshold)
                                | (
                                    F.col("share")
                                    <= bin_params["cat_var_min_bin_share"]
                                )
                            )
                        )
                    )
                    & (F.col(col) != "__missing__"),
                    F.lit("concat"),
                ).otherwise(F.lit("keep")),
            )

            categories_to_keep = [
                row[col]
                for row in category_counts.filter(F.col("cat_status") == "keep")
                .select(col)
                .collect()
            ]

            if n_categories - len(categories_to_keep) > 1:
                df = df.withColumn(
                    col,
                    F.when(
                        (F.col(col).isin(categories_to_keep)) | (F.col(col).isNull()),
                        F.col(col),
                    ).otherwise(F.lit("__other__")),
                )

        return df

    def __get_categories_counts(
        self, df: DataFrame, col: str, bin_params: dict
    ) -> list:
        window_spec = Window.partitionBy().orderBy(F.desc(F.col("count")))

        df_counts = (
            df.select(col)
            .filter((F.col(col) != "__missing__") & (F.col(col).isNotNull()))
            .groupBy(col)
            .count()
            .orderBy(F.desc("count"))
        )
        n_total = df_counts.select(F.sum("count")).collect()[0][0]
        n_categories = df_counts.count()

        df_counts = (
            df_counts.limit(
                bin_params["cat_var_max_bins"]
            )  # to speed up calculation as only limited number of bins would be kept
            .withColumn("cumm_count", F.sum("count").over(window_spec))
            .withColumn("cumm_share", F.col("cumm_count") / F.lit(n_total))
            .withColumn("share", F.col("count") / F.lit(n_total))
            .withColumn("rank", F.rank().over(window_spec))
            .withColumn("cumm_share", F.col("cumm_share") - F.col("share"))
        )

        return df_counts, n_categories


class FloatingPointBinsGenerator:
    """Binning of float/double features."""

    def generate(
        self, df: DataFrame, bin_params: dict, vars_list: list = None
    ) -> DataFrame:
        columns = [
            column for column, dtype in df.dtypes if dtype in ("float", "double")
        ]

        if vars_list:
            columns = [column for column in columns if column in vars_list]

        return df.select(
            *(
                self.__count_percentile(
                    col,
                    bin_params["higher_percentile_percentage"],
                    bin_params["accuracy"],
                ).alias(f"{col}_quantile")
                for col in columns
            ),
            *(F.max(col).alias(f"{col}_max") for col in columns),
        ).select(
            *(
                self.__make_bin_array(col, bin_params["bin_count"]).alias(col)
                for col in columns
            )
        )

    def __count_percentile(
        self, col: str, percentile_percentage: float, accuracy: int
    ) -> Column:
        return F.percentile_approx(
            F.when(F.col(col) > 0, F.col(col)), percentile_percentage, accuracy
        )

    def __round_bin(self, col: str, current_bin: int, bin_count: int) -> Column:
        return current_bin * F.col(f"{col}_quantile") / (bin_count - 1)

    def __make_bin_array(self, col: str, bin_count: int) -> Column:
        return F.array_distinct(
            F.array(
                *(
                    self.__round_bin(col, i, bin_count - 1)
                    for i in range(bin_count - 1)
                ),
                F.col(f"{col}_max"),
            )
        )


class IntegralBinsGenerator:
    """Binning of integer features."""

    def generate(
        self, df: DataFrame, bin_params: dict, vars_list: list = None
    ) -> DataFrame:
        columns = [
            column
            for column, dtype in df.dtypes
            if dtype in ("tinyint", "smallint", "int", "bigint")
        ]

        if vars_list:
            columns = [column for column in columns if column in vars_list]

        low_quantiles = self.__get_low_quantiles(
            df,
            columns,
            bin_params["lower_percentile_percentage"],
            bin_params["accuracy"],
        )
        high_quantiles = self.__get_high_quantiles(
            df,
            columns,
            bin_params["higher_percentile_percentage"],
            bin_params["accuracy"],
            low_quantiles,
        )

        return (
            df.select(*(self.__get_distinct_bins(col).alias(col) for col in columns))
            .select(
                *(
                    self.__remove_quantiles_if_bin_count_exceeds_threshold(
                        col,
                        bin_params["bin_count"],
                        low_quantiles[col],
                        high_quantiles[col],
                    ).alias(col)
                    for col in columns
                )
            )
            .select(
                *(
                    self.__generate_linear_bins_if_bin_count_exceeds_threshold(
                        col,
                        bin_params["bin_count"],
                        low_quantiles[col],
                        high_quantiles[col],
                    ).alias(col)
                    for col in columns
                )
            )
        )

    def __get_distinct_bins(self, col: str) -> Column:
        return F.collect_set(col)

    def __remove_quantiles_if_bin_count_exceeds_threshold(
        self, col: str, bin_count: int, low_quantile: int, high_quantile: int
    ) -> Column:
        return F.when(F.size(col) <= bin_count, F.col(col)).otherwise(
            F.filter(F.col(col), lambda x: x.between(low_quantile, high_quantile))
        )

    def __generate_linear_bins_if_bin_count_exceeds_threshold(
        self, col: str, bin_count: int, low_quantile: int, high_quantile: int
    ) -> Column:
        linear_bins = (
            sorted(np.round(np.linspace(low_quantile, high_quantile, bin_count)))
            if not any([low_quantile is None, high_quantile is None])
            else []
        )

        return F.when(F.size(col) <= bin_count, F.array_sort(F.col(col))).otherwise(
            F.array(*map(F.lit, linear_bins))
        )

    def __get_low_quantiles(
        self,
        df: DataFrame,
        columns: List[str],
        lower_percentile_percentage: float,
        accuracy: int,
    ) -> Dict:
        low_quantiles = (
            df.select(
                *[
                    F.percentile_approx(
                        F.col(col), lower_percentile_percentage, accuracy
                    ).alias(col)
                    for col in columns
                ]
            )
            .collect()[0]
            .asDict()
        )

        return low_quantiles

    def __get_high_quantiles(
        self,
        df: DataFrame,
        columns: List[str],
        higher_percentile_percentage: float,
        accuracy: int,
        low_quantiles: Dict,
    ) -> Dict:
        high_quantiles = (
            df.select(
                *[
                    (
                        F.percentile_approx(
                            F.when(F.col(col) > low_quantiles[col], F.col(col)),
                            higher_percentile_percentage,
                            accuracy,
                        )
                        + 1
                    ).alias(col)
                    for col in columns
                ]
            )
            .collect()[0]
            .asDict()
        )

        return high_quantiles


def _transpose_df(df: DataFrame, header_col="summary") -> DataFrame:
    """Helper to transpose df

    Args:
        df (DataFrame): considered sample
        header_col (str, optional): column to pivot (transpose) by table. Defaults to "summary".

    Returns:
        DataFrame: transposed table
    """
    cols_minus_header = df.columns
    cols_minus_header.remove(header_col)

    df = (
        df.groupBy()
        .pivot(header_col)
        .agg(F.first(F.array(cols_minus_header)))
        .withColumn(header_col, F.array(*map(F.lit, cols_minus_header)))
    )

    return df.select(F.arrays_zip(*df.columns).alias("az")).selectExpr("inline(az)")


def _get_numerical_stats(
    df: DataFrame,
    numerical_vars: list,
    binary_vars: list,
) -> DataFrame:
    """Calculating summary statistics for numerical variables

    Args:
        df (DataFrame): considered table
        numerical_vars (list): list of numerical variables to consider
        binary_vars (list): list of binary variables to consider

    Returns:
        DataFrame: table with summary statistics of numerical features.
    """
    avgs_spec = [F.avg(col).alias(col) for col in numerical_vars] + [
        F.avg(F.col(col).cast("double")).alias(col) for col in binary_vars
    ]
    mins_spec = [F.min(col).alias(col) for col in numerical_vars] + [
        F.min(F.col(col).cast("double")).alias(col) for col in binary_vars
    ]
    maxs_spec = [F.max(col).alias(col) for col in numerical_vars] + [
        F.max(F.col(col).cast("double")).alias(col) for col in binary_vars
    ]

    df_numeric = (
        df.select(F.lit("mean").alias("summary"), *avgs_spec)
        .unionByName(df.select(F.lit("min").alias("summary"), *mins_spec))
        .unionByName(df.select(F.lit("max").alias("summary"), *maxs_spec))
    )

    df_numeric = _transpose_df(df=df_numeric)

    return df_numeric


def _get_missing_rate(
    df: DataFrame,
    vars_list: list,
) -> DataFrame:
    """Calculate missing rate

    Args:
        df (DataFrame): considered sample
        vars_list (list): list of features to consider

    Returns:
        DataFrame: table with summary of missing rate
    """
    n_obs_sample = df.groupBy().count().collect()[0][0]
    counts_spec = [F.count(col).alias(col) for col in vars_list]

    df_counts = df.select(F.lit("count").alias("summary"), *counts_spec)

    df_counts = _transpose_df(df=df_counts)

    df_counts = df_counts.withColumn("n", F.lit(n_obs_sample)).withColumn(
        "missing_rate", ((F.col("n") - F.col("count")) / F.col("n"))
    )

    return df_counts


def _get_count_distinct(
    df: DataFrame,
    vars_list: list,
) -> DataFrame:
    """calculate number of distinct values for features

    Args:
        df (DataFrame): considered sample
        vars_list (list): list of features to consider

    Returns:
        DataFrame: summary with number of distinct values per individual features
    """

    counts_distinct_spec = [
        F.approx_count_distinct(F.col(c)).alias(c) for c in vars_list
    ]

    df_counts_distinct = df.select(
        F.lit("n_distinct").alias("summary"), *counts_distinct_spec
    )

    df_counts_distinct = _transpose_df(df=df_counts_distinct)

    return df_counts_distinct


def _get_info_per_sample(
    df: DataFrame,
    numerical_vars: list,
    categorical_vars: list,
    binary_vars: list,
    spark: SparkSession,
    suffix: str = "all",
) -> DataFrame:
    """Prepare summary of features/variables for given sample

    Args:
        df (DataFrame): analysed sample
        numerical_vars (list): list of numerical variables
        categorical_vars (list): list of categorical variables
        binary_vars (list): list of binary variables
        spark (SparkSession): spark session
        suffix (str, optional): suffix to be add to the name of output columns. Defaults to "all".

    Returns:
        DataFrame: df with basic information about individual features/variables
    """

    schema_numeric = T.StructType(
        [
            T.StructField("summary", T.StringType(), True),
            T.StructField("min", T.DoubleType(), True),
            T.StructField("max", T.DoubleType(), True),
            T.StructField("mean", T.DoubleType(), True),
        ]
    )

    all_vars = numerical_vars + categorical_vars + binary_vars

    # statistic for numerical columns
    if len(numerical_vars + binary_vars) > 0:
        df_numeric = _get_numerical_stats(
            df=df,
            numerical_vars=numerical_vars,
            binary_vars=binary_vars,
        )

    else:
        df_numeric = spark.createDataFrame([], schema_numeric)

    # missings and most common values
    df_counts = _get_missing_rate(df=df, vars_list=all_vars)
    df_counts_distinct = _get_count_distinct(df=df, vars_list=all_vars)

    df_out = (
        df_counts.join(df_counts_distinct, on="summary", how="left")
        .join(df_numeric, on="summary", how="left")
        .select(
            F.col("summary").alias("id"),
            F.col("count").alias(f"n_not_missing_{suffix}"),
            F.col("n").alias(f"n_{suffix}"),
            F.col("missing_rate").alias(f"missing_rate_{suffix}"),
            F.col("n_distinct").alias(f"n_distinct_{suffix}"),
            F.col("min").alias(f"min_{suffix}"),
            F.col("max").alias(f"max_{suffix}"),
            F.col("mean").alias(f"avg_{suffix}"),
        )
    )

    return df_out


def _get_n_of_most_common(
    df: DataFrame, vars_list: list, spark: SparkSession, suffix: str = "all"
) -> DataFrame:
    """Helper to calculate occurence of most common value in the column

    Args:
        df (DataFrame): sample to be analysed
        vars_list (list): list of variables/features
        spark (SparkSession): spark session
        suffix (str, optional): suffix to be add to the name of output columns. Defaults to "all".

    Returns:
        DataFrame: df with occurence of most common value for give features.
    """
    res_list = []

    for var in vars_list:
        dist_var = df.groupBy(var).count().orderBy(F.desc("count"))

        n_most_common = dist_var.head()["count"]
        try:
            n_most_common_without_missings = dist_var.filter(
                F.col(var).isNotNull()
            ).head()["count"]
        except:
            n_most_common_without_missings = 0

        res_list.append(
            {
                "id": var,
                f"n_most_common_{suffix}": n_most_common,
                f"n_most_common_without_missings_{suffix}": n_most_common_without_missings,
            }
        )

    schema_most_common = T.StructType(
        [
            T.StructField("id", T.StringType(), True),
            T.StructField(f"n_most_common_{suffix}", T.IntegerType(), True),
            T.StructField(
                f"n_most_common_without_missings_{suffix}", T.IntegerType(), True
            ),
        ]
    )

    return spark.createDataFrame(res_list, schema=schema_most_common)


def _get_contigency_tables(
    df: DataFrame, vars_list: list, keep_missings: bool = True
) -> dict:
    """Helper to create contingency table for categorical variables (sample vs. category)

    Args:
        df (DataFrame): sample to be analysed
        vars_list (list): list of variables/features
        keep_missings (bool, optional): Flag whether to keep missings (__missing__) in the sample. Defaults to True.

    Returns:
        dict: dictionary with calculated contingency tables
    """
    cont_tables = {}

    for var in vars_list:
        if keep_missings:
            res = (
                df
                .crosstab(var, "SAMPLE_NAME")
            )
        else:
            res = (
                df.filter((F.col(var).isNotNull()) & (F.col(var) != "__missing__"))
                .crosstab(var, "SAMPLE_NAME")
            )

        # check that both samples are available
        if "BASE" not in res.columns:
            res = res.withColumn("BASE", F.lit(0))
        if "OBS" not in res.columns:
            res = res.withColumn("OBS", F.lit(0))

        res = (
            res
            .select("BASE", "OBS")
            .fillna(0)
            .collect()
        )

        # assign only non-empty
        if res:
            cont_tables[var] = [item.asDict() for item in res]
        else:
            print(f'Contingency table is empty for feature: {var}')

    return cont_tables


def _wrap_labels(ax, width):
    """Helper to wrap lables of the plot"""
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        if text in ["__missing__", "__other__"]:
            labels.append(text)
        else:
            labels.append(textwrap.fill(text, width=width, break_long_words=True))

    ax.set_xticklabels(labels, rotation=0, fontsize=9)


def print_binning_overview(binning_overview_wide: DataFrame, vars_list: list = None):
    """Runner to print tables with overview of binning"""
    if vars_list:
        if isinstance(vars_list, str):
            vars_list = [vars_list]

        binning_overview_wide = binning_overview_wide.filter(
            F.col("feature").isin(vars_list)
        )

    vars_list = [
        row["feature"]
        for row in binning_overview_wide.select("feature", "order_psi").distinct().orderBy("order_psi").collect()
    ]

    # remove underscores from column names
    binning_overview_wide = binning_overview_wide.select(
        [
            F.col(col).alias(col.replace("_", " "))
            for col in binning_overview_wide.columns
        ]
    )

    for var in vars_list:
        print(var)
        binning_overview_wide.filter(F.col("feature") == var).drop("feature", "order psi").display()


def figures_binning_overview(
    binning_overview_long: DataFrame, vars_list: list = None, keep_missings: bool = True
):
    """Runner to prepare plots comparing bining on BASE and OBS sample"""
    if vars_list:
        if isinstance(vars_list, str):
            vars_list = [vars_list]

        binning_overview_long = binning_overview_long.filter(
            F.col("feature").isin(vars_list)
        )

    vars_list = [
        row["feature"]
        for row in binning_overview_long.select("feature", "order_psi").distinct().orderBy("order_psi").collect()
    ]

    if keep_missings is False:
        binning_overview_long = binning_overview_long.filter(
            (F.col("Bin") != "__missing__") & F.col("Bin").isNotNull()
        )

    # remove underscores from column names
    binning_overview_long = binning_overview_long.select(
        [
            F.col(col).alias(col.replace("_", " "))
            for col in binning_overview_long.columns
        ]
    )

    binning_overview_pd = binning_overview_long.toPandas()

    # set plot style: grey grid in the background:
    sns.set(style="darkgrid")

    for var in vars_list:
        var_overview = binning_overview_pd.loc[binning_overview_pd["feature"] == var]
        var_overview = var_overview.rename(columns={"Bin": var})

        if not var_overview.empty:
            # Set the figure size
            _, ax = plt.subplots(figsize=(24, 10))

            sns.barplot(
                x=var, y="Share per sample", hue="Sample name", data=var_overview
            )

            _wrap_labels(ax, 10)

            plt.show()


def print_binning_overview_and_plots(
    qi_results_table_name: str,
    condition_to_select_features: str = None,
    binning_overview_wide_table_name: str = None,
    binning_overview_long_table_name: str = None,
    keep_missings: bool = True,
) -> None:
    """Runer to print both binning overview and binning plots from saved result tables.

    It is possible to specify condition (condition_to_select_features) that would determine for which features should be results displayed.

    Args:
        qi_results_table_name (str): table name of table with QI results
        condition_to_select_features (str, optional): optional condition to select features based on QI results. Defaults to None.
        binning_overview_wide_table_name (str, optional): name of saved binning overview (wide format) table. Defaults to None.
        binning_overview_long_table_name (str, optional): name of saved binning overview (long format) table. Defaults to None.
    """

    spark = SparkSession.builder.getOrCreate()

    # load feature store stats
    df_qi_results = spark.read.table(qi_results_table_name)

    if condition_to_select_features:
        df_qi_results = df_qi_results.filter(F.expr(condition_to_select_features))

    # list of relevant features
    vars_list = [row["id"] for row in df_qi_results.select("id").collect()]

    if len(vars_list) > 0:
        if binning_overview_long_table_name:
            print("Binning plots:")
            binning_overview_long = spark.read.table(binning_overview_long_table_name)
            figures_binning_overview(
                binning_overview_long=binning_overview_long, vars_list=vars_list, keep_missings=keep_missings
            )
            print("")

        if binning_overview_wide_table_name:
            print("Binning overview:")
            binning_overview_wide = spark.read.table(binning_overview_wide_table_name)
            print_binning_overview(
                binning_overview_wide=binning_overview_wide, vars_list=vars_list
            )
    else:
        print("No variables selected")


def _round_binning_splits(splits: list, n_significant: int = 2):
    def _round_to_n(x, n):
        if x in [-float("inf"), float("inf")]:
            return x
        elif x == 0:
            return x
        elif abs(x) >= 1 and x == int(x):
            return x
        elif abs(x) >= 1:
            return round(x, 2)
        return round(x, -int(floor(log10(abs(x)))) + (n - 1))

    splits_out = []

    for split in splits:
        splits_out.append(_round_to_n(split, n_significant))

    return splits_out


def _categorise_metric(
    df: DataFrame,
    categories: dict = {
        "Significant change": 0.2,
        "Slight change": 0.1,
        "Not significant": 0.0,
    },
    input_col_name: str = "psi",
    output_col_name: str = "psi_category",
) -> DataFrame:
    for i, (category, threshold) in enumerate(categories.items()):
        if i == 0:
            categories_cond = F.when(
                F.col(input_col_name) >= threshold, F.lit(category)
            )
        else:
            categories_cond = categories_cond.when(
                F.col(input_col_name) >= threshold, F.lit(category)
            )

    return df.withColumn(output_col_name, categories_cond)


def _process_results_features_selection(qi_res: dict) -> dict:
    return {
        "features analysis": qi_res["features analysis"].filter(
            F.col("variable_status") == "ok"
        ),
        "features analysis missings excluded": qi_res[
            "features analysis missings excluded"
        ].filter(F.col("variable_status") == "ok"),
        "problematic features": qi_res["features analysis"].filter(
            F.col("variable_status") != "ok"
        ),
        "binning overview input": qi_res["binning overview input"],
        "binning overview input missings excluded": qi_res["binning overview input missings excluded"],
        "binning plots input": qi_res["binning plots input"],
    }


class WOE_IV:
    # TODO: check whether approach based on _get_contingency_tables would be faster
    # original code: https://github.com/albertusk95/weight-of-evidence-spark
    def __init__(
        self, df: DataFrame, cols_to_woe: list, label_column: str, good_label: str
    ):
        self.df = df
        self.cols_to_woe = cols_to_woe
        self.label_column = label_column
        self.good_label = good_label
        self.fit_data = {}

    def fit(self):
        for col_to_woe in self.cols_to_woe:
            total_good = self.compute_total_amount_of_good()
            total_bad = self.compute_total_amount_of_bad()

            woe_df = self.df.select(col_to_woe)
            categories = woe_df.distinct().collect()
            for category_row in categories:
                category = category_row[col_to_woe]
                good_amount = self.compute_good_amount(col_to_woe, category)
                bad_amount = self.compute_bad_amount(col_to_woe, category)

                good_amount = good_amount if good_amount != 0 else 0.5
                bad_amount = bad_amount if bad_amount != 0 else 0.5

                good_dist = good_amount / total_good
                bad_dist = bad_amount / total_bad

                self.build_fit_data(col_to_woe, category, good_dist, bad_dist)

    def transform(self, df: DataFrame):
        def _encode_woe(col_to_woe_):
            return F.coalesce(
                *[
                    F.when(F.col(col_to_woe_) == category, F.lit(woe_iv["woe"]))
                    for category, woe_iv in self.fit_data[col_to_woe_].items()
                ]
            )

        for col_to_woe, woe_info in self.fit_data.items():
            df = df.withColumn(col_to_woe + "_WOE", _encode_woe(col_to_woe))
        return df

    def compute_total_amount_of_good(self):
        return (
            self.df.select(self.label_column)
            .filter(F.col(self.label_column) == self.good_label)
            .count()
        )

    def compute_total_amount_of_bad(self):
        return (
            self.df.select(self.label_column)
            .filter(F.col(self.label_column) != self.good_label)
            .count()
        )

    def compute_good_amount(self, col_to_woe: str, category: str):
        return (
            self.df.select(col_to_woe, self.label_column)
            .filter(
                (F.col(col_to_woe) == category)
                & (F.col(self.label_column) == self.good_label)
            )
            .count()
        )

    def compute_bad_amount(self, col_to_woe: str, category: str):
        return (
            self.df.select(col_to_woe, self.label_column)
            .filter(
                (F.col(col_to_woe) == category)
                & (F.col(self.label_column) != self.good_label)
            )
            .count()
        )

    def build_fit_data(self, col_to_woe, category, good_dist, bad_dist):
        woe_info = {
            category: {
                "woe": math.log(good_dist / bad_dist),
                "iv": (good_dist - bad_dist) * math.log(good_dist / bad_dist),
            }
        }

        if col_to_woe not in self.fit_data:
            self.fit_data[col_to_woe] = woe_info
        else:
            self.fit_data[col_to_woe].update(woe_info)

    def compute_iv(self):
        iv_dict = {}

        for woe_col, categories in self.fit_data.items():
            iv_dict[woe_col] = 0
            for _, woe_iv in categories.items():
                iv_dict[woe_col] += woe_iv["iv"]
        return iv_dict
