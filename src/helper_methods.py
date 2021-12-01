import streamlit as st
from scipy.stats import f_oneway
from scipy.stats import shapiro
from scipy.stats import levene

def test_normality(group_names, groups, alpha: float) -> dict:
    normal = []
    for group in groups:
        normal.append(shapiro(group)[1] > alpha)
    return dict(zip(group_names, normal))

def test_homoscedasticity(df, group_var: str, measure_var: str, alpha: float, center: str):
    return

def anova(groups):
    return f_oneway(*groups)