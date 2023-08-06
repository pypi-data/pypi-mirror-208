import scipy
import pytest
import numpy as np
import pandas as pd
from collections import Counter
# from pandas.testing import assert_frame_equal
import statistics

import flyingfish.EDA as EDA


@pytest.fixture
def simple_list() -> list[int]:
    return [1, 2, 3]


@pytest.fixture
def list_with_outlier1() -> list[int]:
    return [-100.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 100.0]


@pytest.fixture
def list_with_outlier2() -> list[int]:
    return [1.0, 2.0, 2.0, 2.0, 3.0, 1.0, 1.0, 15.0, 2.0, 2.0, 2.0, 3.0, 1.0,
            1.0, 2.0]


@pytest.fixture
def list_with_outlier3() -> list[int]:
    return [-15.0, 2.0, 2.0, 2.0, 3.0, 1.0, 1.0, 15.0, 2.0, 2.0, 2.0, 3.0, 1.0,
            1.0, 2.0]


# -------------------------------------------------------------------------
# estimates of location
# -------------------------------------------------------------------------

def test_arithmetic_mean(simple_list) -> None:
    assert 6/3 == EDA.arithmetic_mean(simple_list)


def test_weighted_mean(simple_list) -> None:
    assert 2.0 == EDA.weighted_mean(simple_list, weights=[2, 2, 2])


def test_trimmed_mean() -> None:
    assert 5/2 == EDA.trimmed_mean(data=[1, 2, 3, 4], p=1)


def test_geometric_mean(simple_list) -> None:
    assert 1.8171 == round(EDA.geometric_mean(data=simple_list), 4)


def test_exponential_mean(simple_list) -> None:
    assert 2.1602 == round(EDA.exponential_mean(data=simple_list, m=2), 4)


def test_harmonic_mean(simple_list) -> None:
    assert 1.6364 == round(EDA.harmonic_mean(data=simple_list), 4)


def test_median_even() -> None:
    assert 2.5 == EDA.median(data=[1, 2, 3, 4])


def test_median_odd(simple_list) -> None:
    assert 2.0 == EDA.median(simple_list)


def test_weighted_median_even(simple_list) -> None:
    assert 2.5 == EDA.weighted_median(data=simple_list, weights=[1, 2, 3])


def test_weighted_median_odd(simple_list) -> None:
    assert 3.0 == EDA.weighted_median(data=simple_list, weights=[1, 1, 3])


def test_percentile() -> None:
    test = EDA.percentile(
        data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0], per=50)
    assert 6.0 == test
    assert EDA.median(
        data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]) == test

# -------------------------------------------------------------------------
# estimates of variability
# -------------------------------------------------------------------------


def test_avg_absolute_deviation_mean(simple_list) -> None:
    assert 2/3 == EDA.MAD_mean(data=simple_list)


def test_avg_absolute_deviation_mean_2() -> None:
    assert 0.0 == EDA.MAD_mean(data=[1, 1, 1])


def test_avg_absolute_deviation_median_1() -> None:
    assert 2/3 == EDA.MAD_median(data=[1, 1, 3])


def test_avg_absolute_deviation_median_2() -> None:
    assert 0.0 == EDA.MAD_median(data=[1, 1, 1])


def test_mean_absolute_deviation() -> None:
    assert 1.0 == EDA.MedAD_median(data=[1, 1, 2, 2, 4, 6, 9])


def test_variance_biased(simple_list) -> None:
    assert 2/3 == EDA.variance(data=simple_list, biased=True)


def test_variance_unbiased(simple_list) -> None:
    assert 1/1 == EDA.variance(data=simple_list, biased=False)


def test_stdev_biased(simple_list) -> None:
    assert (2/3)**(1/2) == EDA.stdev(data=simple_list, biased=True)


def test_stdev_unbiased(simple_list) -> None:
    assert 1/1 == round(EDA.stdev(data=simple_list, biased=False), 4)


def test_range(simple_list) -> None:
    assert 2.0 == EDA.range(data=simple_list)


def test_iqr() -> None:
    assert 4.0 == EDA.iqr(data=[1, 2, 3, 3, 5, 6, 7, 9])


def test_mu2(simple_list) -> None:
    assert 2/3 == EDA.mu(data=simple_list, k=2)


def test_mu3(simple_list) -> None:
    assert 0.0 == EDA.mu(data=simple_list, k=3)


def test_mu4(simple_list) -> None:
    assert 2/3 == EDA.mu(data=simple_list, k=4)


def test_coefficient_of_variation(simple_list) -> None:
    assert 0.408 == round(EDA.coefficient_of_variation(simple_list), 3)

# -------------------------------------------------------------------------
# estimates of distribution
# -------------------------------------------------------------------------


def test_skewness_biased() -> None:
    test = round(EDA.coefficient_of_skewness(
        data=[1, 5, 5, 1], biased=True), 4)
    ref = round(scipy.stats.skew([1, 5, 5, 1], bias=True), 4)
    assert test == ref


