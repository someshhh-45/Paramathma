import streamlit as st
import pandas as pd
file=st.file_uploader("upload your file :",type=["csv"])
if file:
    df=pd.read_csv(file)
    st.subheader("data preview")
    st.dataframe(df)