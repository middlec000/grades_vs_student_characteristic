from typing import List
from scipy.stats import f_oneway, shapiro, levene, ttest_ind
import pandas as pd

def get_menu_items() -> dict:
    menu = {
        "Get Help": None,
        "Report a Bug": 'https://github.com/middlec000/grades_vs_student_characteristic',
        "About": "This site is intended to be used by teachers to test if there are statistically significant differences in class performance between groups of students. These groups are formed using characteristics of the students such as ethnicity, income level, or neighborhood. These characteristics must be present in the data file before it is uploaded and likely must be added to the grades file by the teacher.\n\nThis site may be used by anyone wishing to investigate differences in a continuous variable between groups where groups are based on a categorical variable.\n\nView code at: [https://github.com/middlec000/grades_vs_student_characteristic](https://github.com/middlec000/grades_vs_student_characteristic)\n\nCreated by Colin Middleton.\n\nPersonal website: [https://middlec000.github.io/](https://middlec000.github.io/)"
    }
    return menu


def get_descriptive_stats(df: pd.DataFrame, group_var: str, measure_var: str) -> pd.DataFrame:
    """Generates descriptive statistics for each group.

    Args:
        df (pd.DataFrame): Original dataset.

        group_var (str): Variable in df upon which groupings are performed.

        measure_var (str): Variable in df upon which groups are compared.

    Returns:
        summary (pd.DataFrame): Descriptive statistics of groups.
    """
    summary = df.groupby(group_var)[measure_var].agg([
        ('Min', 'min'),
        ('Max', 'max'),
        ('Mean','mean'),
        ('Median', 'median'),
        ('Standard Deviation', 'std')
    ])
    return summary


def test_normality(group_names: List[str], groups: List[List[float]], params: dict) -> pd.DataFrame:
    """Performs Shapiro-Wilk Test for normality. Tests each group to determine if it is normally distributed.

    Args:
        group_names (List[str]): List of names/labels for the groups.

        groups (List[List[float]]): List of groups. Each group is represented a list of continuous (float) values.
        
        params (dict): Collection of passed parameters as follows:
            alpha (float): Alpha corresponding to the confidence level.

            center (str): Which measure of center to use. Options: 'mean', 'median', and 'trimmed'.

            normality_checker (str): Which method to use to check the normality assumption. Options: 'Shapiro-Wilk Test'

            homoskedasticity_checker (str): Which method to use to check the homoskedasticity assumption. Options: 'Levene Test'

            proportiontocut (float): If 'trimmed' is the chosen measure of center, proportiontocut tells which proportion of the data to trim.

    Returns:
        summary (pd.DataFrame): DataFrame that summarized the Shapiro-Wilk tests on each group. Records the test statistic, pvalue, and conclusion of hypothesis test.
    """
    columns = ['Statistic', 'p-Value', 'Normally Distributed?']
    summary = pd.DataFrame(index=group_names, columns=columns)
    for i in range(len(group_names)):
        statistic, pvalue = shapiro(groups[i])
        summary.loc[group_names[i]] = {columns[0]: statistic, columns[1]: pvalue, columns[2]: pvalue > params['alpha']}
    return summary


def test_homoskedasticity(groups: List[List[float]], params: dict) -> pd.DataFrame:
    """Performs Levene Test for homoskedasticity (equal variances) in groups.

    Args:
        groups (List[List[float]]): List of groups. Each group is represented a list of continuous (float) values.
        
        params (dict): Collection of passed parameters as follows:
            alpha (float): Alpha corresponding to the confidence level.

            center (str): Which measure of center to use. Options: 'mean', 'median', and 'trimmed'.

            normality_checker (str): Which method to use to check the normality assumption. Options: 'Shapiro-Wilk Test'

            homoskedasticity_checker (str): Which method to use to check the homoskedasticity assumption. Options: 'Levene Test'

            proportiontocut (float): If 'trimmed' is the chosen measure of center, proportiontocut tells which proportion of the data to trim.

    Returns:
        summary (pd.DataFrame): DataFrame that summarized the Levene test for homoskedasticity. Records the test statistic, pvalue, and conclusion of hypothesis test.
    """
    statistic, pvalue = levene(*groups, center=params['center'], proportiontocut=params['proportiontocut'])
    summary = pd.DataFrame(columns=['Statistic', 'p-Value', 'Equal Variance?'], data=[[statistic, pvalue, pvalue > params['alpha']]])
    return summary