def test_skewness_unbiased() -> None:
    test = round(EDA.coefficient_of_skewness(
        data=[1, 5, 5, 1], biased=False), 4)
    ref = round(scipy.stats.skew([1, 5, 5, 1], bias=False), 4)
    assert test == ref


def test_kurtosis_biased() -> None:
    test = round(EDA.coefficient_of_kurtosis(
        data=[-10, -5, 0, 5, 10], biased=True), 4)
    ref = round(scipy.stats.kurtosis([-10, -5, 0, 5, 10], bias=True) + 3, 4)
    assert test == ref


def test_mode_single() -> None:
    assert [3] == EDA.mode(data=[1, 3, 3])


def test_mode_multiple(simple_list) -> None:
    assert [1, 2, 3] == EDA.mode(simple_list)


# ----------------------------------------------------------------
# multivariate
# ----------------------------------------------------------------


def test_covariance() -> None:
    assert statistics.covariance([1, 2, 3], [3, 1, 2]) \
            == EDA.covariance([1, 2, 3], [3, 1, 2])


def test_lin_interpol_2D() -> None:
    test = EDA.lin_interpol_2D(x1=-1, x2=1, xi=0, y1=-1, y2=1)
    ref = 0
    assert test == ref


def test_lin_interpol_2D_2() -> None:
    test = EDA.lin_interpol_2D(x1=1, x2=3, xi=2, y1=1, y2=3)
    assert test == 2


def test_bin_2d_feature_mean() -> None:

    test = EDA.bin_2d_feature(
            x_intervals=[(0, 2), (2, 4), (4, 6)],
            y_intervals=[(0, 2), (2, 4)],
            x_data=[1, 1, 5],
            y_data=[1, 1, 3],
            z_data=[1, 9, 1],
            aggregate_fn=np.mean
            )
    ref = np.array([[5, 0, 0], [0, 0, 1]])
    assert (test == ref).all()


def test_bin_2d_feature_sum() -> None:

    test = EDA.bin_2d_feature(
            x_intervals=[(0, 2), (2, 4), (4, 6)],
            y_intervals=[(0, 2), (2, 4)],
            x_data=[1, 1, 5],
            y_data=[1, 1, 3],
            z_data=[1, 9, 1],
            aggregate_fn=np.sum
            )
    ref = np.array([[10, 0, 0], [0, 0, 1]])
    assert (test == ref).all()

# ----------------------------------------------------------------
# plotting positions
# ----------------------------------------------------------------


def test_plotting_positions_Weibull() -> None:
    test = EDA.plotting_position(3, method="Weibull")
    ref = [0.25, 0.5, 0.75]
    test = [round(i, 4) for i in test]
    ref = [round(i, 4) for i in ref]
    assert test == ref


def test_plotting_positions_Hazen() -> None:
    test = EDA.plotting_position(3, method="Hazen")
    ref = [1/6, 3/6, 5/6]
    test = [round(i, 4) for i in test]
    ref = [round(i, 4) for i in ref]
    assert test == ref


def test_plotting_positions_Cunnane() -> None:
    test = EDA.plotting_position(3, method="Cunnane")
    ref = [0.1875, 0.5, 0.8125]
    test = [round(i, 4) for i in test]
    ref = [round(i, 4) for i in ref]
    assert test == ref


def test_plotting_positions_Chegodayev() -> None:
    test = EDA.plotting_position(3, method="Chegodayev")
    ref = [7/34, 0.5, 27/34]
    test = [round(i, 4) for i in test]
    ref = [round(i, 4) for i in ref]
    assert test == ref


def test_plotting_positions_Beard() -> None:
    test = EDA.plotting_position(3, method="Beard")
    ref = [273/1346, 1/2, 1073/1346]
    test = [round(i, 4) for i in test]
    ref = [round(i, 4) for i in ref]
    assert test == ref


# ----------------------------------------------------------------
# quality investigation
# ----------------------------------------------------------------


def test_missing_days() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 2),
                pd.Timestamp(2000, 1, 4)],
            "discharge": [1, 2, 3]
            }).set_index("date")
    test = EDA.missing_days(df)
    ref = [pd.Timestamp(2000, 1, 3)]
    assert len(test) == len(ref)
    assert all([a == b for a, b in zip(test, ref)])


def test_missing_days_2() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 3),
                pd.Timestamp(2000, 1, 5)],
            "discharge": [1, 2, 3]
            }).set_index("date")
    test = EDA.missing_days(df)
    ref = [pd.Timestamp(2000, 1, 2), pd.Timestamp(2000, 1, 4)]
    assert len(test) == len(ref)
    assert all([a == b for a, b in zip(test, ref)])


def test_missing_days_3() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 3),
                pd.Timestamp(2000, 1, 1)],
            "discharge": [1, 2]
            }).set_index("date")
    test = EDA.missing_days(df)
    ref = [pd.Timestamp(2000, 1, 2)]
    assert len(test) == len(ref)
    assert all([a == b for a, b in zip(test, ref)])


def test_missing_days_4() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 2),
                pd.Timestamp(2000, 1, 1)],
            "discharge": [1, 2]
            }).set_index("date")
    test = EDA.missing_days(df)
    ref = []
    assert len(test) == len(ref)
    assert all([a == b for a, b in zip(test, ref)])


