from pyspark.sql import SparkSession

from odapqi.api.classes.qi_api_preprocessing import QiApiSample, QiApiPreprocess
from odapqi.api.classes.qi_api import QiApi
from odapqi.api.qi_helpers import _process_results_features_selection


class QiFeaturesSelection:
    """Class that can be used for features selection usecase (Quick Insights)

    This can be used to select relevant feature for given binary model.
    - analysed sample is splitted into two subsamples - OBS (target = 1) vs. BASE (target = 0)
    - differences between these samples are analysed for individual variables/features

    The following steps are performed:
    - sampling (optional) - provided feature store can be sampled down
    - pre-processing (optional) - (sampled) feature store is pre-processed (or already pre-processed sample is loaded):
        - gather information about features to identify the problematic features
        - missings treatment
        - binning of numerical features
        - reduce number of categories for categorical features
    - Quick Insights:
        - (optional) missing rate analysis (missings share per samples)
        - basic tests:
            - JLH
            - distance
            - PSI
        - univariate logistic regression

    Remark: by problematic features we mean features with high missing rate or very low/high share of the most dominant value.
    Remark: for feature selection it makes sense to specify analyse_all_feature = False as it makes sense to analyse only features that can be used in model.

    """

    def __init__(
        self,
        obs_cond: str,
        base_cond: str = None,
        feature_store: str = None,
        feature_store_sampled: str = None,
        feature_store_processed: str = None,
        feature_store_stats: str = None,
        perform_sampling: bool = False,
        perform_preprocessing: bool = False,
        features_list: list = None,
        features_to_exclude_list: list = None,
        sample_rate: float = 0.1,
        run_missings_rate: bool = False,
        run_logistic_regression: bool = False,
        run_analysis_without_missings: bool = False,
        save_qi_results: bool = False,
        qi_results_table_name: str = None,
        save_binning_overview: bool = False,
        binning_overview_table_name: str = None,
        regression_estimator: str = "spark",
        analyse_all_features: bool = False,
    ):
        """

        Args:
            obs_cond (str): condition to define OBS sample
            base_cond (str, optional): condition to define BASE sample (if not selected that all rows not fullfiling obs_cond are considered). Defaults to None.
            feature_store (str, optional): name of feature store table. Defaults to None.
            feature_store_sampled (str, optional): name of sampled feature store table. Defaults to None.
            feature_store_processed (str, optional): name of processed feature store table. Defaults to None.
            feature_store_stats (str, optional): name of table with summary of features Defaults to None.
            perform_sampling (bool, optional): flag, whether to perform sampling. Defaults to False.
            perform_preprocessing (bool, optional): flag, whether to perform preprocessing. Defaults to False.
            features_list (list, optional): list of features to consider (if not specified all features considered). Defaults to None.
            sample_rate (float, optional): sampling rate. Defaults to 0.1.
            run_missings_rate (bool, optional): flag whetehr to run missing rate analysis. Defaults to False.
            run_logistic_regression (bool, optional): flag whether to run logistic regression analysis. Defaults to False.
            run_analysis_without_missings (bool, optional): flag whether to perform analysis without missing values. Defaults to False.
            save_qi_results (bool, optional): flag whether to save QI results. Defaults to False.
            qi_results_table_name (str, optional): name of output table with QI results. Defaults to None.
            save_binning_overview (bool, optional): flag whether to save binning overview. Defaults to False.
            binning_overview_table_name (str, optional): name of table with binning overview. Defaults to None.
            regression_estimator (str, optional): method to estimate logistic regression: spark vs sklearn. Defaults to "spark".
            analyse_all_features (bool, optional): flag whether to analyse all features (or to process only not-problematic ones). Defaults to False.
        """
        self.spark = SparkSession.builder.getOrCreate()

        self.feature_store = feature_store
        self.feature_store_sampled = feature_store_sampled
        self.feature_store_processed = feature_store_processed
        self.feature_store_stats = feature_store_stats
        self.perform_sampling = perform_sampling
        self.perform_preprocessing = perform_preprocessing
        self.obs_cond = obs_cond
        self.base_cond = base_cond
        self.features_list = features_list
        self.features_to_exclude_list = features_to_exclude_list
        self.sample_rate = sample_rate
        self.run_missings_rate = run_missings_rate
        self.run_logistic_regression = run_logistic_regression
        self.run_analysis_without_missings = run_analysis_without_missings
        self.save_qi_results = save_qi_results
        self.qi_results_table_name = qi_results_table_name
        self.save_binning_overview = save_binning_overview
        self.binning_overview_table_name = binning_overview_table_name
        self.regression_estimator = regression_estimator
        self.analyse_all_features = analyse_all_features

        self.analysis_mode = "FEATURES_SELECTION"
        self.base_name = "BASE"
        self.obs_name = "TARGET"
        self.sampling_method = "basic"

        # validate inputs
        if self.perform_sampling is True and self.perform_preprocessing is False:
            print(
                """Warning: you specify that sampling should be permorned why preprocessing shouldn't be permormed.
                Sampling is performed prior preprocessing and preprocessing cannot be skipped in this case.
                Hence, paremeter perform_sampling was adjusted to False.
                """
            )
            self.perform_sampling = False

        if self.perform_sampling is True and (
            self.feature_store is None or feature_store_sampled is None
        ):
            raise ValueError(
                """Sampling cannot be performed when name of input table (i.e. 'feature_store' parameter) or name of output table ('feature_store_sampled') are not provided.
                Please note that when you want to perform sampling you need to specify also following parameters (as also preprocessing would be performed):
                - perform_preprocessing=True
                - feature_store=[name of input feature store table]
                - feature_store_sampled=[name of output table, sampled feature store]
                - feature_store_processed=[name of output table, preprocessed feature store]
                - feature_store_stats=[name of output table, stats for individual features]
                """
            )

        if self.perform_preprocessing is True and self.feature_store_sampled is None:
            raise ValueError(
                """Pre-processing cannot be performed when name of input (i.e. 'feature_store_sampled' parameter) is not provided.
                Please note, that parameter 'feature_store_sampled' can reference to full feature store or sampled feature store."""
            )

        if self.perform_preprocessing is False and (
            self.feature_store_processed is None or self.feature_store_stats is None
        ):
            raise ValueError(
                """If it's specified that pre-processing shouldn't be performed, then input parameters 'feature_store_processed' and 'feature_store_stats' should be specified.
                When you want to skip preprocessing (i.e. use already preproccesed feature store) you need to specify:
                - perform_preprocessing=False
                - feature_store_processed=[name of input table, pre-processed feature store]
                - feature_store_stats=[name of input table, stats for individual features]
                Alternatively you can perfrom preprocessing by specifying:

                Please note that you can specify name of properocessed feature store via parameter feature_store_processed together via parameter feature_store_stats (information about features, saved when preprocessing was performed) or
                You need to provide un-processed feature store name as input (feature_store_sampled) and change perform_preprocessing to True.
                Additonality, together with pre-processing you can perform sampling as an optional step (by specifying perform_sampling=True and feature_store parameters).
                """
            )

    def _set_condition_feature_selection(self) -> None:
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

    def _runner(self) -> dict:
        """Runner helper for features selection QI usecase

        Returns:
            dict: QI results
        """

        if self.perform_sampling:
            # perform preprocessing
            qi_sample = QiApiSample(
                spark=self.spark,
                features_table_full=self.feature_store,
                features_table_sampled=self.feature_store_sampled,
                main_filter_condition=self.total_cond,
                method=self.sampling_method,
                sample_rate=self.sample_rate,
            )

            # save relevant subsample - apply condition and sampling
            qi_sample.save_sample()

        if self.perform_preprocessing:
            # pre-processing
            qi_preprocess = QiApiPreprocess(
                spark=self.spark,
                features_store_sampled=self.feature_store_sampled,
                features_store_processed=self.feature_store_processed,
                stats_output_table_name=self.feature_store_stats,
                main_filter_condition=self.total_cond,
                features_list=self.features_list,
                analyse_all_features=self.analyse_all_features,
            )
            qi_preprocess.get_preprocessed_table()

        # run QI
        qi_api = QiApi(
            spark=self.spark,
            features_table_processed=self.feature_store_processed,
            feature_store_stats=self.feature_store_stats,
            obs_cond=self.obs_cond,
            base_cond=self.base_cond,
            features_list=self.features_list,
            features_to_exclude_list=self.features_to_exclude_list,
            run_missings_rate=self.run_missings_rate,
            run_logistic_regression=self.run_logistic_regression,
            run_analysis_without_missings=self.run_analysis_without_missings,
            save_qi_results=self.save_qi_results,
            qi_results_table_name=self.qi_results_table_name,
            save_binning_overview=self.save_binning_overview,
            binning_overview_table_name=self.binning_overview_table_name,
            regression_estimator=self.regression_estimator,
            analysis_mode=self.analysis_mode,
            base_name=self.base_name,
            obs_name=self.obs_name,
        )

        return qi_api.get_qi()

    def runner(self) -> dict:
        """Runner for features selection QI usecase

        Returns:
            dict: QI results
        """
        self._set_condition_feature_selection()

        qi_res = self._runner()

        return _process_results_features_selection(qi_res)


