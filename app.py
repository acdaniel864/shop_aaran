import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Constants
API_URL = st.secrets['api_url']
HEADERS = {
    "x-api-key": st.secrets['api_key'],
    'Content-Type': 'application/json'
}

# Function to call the API
def call_lwin(lwin_array, timeout=10):
    lwin_type = len(lwin_array[0])
    payload = {f"lwin{lwin_type}": lwin_array}
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=timeout)
    print("call_lwin response status code:", response.status_code)
    return response

# Function to validate LWIN code
def validate_string(s):
    if len(s) not in [7, 11, 16, 18]:
        raise ValueError(f"Whoa there! The length of the LWIN must be 7, 11, 16, or 18. Current length is {len(s)}.")
    if not s.isdigit():
        raise ValueError("Bro?! LWINs contain numeric characters only.")
    return s

# Function to call the stock API with a single LWIN code
def call_stock_api_single_lwin(lwin_code):
    lwin_code = str(lwin_code).strip()
    try:
        valid_lwin = validate_string(lwin_code)
        lwin_array = [valid_lwin]
        all_results = []
        response = call_lwin(lwin_array)
        if response.status_code == 200:
            results = response.json().get('wines', [])
            all_results.extend(results)
        else:
            return None, f"We were unable to find results for {lwin_code}, send screenshot to Aaran {response.status_code}."
        df = pd.DataFrame(all_results)
        df.drop(columns=['type', 'time_extracted', 'merchant_description', 'id', 'lwin11', 'lwin16', 'lwin7'], inplace=True)
        df.rename(columns={'display_name': 'name', 'producer_name': 'producer'}, inplace=True)
        return df, None
    except ValueError as e:
        return None, str(e)

# Streamlit app layout
st.set_page_config(page_title="Shop Aaran - Stock Checker", layout="wide", initial_sidebar_state="expanded")

# Add custom CSS to hide the GitHub icon
st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .reportview-container {
        background: #262641;
        color: #FAFCFE;
        font-family: Arial, sans-serif;
    }
    .sidebar .sidebar-content {
        background: #262641;
        color: #FAFCFE;
    }
    .stButton>button {
        background-color: #9437ff;
        border-color: #9437ff;
    }
    .stButton>button:hover {
        background-color: #A2FF37;
        border-color: #A2FF37;
        color: #262641;
    }
    </style>
    """,
    unsafe_allow_html=True
)

logo_path_1 = 'images/winefi_white.svg' 
st.image(logo_path_1, width=230)
st.title("Shop Aaran - Stock Checker")

# Input field for LWIN code
lwin_code = st.text_input("Enter a single LWIN code of any length", "")

# Button to submit the LWIN code
submit_button = st.button("Submit")

# Placeholder for the results
results_placeholder = st.empty()

# Placeholder for the download button
download_button_placeholder = st.empty()

if submit_button:
    if not lwin_code:
        st.error("Please enter a valid ID code.")
    else:
        df, error = call_stock_api_single_lwin(lwin_code)
        if error:
            st.error(error)
        elif df is not None:
            # Display the DataFrame using Streamlit's built-in interactive dataframe
            results_placeholder.dataframe(df, use_container_width=True)

            # Add download button
            def convert_df(df):
                return df.to_csv().encode('utf-8')

            csv = convert_df(df)

            download_button_placeholder.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{datetime.now().strftime('%Y%m%d')}_{lwin_code}_dataframe.csv",
                mime='text/csv',
            )
        else:
            st.error("Data fetch unsuccessful. Please try again.")