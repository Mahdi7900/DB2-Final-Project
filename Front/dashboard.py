from components.data import paginate_data
import streamlit as st
from api.requests import get_apps_data, get_categories, get_max_price

st.set_page_config(layout="wide")

max_price = get_max_price()
categories = get_categories()
st.header("App Search Dashboard")
st.sidebar.header("Filters")

search_query = st.text_input("Search")

SORT_COLUMNS = {
    "None": None,
    "App Name": "app_name",
    "Category Name": "category_name",
    "Developer Name": "developer_name",
    "Rating": "rating",
    "Price": "price",
    "Installs": "installs",
    "Size": "size",
    "Released": "released",
    "Last Updated": "last_updated"
}

category = st.sidebar.selectbox(
    "Category", (["All"] + list(categories.keys())))
category_filter = None if category == "All" else categories[category]

sort_by = st.sidebar.selectbox("Sort by", list(SORT_COLUMNS.keys()))
sort_order = st.sidebar.radio(
    "Sort order", ["Ascending", "Descending"], horizontal=True)

rating = st.sidebar.slider("Rating", 0.0, 5.0, (0.0, 5.0))
price = st.sidebar.slider(
    "Price", 0.0, max_price, (0.0, max_price))

col1, col2 = st.sidebar.columns([2, 2])
with col1:
    is_free = st.radio("Is Free?", [None, False, True])
    ad_supported = st.radio("Ad Supported?", [None, False, True])
with col2:
    in_app_purchases = st.radio("In-App Purchases?", [None, False, True])
    editors_choice = st.radio("Editors Choice?", [None, False, True])

sort_order_api = "asc" if sort_order == "Ascending" else "desc"

if "page" not in st.session_state:
    st.session_state.page = 1
if "page_size" not in st.session_state:
    st.session_state.page_size = 10

params = {
    "search_query": search_query,
    "min_rating": rating[0],
    "max_rating": rating[1],
    "min_price": price[0],
    "max_price": price[1],
    "category_id": category_filter,
    "is_free": is_free,
    "ad_supported": ad_supported,
    "in_app_purchases": in_app_purchases,
    "editors_choice": editors_choice,
    "page": st.session_state.page,
    "page_size": st.session_state.page_size,
    "sort_by": SORT_COLUMNS[sort_by],
    "sort_order": sort_order_api
}

apps = get_apps_data(params)
if apps:
    paginate_data(apps["data"], apps["total"], apps["total_pages"],
                  apps["page_numbers"], apps["execution_time"])