class QiFeaturesMonitoring(QiFeaturesSelection):
    """Class that can be used for features monitoring usecase (Quick Insights)

    This can be used to monitor feature store between two snapshots.

    The following steps are performed:
    - sampling (optional) - provided feature store can be sampled down
    - pre-processing (optional) - (sampled) feature store is pre-processed (or already pre-processed sample is loaded):
        - gather information about features to identify the problematic features
        - missings treatment
        - binning of numerical features
        - reduce number of categories for categorical features
    - Quick Insights:
        - (optional) missing rate analysis (missings share per samples)
        - basic tests:
            - JLH
            - distance
            - PSI
        - univariate logistic regression

    Remark: by problematic features we mean features with high missing rate or very low/high share of the most dominant value.
    Remark: for feature selection it makes sense to specify analyse_all_feature = True as it makes sense to monitor all features (and not only non-problematic ones).

    """

    def __init__(
        self,
        date_column: str,
        obs_date: str,
        base_date: str,
        feature_store: str = None,
        feature_store_sampled: str = None,
        feature_store_processed: str = None,
        feature_store_stats: str = None,
        perform_sampling: bool = False,
        perform_preprocessing: bool = False,
        features_list: list = None,
        features_to_exclude_list: list = None,
        sample_rate: float = 0.1,
        run_missings_rate: bool = True,
        run_logistic_regression: bool = False,
        run_analysis_without_missings: bool = False,
        save_qi_results: bool = False,
        qi_results_table_name: str = None,
        save_binning_overview: bool = False,
        binning_overview_table_name: str = None,
        regression_estimator: str = "spark",
        analyse_all_features: bool = True,
    ):
        """

        Args:
            date_column (str): snapshot/date column
            obs_date (str): date defining OBS sample
            base_date (str): date defining BASE sample
            feature_store (str, optional): name of feature store table. Defaults to None.
            feature_store_sampled (str, optional): name of sampled feature store table. Defaults to None.
            feature_store_processed (str, optional): name of processed feature store table. Defaults to None.
            feature_store_stats (str, optional): name of table with summary of features Defaults to None.
            perform_sampling (bool, optional): flag, whether to perform sampling. Defaults to False.
            perform_preprocessing (bool, optional): flag, whether to perform preprocessing. Defaults to False.
            features_list (list, optional): list of features to consider (if not specified all features considered). Defaults to None.
            sample_rate (float, optional): sampling rate. Defaults to 0.1.
            run_missings_rate (bool, optional): flag whether to run missing rate analysis. Defaults to True.
            run_logistic_regression (bool, optional): flag whether to run logistic regression analysis. Defaults to False.
            run_analysis_without_missings (bool, optional): flag whether to perform analysis without missing values. Defaults to False.
            save_qi_results (bool, optional): flag whether to save QI results. Defaults to False.
            qi_results_table_name (str, optional): name of output table with QI results. Defaults to None.
            save_binning_overview (bool, optional): flag whether to save binning overview. Defaults to False.
            binning_overview_table_name (str, optional): name of table with binning overview. Defaults to None.
            regression_estimator (str, optional): method to estimate logistic regression: spark vs sklearn. Defaults to "spark".
            analyse_all_features (bool, optional): flag whether to analyse all features (or to process only not-problematic ones). Defaults to True.
        """
        super().__init__(
            obs_cond="",
            base_cond="",
            feature_store=feature_store,
            feature_store_sampled=feature_store_sampled,
            feature_store_processed=feature_store_processed,
            feature_store_stats=feature_store_stats,
            perform_sampling=perform_sampling,
            perform_preprocessing=perform_preprocessing,
            features_list=features_list,
            features_to_exclude_list=features_to_exclude_list,
            sample_rate=sample_rate,
            run_missings_rate=run_missings_rate,
            run_logistic_regression=run_logistic_regression,
            run_analysis_without_missings=run_analysis_without_missings,
            save_qi_results=save_qi_results,
            qi_results_table_name=qi_results_table_name,
            save_binning_overview=save_binning_overview,
            binning_overview_table_name=binning_overview_table_name,
            regression_estimator=regression_estimator,
            analyse_all_features=analyse_all_features,
        )

        self.date_column = date_column
        self.base_name = base_date
        self.obs_name = obs_date
        self.base_date = base_date
        self.obs_date = obs_date
        self.analysis_mode = "FEATURES_MONITORING"
        self.sampling_method = "dates"

    def _set_conditions_features_monitoring(self) -> None:
        """Process base and obs condition and define condition for whole sample (i.e. OBS + BASE)
        Provide dates (base_date and obs_date) are converted into logical SQL condition.

        """
        self.base_cond = f"({self.date_column} == '{self.base_date}')"
        self.obs_cond = f"({self.date_column} == '{self.obs_date}')"

        self.total_cond = " OR ".join(
            [cond for cond in [self.base_cond, self.obs_cond] if cond]
        )

    def runner(self) -> dict:
        """Runner for features monitoring QI usecase

        Returns:
            dict: QI results
        """

        self._set_conditions_features_monitoring()

        qi_res = self._runner()

        return qi_res
