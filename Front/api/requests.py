import requests as req
from api.urls import API_URL
import streamlit as st
import numpy as np 

def get_max_price():
    res = req.get(API_URL[1])
    if res.status_code != 200:
        st.error("Error fetching max price!")
    else:
        return res.json()["max_price"]


def get_categories():
    res = req.get(API_URL[2])
    if res.status_code != 200:
        st.error("Error fetching categories!")
    else:
        return res.json()["categories"]


def get_apps_data(params):
    res = req.get(API_URL[0], params={
        k: v for k, v in params.items() if v is not None})
    if res.status_code != 200:
        st.error("Error fetching results.")
    else:
        return res.json()


def post_apps_data(params: dict):
    try:
        response = req.post(API_URL[0], json=params)
        if response.status_code == 200:
            st.success("App data submitted successfully!")
            return response.json()
        else:
            error_message = f"Failed to submit app data. Status Code: {response.status_code}, Response: {response.text}"
            st.error(error_message)
            return None

    except req.exceptions.RequestException as e:
        st.error(f"An error occurred while submitting app data: {str(e)}")
        return None


def get_statistics(params):
    res = req.get(API_URL[3], params=params)
    if res.status_code != 200:
        st.error("Error fetching statistics.")
    else:
        return res.json()


def put_app(params):

    def convert_to_serializable(value):
        if isinstance(value, (np.int64, np.int32, np.float64, np.float32)):
            return int(value) if isinstance(value, (np.int64, np.int32)) else float(value)
        return value
    
    app_data = {key: convert_to_serializable(val) for key, val in params.items()}
    res = req.put(f"{API_URL[0]}{params['app_id']}", json=app_data)

    if res.ok:
        st.success(f"Updated app {params['app_id']} successfully.")
    elif res.status_code == 404:
        st.error(f"App with ID {params['app_id']} not found.")
    else:
        st.error(f"Failed to update app {params['app_id']}: {res.text}")


def delete_app(app_id):
    res = req.delete(f"{API_URL[0]}{app_id}")
    if res.ok:
        st.success(f"Deleted app {app_id} successfully.")
    else:
        st.error(
            f"Failed to delete app {app_id}: {res.text}")
