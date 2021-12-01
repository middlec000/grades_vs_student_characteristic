import streamlit as st
import pandas as pd

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

def print_hello():
    st.write('hello')

'# Step 3: Run Analysis'
if st.button(label='Analyze'):
    print_hello()