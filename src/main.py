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
def get_groups(df: pd.DataFrame, group_var: str, measure_var: str):
    group_names = df[group_var].unique()
    groups = []
    for group_name in group_names:
        groups += [list(df[df[group_var] == group_name][measure_var].values)]
    return group_names, groups

'# Step 1: Choose Your Data File'
'The file must be one of the following formats: .csv, .xls, .xlsx'
uploaded_file = st.file_uploader("Choose a file")
try:
    df = file_to_dataframe(file=uploaded_file)
except TypeError:
    st.warning("You need to upload a csv or excel file.")

'## Check'
'Below are the first few rows of your file. Please check that it is correct.'
st.write(df.head())

'# Step 2: Select Variables'
group_var = st.selectbox(
    'Select the grouping variable.', 
    (df.columns.to_list())
)
measure_var = st.selectbox(
    'Select the measurement variable.', 
    (df.columns.to_list())
)
if group_var == measure_var:
    st.warning('The measurement variable cannot be the same as the grouping variable.')

# Determine Appropriate Test
test = None
num_groups = df[group_var].nunique()
if num_groups == 1:
    st.warning(f'All students have the same {group_var}. Choose another grouping variable that will split the students into multiple groups.')
elif num_groups == 2:
    test = 'a t-test'
elif num_groups > 2:
    test = 'an ANOVA'
st.write(f'There are {num_groups} groups of students based on {group_var} so {test} test will be performed.')

'# Step 3: Run Analysis'
confidence_level = st.number_input(
    label='Choose the confidence level:',
    min_value=0.0,
    max_value=1.0,
    value=0.95
)
alpha = 1 - confidence_level

group_names, groups = get_groups(df=df, group_var=group_var, measure_var=measure_var)

if st.button(label='Analyze'):
    normality_results = helper_methods.test_normality(group_names=group_names, groups=groups, alpha=alpha)
    
    statistic, pvalue = helper_methods.anova(groups=groups)

    st.write(f'Normality Results: {normality_results}')
    st.write(f'statistic: {statistic}\npvalue: {pvalue}')