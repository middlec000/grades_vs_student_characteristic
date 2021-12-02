import streamlit as st
import pandas as pd
import numpy as np
import helper_methods

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
def get_groups(df: pd.DataFrame, group_var: str, measure_var: str):
    group_names = list(df[group_var].astype(str).unique())
    groups = []
    for group_name in group_names:
        groups += [list(df[df[group_var] == group_name][measure_var].values)]
    return group_names, groups

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

def main():
    # Set Page Configuration
    st.set_page_config(initial_sidebar_state='collapsed', menu_items=helper_methods.get_menu_items())

    # Create Sidebar
    params = create_sidebar()

    # Get Data
    st.write('# Step 1: Choose Your Data File Or Use Example')
    st.write('The file must be one of the following formats: .csv, .xls, .xlsx')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        try:
            df = file_to_dataframe(file=uploaded_file)
        except TypeError:
            st.warning("You need to upload a csv or excel file.")

        st.write('## Visual Check')
        st.write('Below are the first few rows of your file. Please check that these are correct.')
        st.write(df.head())

        # Get Variables
        st.write('# Step 2: Select Variables')
        measure_var = st.selectbox(
            label = 'Select the measurement variable. This is the variable we will compare groups with. Typically this will be a test grade column or cumulative grade column in your data.', 
            options = df.columns.to_list(),
            index = 1
        )
        group_var = st.selectbox(
            label = 'Select the grouping variable. This is the variable with which we will form groups of students. If the group variable is ethnicity, all students of each ethnicity will be grouped together.', 
            options = df.columns.to_list(),
            index = len(df.columns.to_list())-1
        )
        if group_var == measure_var:
            st.warning('The measurement variable cannot be the same as the grouping variable.')

        # Get Groups
        group_names, groups = get_groups(df=df, group_var=group_var, measure_var=measure_var)

        # Check there are 2 or more groups
        num_groups = len(group_names)
        if num_groups == 1:
            st.warning(f'All students have the same {group_var}. Choose another grouping variable that will split the students into multiple groups.')

        st.write('# Step 3: Run Analysis')
        st.write('See additional options in the sidebar on the left. Access it with the arrow at the top left of the page.')

        if st.button(label='Analyze'):
            st.write('## Descriptive Statistics')
            st.write(helper_methods.get_descriptive_stats(df=df, group_var=group_var,measure_var=measure_var))

            st.write('## ANOVA Hypothesis Testing Assumptions')
            normality_results = helper_methods.test_normality(group_names=group_names, groups=groups, params=params)

            homoskedasticity_results = helper_methods.test_homoskedasticity(groups=groups, params=params)
            
            anova_result = helper_methods.test_anova(groups=groups, params=params)

            st.write('### Normal Distribution')
            st.write(f'The ANOVA test requires that each of the groups based on {group_var} are normally distributed in {measure_var}.')
            st.write(normality_results)

            st.write('### Homoskedasticity')
            st.write(f'The ANOVA test requires that each of the groups in {group_var} are have equal variance in {measure_var}.')
            st.write(homoskedasticity_results)

            st.write(f'## Results of ANOVA Test')
            if anova_result['All Groups the Same?'].values:
                st.write(f'### There is No Statistically Significant Difference in mean {measure_var} Between {group_var} Groups at the {(1-params["alpha"])*100}% Confidence Level.')
                st.write(anova_result)
            else:
                st.write(f'### There is a Statistically Significant Difference in {measure_var} Between {group_var} Groups at the {(1-params["alpha"])*100}% Confidence Level.')
                st.write(anova_result)

                st.write('### Post-Hoc Pairwise Significance Test')
                pairwise_results = helper_methods.test_pairwise(
                    group_names=group_names, 
                    groups=groups, 
                    params=params, 
                    equal_var=True
                )
                st.write(pairwise_results)

if __name__ == '__main__':
    main()