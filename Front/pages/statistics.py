from components.statistics import visualize_statistics
import streamlit as st
from api.requests import get_categories, get_statistics

st.set_page_config(layout="wide")

categories = get_categories()
st.header("Statistics")

st.sidebar.header('Options')
category_id = categories[st.sidebar.selectbox(
    "Category", list(categories.keys()))]
year = st.sidebar.number_input("Year", min_value=2009, max_value=2025, step=1)

if st.sidebar.button("Get Statistics"):
    params = {"category_id": category_id, "year": year}
    stats = get_statistics(params)
    if stats:
        visualize_statistics(stats['last_updated'],
                             stats['released_time'], stats['rating_counts'], stats['execution_time'])
