from typing import List
from scipy.stats import f_oneway, shapiro, levene, ttest_ind
import pandas as pd
import streamlit as st

@st.cache
def file_to_dataframe(file) -> pd.DataFrame:
    try:
        # read csv
        df=pd.read_csv(file)
    except:
        try:
            # read xls or xlsx
            df=pd.read_excel(file)
        except:
            raise TypeError
    return df


@st.cache
def get_example_data() -> pd.DataFrame:
    source = 'https://raw.githubusercontent.com/middlec000/grades_vs_student_characteristic/main/example_data/example_data.csv'
    # source = './example_data/example1_data.csv'
    return pd.read_csv(source)


def create_sidebar() -> dict:
    st.sidebar.write('# Additional Parameters')
    confidence_level = st.sidebar.number_input(
        label='Confidence Level:',
        min_value=0.0,
        max_value=1.0,
        value=0.95
    )
    alpha = 1 - confidence_level

    center = st.sidebar.selectbox(
        label = 'Measure of Center:',
        options = ['mean', 'median', 'trimmed'],
        index = 0
    )

    if center == 'trimmed':
        proportiontocut = st.sidebar.number_input(
        label = 'Proportion to Cut:',
        min_value=0.0,
        max_value=1.0,
        value=0.5
    )
    else:
        proportiontocut = 0.5

    normality_checker = st.sidebar.selectbox(
        label = 'How to Check Normality Assumption:',
        options = ['Shapiro-Wilk Test'],
        index = 0
    )

    homoskedasticity_checker = st.sidebar.selectbox(
        label = 'How to Check Homoskedasticity Assumption:',
        options = ['Levene Test'],
        index = 0
    )

    return {'alpha':alpha, 'center':center, 'normality_checker':normality_checker, 'homoskedasticity_checker':homoskedasticity_checker, 'proportiontocut':proportiontocut}


def visual_check(df: pd.DataFrame) -> None:
    st.write('## Visually Check Data')
    st.write('Below are the first few rows of your file. Please check that these are correct.')
    st.write(df.head())
    return


@st.cache
def get_groups(df: pd.DataFrame, measure_var: str, group_var: str):
    group_names = list(df[group_var].astype(str).unique())
    groups = []
    for group_name in group_names:
        groups += [list(df[df[group_var] == group_name][measure_var].values)]
    # Check there are 2 or more groups
    num_groups = len(group_names)
    if num_groups == 1:
        st.warning(f'All students have the same {group_var}. Choose another grouping variable that will split the students into multiple groups.')
    return group_names, groups


def get_menu_items() -> dict:
    menu = {
        "Get Help": None,
        "Report a Bug": 'https://github.com/middlec000/grades_vs_student_characteristic',
        "About": "Last Updated: December 5, 2021\n\nThis site is intended to be used by teachers to test if there are statistically significant differences in class performance between groups of students. These groups are formed using characteristics of the students such as ethnicity, income level, or neighborhood. These characteristics must be present in the data file before it is uploaded and likely must be added to the grades file by the teacher.\n\nThis site may be used by anyone wishing to investigate differences in a continuous variable between groups where groups are based on a categorical variable.\n\nView code at: [https://github.com/middlec000/grades_vs_student_characteristic](https://github.com/middlec000/grades_vs_student_characteristic)\n\nCreated by Colin Middleton.\n\nPersonal website: [https://middlec000.github.io/](https://middlec000.github.io/)"
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


def test_pairwise(group_names: List[str], groups: List[List[float]], params: dict, equal_var: bool, descriptive_stats: pd.DataFrame) -> pd.DataFrame:
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

        equal_var (bool): Result from homoskedasticity test.

        descriptive_stats (pd.DataFrame): The descriptive stats by group produced earlier in the analysis.

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
    columns = ['Statistic', 'p-Value', 'Different?', 'Higher']
    summary = pd.DataFrame(index=index, columns=columns)
    
    # Get Results
    for i in range(len(group_names)):
        name1 = group_names[i]
        group1 = groups[i]
        for j in range(len(group_names)):
            name2 = group_names[j]
            group2 = groups[j]
            statistic, pvalue = ttest_ind(group1, group2, equal_var=equal_var)
            # Determine which has higher mean score
            higher = ''
            if descriptive_stats.loc[name1, 'Mean'] > descriptive_stats.loc[name2, 'Mean']:
                higher = name1
            else:
                higher = name2
            summary.loc[(name1, name2)] = {columns[0]:statistic, columns[1]:pvalue, columns[2]:pvalue < params['alpha'], columns[3]:higher}

    for column in [x for x in summary.columns if x not in columns]:
        summary = summary.drop(column, axis=1)
    return summary

def file_format_example() -> pd.DataFrame:
    data = {'Student ID (Optional, Not Used)':['Student ID 1', 'Student ID 2'], 'Measurement (Continuous)':['Measurement for Student 1', 'Measurement for Student 2'], 'Group (Categorical)':['Group for Student 1', 'Group for Student 2']}
    example = pd.DataFrame(data=data)
    return example