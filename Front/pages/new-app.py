import streamlit as st
from api.requests import get_categories, post_apps_data

st.set_page_config(layout="wide")

categories = get_categories()

st.header("New App")

form = st.form(key='new-app-form')
with form:
    app_name = st.text_input('App Name', key='app_name')
    category_id = st.selectbox("Category", list(
        categories.keys()), key='category_id')
    price = st.number_input('Price ($)', min_value=0, key='price')
    size = st.number_input('Size (MB)', min_value=0, key='size')
    minimum_android_version = st.text_input(
        'Minimum Android Version', key='minimum_android_version')
    developer_name = st.text_input('Developer Name', key='developer_name')
    developer_website = st.text_input(
        'Developer Website', key='developer_website')
    developer_email = st.text_input('Developer Email', key='developer_email')
    ad_supported = st.checkbox('Ad Supported', key='ad_supported')
    in_app_purchases = st.checkbox('In-App Purchases', key='in_app_purchases')
    editors_choice = st.checkbox("Editor's Choice", key='editors_choice')

    if st.form_submit_button('Submit'):
        app_data = {
            "app_name": app_name,
            "category_id": categories[category_id], 
            "price": price,
            "size": size,
            "minimum_android_version": minimum_android_version,
            "developer_name": developer_name,
            "developer_website": developer_website,
            "developer_email": developer_email,
            "ad_supported": ad_supported,
            "in_app_purchases": in_app_purchases,
            "editors_choice": editors_choice
        }
        response = post_apps_data(app_data)

        if response:
            st.write("API Response:", response)