def test_anova(groups: List[List[float]], params: dict) -> pd.DataFrame:
    """Performs one-way ANOVA test on the passed groups.

    Args:
        groups (List[List[float]]): List of groups. Each group is represented a list of continuous (float) values.

        params (dict): Collection of passed parameters as follows:
            alpha (float): Alpha corresponding to the confidence level.

            center (str): Which measure of center to use. Options: 'mean', 'median', and 'trimmed'.

            normality_checker (str): Which method to use to check the normality assumption. Options: 'Shapiro-Wilk Test'

            homoskedasticity_checker (str): Which method to use to check the homoskedasticity assumption. Options: 'Levene Test'

            proportiontocut (float): If 'trimmed' is the chosen measure of center, proportiontocut tells which proportion of the data to trim.

    Returns:
        summary (pd.DataFrame): DataFrame that summarized the ANOVA test. Records the test statistic, pvalue, and conclusion of hypothesis test.
    """
    statistic, pvalue = f_oneway(*groups)
    summary = pd.DataFrame(columns=['Statistic', 'p-Value', 'All Groups the Same?'], data=[[statistic, pvalue, pvalue > params['alpha']]])
    return summary


def test_pairwise(group_names: List[str], groups: List[List[float]], params: dict, equal_var: bool) -> pd.DataFrame:
    """Performs pairwise t-tests for equal means on each pairing of the groups.

    Args:
        group_names (List[str]): List of group names.

        groups (List[List[float]]): List of groups. Each group is represented a list of continuous (float) values.

        params (dict): Collection of passed parameters as follows:
            alpha (float): Alpha corresponding to the confidence level.

            center (str): Which measure of center to use. Options: 'mean', 'median', and 'trimmed'.

            normality_checker (str): Which method to use to check the normality assumption. Options: 'Shapiro-Wilk Test'

            homoskedasticity_checker (str): Which method to use to check the homoskedasticity assumption. Options: 'Levene Test'

            proportiontocut (float): If 'trimmed' is the chosen measure of center, proportiontocut tells which proportion of the data to trim.

        equal_var (bool): [description]

    Returns:
        summary (pd.DataFrame): Summary of paired t-tests that records for each pairing the test statistic, pvalue, and conclusion of the hypothesis test.
    """
    # Create Two Level Index
    first = []
    second = []
    for name1 in group_names:
        for name2 in group_names:
            if name1 != name2:
                first.append(name1)
                second.append(name2)
    index = pd.MultiIndex.from_tuples(list(zip(first, second)))
    columns = ['Statistic', 'p-Value', 'Different?']
    summary = pd.DataFrame(index=index, columns=columns)
    
    # Get Results
    for i in range(len(group_names)):
        name1 = group_names[i]
        group1 = groups[i]
        for j in range(len(group_names)):
            name2 = group_names[j]
            group2 = groups[j]
            statistic, pvalue = ttest_ind(group1, group2, equal_var=equal_var)
            summary.loc[(name1, name2)] = {columns[0]:statistic, columns[1]:pvalue, columns[2]:pvalue < params['alpha']}

    for column in [x for x in summary.columns if x not in columns]:
        summary = summary.drop(column, axis=1)
    return summary

def file_format_example() -> pd.DataFrame:
    data = {'Student ID (Optional, Not Used)':['Student ID 1', 'Student ID 2'], 'Measurement (Continuous)':['Measurement for Student 1', 'Measurement for Student 2'], 'Group (Categorical)':['Group for Student 1', 'Group for Student 2']}
    example = pd.DataFrame(data=data)
    return example