def test_duplicates() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 2)],
            "discharge": [1, 2, 3]
            }).set_index("date")
    test = EDA.duplicates(df)
    ref = [pd.Timestamp(2000, 1, 1)]
    assert test == ref


def test_no_duplicates() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 2),
                pd.Timestamp(2000, 1, 3)],
            "discharge": [1, 2, 3]
            }).set_index("date")
    test = EDA.duplicates(df)
    ref = []
    assert test == ref


def test_search_missing_values() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 2),
                pd.Timestamp(2000, 1, 3)],
            "discharge": [-999, 2, 3]
            }).set_index("date")
    test = EDA.search_missing_values(df=df, colname="discharge", val=-999)
    ref = [pd.Timestamp(2000, 1, 1)]
    assert test == ref


def test_search_missing_values2() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 2),
                pd.Timestamp(2000, 1, 3)],
            "discharge": [-999, "-999", 3]
            }).set_index("date")
    test = EDA.search_missing_values(df=df, colname="discharge", val="-999")
    ref = [pd.Timestamp(2000, 1, 2)]
    assert test == ref


def test_search_missing_values3() -> None:
    df = pd.DataFrame({
            "date": [
                pd.Timestamp(2000, 1, 1),
                pd.Timestamp(2000, 1, 2),
                pd.Timestamp(2000, 1, 3)],
            "discharge": [1, 2, 3]
            }).set_index("date")
    test = EDA.search_missing_values(df=df, colname="discharge", val=1)
    ref = [pd.Timestamp(2000, 1, 1)]
    assert test == ref


def test_outlier_iqr_1(list_with_outlier1) -> None:
    data = list_with_outlier1
    outlier_ref = [-100, 100]
    corr_data_ref = [-100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]

    outlier_test, corr_data_test = EDA.outlier(
        data, method="iqr", solving_strategy="none")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_iqr_2(list_with_outlier1) -> None:
    data = list_with_outlier1
    outlier_ref = [-100, 100]
    corr_data_ref = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    outlier_test, corr_data_test = EDA.outlier(
        data, method="iqr", solving_strategy="drop_outlier")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_iqr_3(list_with_outlier1) -> None:
    data = list_with_outlier1
    outlier_ref = [-100.0, 100.0]
    corr_data_ref = [-6.25, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0,
                     8.0, 9.0, 10.0, 17.25]

    outlier_test, corr_data_test = EDA.outlier(
        data, method="iqr", solving_strategy="cap_outlier")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_zscore_1(list_with_outlier2) -> None:
    data = list_with_outlier2
    outlier_ref = [15.0]
    corr_data_ref = data

    outlier_test, corr_data_test = EDA.outlier(
        data, method="zscore", solving_strategy="none")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_zscore_2(list_with_outlier2) -> None:
    data = list_with_outlier2
    outlier_ref = [15.0]
    corr_data_ref = [1.0, 2.0, 2.0, 2.0, 3.0, 1.0, 1.0, 2.0, 2.0, 2.0,
                     3.0, 1.0, 1.0, 2.0]

    outlier_test, corr_data_test = EDA.outlier(
        data, method="zscore", solving_strategy="drop_outlier")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_zscore_3(list_with_outlier2) -> None:
    data = list_with_outlier2
    outlier_ref = [15.0]
    upper_border = EDA.arithmetic_mean(data) + 3*EDA.stdev(data, biased=False)
    corr_data_ref = [1.0, 2.0, 2.0, 2.0, 3.0, 1.0, 1.0, upper_border,
                     2.0, 2.0, 2.0, 3.0, 1.0, 1.0, 2.0]

    outlier_test, corr_data_test = EDA.outlier(
        data, method="zscore", solving_strategy="cap_outlier")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_hampler_1(list_with_outlier2) -> None:
    data = list_with_outlier2
    outlier_ref = [15.0]
    corr_data_ref = data

    outlier_test, corr_data_test = EDA.outlier(
        data, method="hampler_filter", solving_strategy="none")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_hampler_2(list_with_outlier2) -> None:
    data = list_with_outlier2
    outlier_ref = [15.0]
    corr_data_ref = [1.0, 2.0, 2.0, 2.0, 3.0, 1.0, 1.0, 2.0, 2.0, 2.0,
                     3.0, 1.0, 1.0, 2.0]

    outlier_test, corr_data_test = EDA.outlier(
        data, method="hampler_filter", solving_strategy="drop_outlier")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test


def test_outlier_hampler_3(list_with_outlier2) -> None:
    data = list_with_outlier2
    outlier_ref = [15.0]
    corr_data_ref = [1.0, 2.0, 2.0, 2.0, 3.0, 1.0, 1.0, 5.0, 2.0, 2.0, 2.0,
                     3.0, 1.0, 1.0, 2.0]

    outlier_test, corr_data_test = EDA.outlier(
        data, method="hampler_filter", solving_strategy="cap_outlier")

    assert Counter(outlier_ref) == Counter(outlier_test)
    assert corr_data_ref == corr_data_test
