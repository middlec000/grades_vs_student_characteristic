# Overview
 Use an ANOVA test to determine if there is a significant difference in grades between groups of students where groups are based on some characteristic such as race.

# Outline
## Upload Data
Allow the user to upload the data. This must be .csv file with the following structure:  
columns: grade_1, grade_2, ... student_characteristic  
row index: student_1, student_2, ...  
TODO: create a table to show structure here

## Select Variables
Let the user select which is the grouping variable and which is the measurement variable.

## Determine Appropriate Test
If student_characteristic has only 2 values, such as white and non-white, use a t-test. If student_characteristic has more than 2 values, use an ANOVA test followed by paired t-tests if the ANOVA is significant. If there are too many groups alert the user.

## Assess Test Assumptions
Determine if the following assumptions are met:  
* Continuous variable is normally distributed.  (Shapiro-Wilk Test)
* Variance is equal between groups. (Levene Test)

## Present Findings
Show the user the findings.