import streamlit as st
import pandas as pd
from datetime import datetime


def visualize_statistics(last_updated, released_time, rating_counts, running_time):
    last_updated_dt = [datetime.strptime(
        date, "%Y-%m-%d") for date in last_updated] if last_updated else []
    released_time_dt = [datetime.strptime(
        date, "%Y-%m-%d") for date in released_time] if released_time else []

    st.write(f"Query Execution Time {running_time}")

    cols = st.columns(2)

    with cols[0]:
        if last_updated_dt:
            df_last_updated = pd.DataFrame({
                "Date": last_updated_dt,
                "Count": range(len(last_updated_dt), 0, -1)
            })
            st.subheader("Last Updated")
            st.area_chart(df_last_updated.set_index("Date"))

        if rating_counts:
            rating_df = pd.DataFrame({
                "Rating": list(rating_counts.keys()),
                "Number of Apps": list(rating_counts.values())
            }).sort_values(by="Rating")

            st.subheader("Rating")
            st.bar_chart(rating_df.set_index("Rating"))
    with cols[1]:
        if released_time_dt:
            df_released_time = pd.DataFrame({
                "Date": released_time_dt,
                "Count": range(1, len(released_time_dt) + 1)
            })
            st.subheader("Released Time")
            st.area_chart(df_released_time.set_index("Date"))
