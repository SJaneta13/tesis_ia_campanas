import streamlit as st
import pandas as pd
import plotly.express as px

print("Checking st.dataframe...")
try:
    # Use a try-except block to catch type errors if the signature is wrong
    st.dataframe(pd.DataFrame({'a':[1]}), width="stretch") 
    print("SUCCESS: st.dataframe accepts width='stretch'")
except Exception as e:
    print(f"FAIL: st.dataframe {e}")

print("Checking st.plotly_chart...")
try:
    fig = px.bar(x=[1], y=[1])
    st.plotly_chart(fig, width="stretch")
    print("SUCCESS: st.plotly_chart accepts width='stretch'") 
except TypeError as e:
    # st.plotly_chart might not take 'width' as argument yet if it's lagging
    print(f"FAIL: st.plotly_chart {e}")
except Exception as e:
    print(f"FAIL: st.plotly_chart {e}")
