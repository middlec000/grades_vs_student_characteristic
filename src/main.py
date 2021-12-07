import streamlit as st
import pandas as pd
from helper_methods import *

def main():
    # Set Page Configuration
    st.set_page_config(
        layout='wide',
        initial_sidebar_state='collapsed', 
        menu_items=get_menu_items()
    )

    # Create Sidebar
    params = create_sidebar()

    # Disclaimer
    st.write('# Disclaimer: How to Interpret Results')
    st.write('Correlation is not causation! Just because groups may have different grades does not mean that the grouping variable caused those grade differences. For example, if you group students by race and find that black students have lower grades than white students, this does not mean that the difference in race caused the difference in grades. There are likely lurking variables that relate the two such as economic status, parents education level, systemic racism, and others. This website is meant as a tool for teachers to investigate if there is a difference in grades based on some characteristic of students. It cannot tell you where that difference comes from, if it exists.\n\nIf you want to determine if your grouping variable is the cause of the difference in grades, you must perform a randomized controlled study (or find research that has already been done).')

    # Get Data
    st.write('# Step 1: Choose Your Data File Or Use Example')
    st.write('I suggest you use the example first, then try the analysis with your own data. Note that the example data was artificially created and is not from real students.')
    own_data_vs_example = st.radio(
        label = 'Decide to use your own data or use the example data.', 
        options = ['Example', 'Bring Your Own Data'],
        index = 0
    )
    if own_data_vs_example == 'Example':
        df = get_example_data()
        main2(df=df, params=params)
    else:
        st.write('The file must have the following:\n* Be one of these file types: .csv, .xls, .xlsx\n* Be in the format below')
        st.write(file_format_example())
        st.write('* The Measurement column must be continuous - any positive number (in a range) is meaningful. Example: scores from 0 to 30.\n* The Group column must be categorical - students can have one of only a few possible values. Example: race. Also, each group must have at least 3 members.\n* Note: You will likely have to create the Group column yourself in the data file.\n* Look at the Example dataset for further clarification.')
        uploaded_file = st.file_uploader(label="Choose a file",type=['csv', 'xls', 'xlsx'])
        if uploaded_file is not None:
            try:
                df = file_to_dataframe(file=uploaded_file)
                main2(df=df, params=params)
            except TypeError:
                st.warning("You need to upload a csv or excel file.")
    return


def main2(df: pd.DataFrame, params: dict):
    visual_check(df)

    # Get Variables
    st.write('# Step 2: Select Variables')
    st.write('## Measurement Variable')
    measure_var = st.selectbox(
        label = 'Select the measurement variable. This is the variable we will compare groups with. Typically this will be a test grade column or cumulative grade column in your data.', 
        options = df.columns.to_list(),
        index = 1
    )
    st.write('## Grouping Variable')
    group_var = st.selectbox(
        label = 'Select the grouping variable. This is the variable with which we will form groups of students. If the group variable is race, all students of the same race will be grouped together.', 
        options = df.columns.to_list(),
        index = len(df.columns.to_list())-1
    )
    if group_var == measure_var:
        st.warning('The measurement variable cannot be the same as the grouping variable.')
    
    # Get Groups
    group_names, groups = get_groups(df=df, measure_var=measure_var, group_var=group_var)

    st.write('# Step 3: Run Analysis')
    st.write('See additional options in the sidebar on the left. Access it with the arrow at the top left of the page.')

    if st.button(label='Analyze'):
        st.write('## Descriptive Statistics')
        descriptive_stats = get_descriptive_stats(df=df, group_var=group_var,measure_var=measure_var)
        st.write(descriptive_stats)

        st.write('## ANOVA Hypothesis Testing Assumptions')
        normality_results = test_normality(group_names=group_names, groups=groups, params=params)

        homoskedasticity_results = test_homoskedasticity(groups=groups, params=params)
        
        anova_result = test_anova(groups=groups, params=params)

        st.write('### Normal Distribution')
        st.write(f'The ANOVA test requires that each of the groups based on {group_var} are normally distributed in {measure_var}.')
        if normality_results['Normally Distributed?'].all():
            st.success('All groups are normally distributed.')
        else:
            st.error('Not all groups are normally distributed. Results of ANOVA test may not be valid.')
        st.write(normality_results)

        st.write('### Homoskedasticity')
        st.write(f'The ANOVA test requires that each of the groups in {group_var} are have equal variance in {measure_var}.')
        if homoskedasticity_results['Equal Variance?'].all():
            st.success('All groups have similar variances.')
        else:
            st.error('Not all groups have similar variances. Results of ANOVA test may not be valid.')
        st.write(homoskedasticity_results)

        st.write(f'## Results of ANOVA Test')
        if anova_result['All Groups the Same?'].values:
            st.write(f'### There is NO statistically significant difference in {measure_var} means between {group_var} groups at the {(1-params["alpha"])*100}% confidence level.')
            st.write(anova_result)
        else:
            st.write(f'### There IS a statistically significant difference in {measure_var} means between {group_var} groups at the {(1-params["alpha"])*100}% confidence level.')
            st.write(anova_result)

            st.write('### Post-Hoc Pairwise Significance Test')
            st.write(f'First see if there is a statistically significant difference between the {measure_var} means (recorded in the "Different?" column) of the two {group_var}s on the left. If there is a statistically significant difference, then you can see which {group_var} has higher mean {measure_var} in the "Higher" column.')
            pairwise_results = test_pairwise(
                group_names=group_names, 
                groups=groups, 
                params=params, 
                equal_var=homoskedasticity_results['Equal Variance?'].all(),
                descriptive_stats=descriptive_stats
            )
            st.write(pairwise_results)
    return

if __name__ == '__main__':
    main()