import streamlit as st
import pandas as pd
from api.requests import put_app, delete_app


def get_changed_rows(original: pd.DataFrame, edited: pd.DataFrame):
    changed_rows = []
    for idx in edited.index:
        for col in original.columns:
            if col == "delete":
                continue
            if original.loc[idx, col] != edited.loc[idx, col]:
                changed_rows.append(idx)
                break
    return changed_rows


def paginate_data(data: list, total: int, total_pages: int, page_numbers: list, running_time: int):
    if "page" not in st.session_state:
        st.session_state.page = 1
    columns = st.columns(3)
    with columns[0]:
        st.write(f"Page {st.session_state.page} of {total_pages}")
    with columns[1]:
        st.write(f"{total} Rows")
    with columns[2]:
        st.write(f"Query Execution Time {running_time}")

    df = pd.DataFrame(data)
    df["delete"] = False
    edited_df = st.data_editor(
        df,
        column_config={
            "delete": st.column_config.CheckboxColumn(
                "Delete",
                default=False,
            )
        },
        hide_index=True,
    )
    if st.button("Apply Changes"):
        for _, row in edited_df.iterrows():
            if row["delete"]:
                delete_app(row["Id"])

        changed_row_indices = get_changed_rows(df, edited_df)
        for idx in changed_row_indices:
            row = edited_df.loc[idx]
            if row["delete"]:
                continue
            params = {
                'app_id': row['Id'],
                'app_name': row['App Name'],
                'category_name': row['Category Name'],
                'developer_name': row['Developer Name'],
                'developer_email': row['Developer Email'],
                'developer_website': row['Developer Website'],
                'rating': row['Rating'],
                'rating_count': row['Rating Count'],
                'content_rating': row['Content Rating'],
                'installs': row['Installs'],
                'price': row['Price'],
                'size': row['Size'],
                'released': row['Released'],
                'last_updated': row['Last Updated'],
            }
            put_app(params)

        st.rerun()

    cols = st.columns(len(page_numbers) + 2)

    with cols[0]:
        if st.session_state.page > 1:
            if st.button("Previous"):
                st.session_state.page -= 1
                st.rerun()
        else:
            st.button("Previous", disabled=True)

    for idx, page_num in enumerate(page_numbers):
        with cols[idx + 1]:
            if st.button(
                str(page_num),
                key=f"page_{page_num}",
                disabled=(page_num == st.session_state.page)
            ):
                st.session_state.page = page_num
                st.rerun()

    with cols[-1]:
        if st.session_state.page < total_pages:
            if st.button("Next"):
                st.session_state.page += 1
                st.rerun()
        else:
            st.button("Next", disabled=True)
