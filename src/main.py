import streamlit as st
import pandas as pd
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
def get_example_data() -> pd.DataFrame:
    source = 'https://raw.githubusercontent.com/middlec000/grades_vs_student_characteristic/main/example_data/example_data.csv'
    # source = './example_data/example_data.csv'
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


def main():
    # Set Page Configuration
    st.set_page_config(
        layout='wide',
        initial_sidebar_state='collapsed', 
        menu_items=helper_methods.get_menu_items()
    )

    # Create Sidebar
    params = create_sidebar()

    # Get Data
    st.write('# Step 1: Choose Your Data File Or Use Example')
    st.write('I suggest you use the example first, then try the analysis with your own data.')
    own_data_vs_example = st.selectbox(
        label = 'Decide to use your own data or use the example data.', 
        options = ['Example', 'Bring Your Own Data'],
        index = 0
    )
    if own_data_vs_example == 'Example':
        df = get_example_data()
        main2(df=df, params=params)
    else:
        st.write('The file must be one of the following formats: .csv, .xls, .xlsx')
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
        st.write(helper_methods.get_descriptive_stats(df=df, group_var=group_var,measure_var=measure_var))

        st.write('## ANOVA Hypothesis Testing Assumptions')
        normality_results = helper_methods.test_normality(group_names=group_names, groups=groups, params=params)

        homoskedasticity_results = helper_methods.test_homoskedasticity(groups=groups, params=params)
        
        anova_result = helper_methods.test_anova(groups=groups, params=params)

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
    return

if __name__ == '__main__':
    main()