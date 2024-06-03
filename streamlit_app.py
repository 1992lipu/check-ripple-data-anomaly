import streamlit as st
import pandas as pd
from io import BytesIO

def load_data(file):
    return pd.read_excel(file, sheet_name='Meter Readings - ELECTRICITY')

def clean_data(data):
    return data.drop_duplicates()

def convert_to_datetime(data):
    data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%d-%b-%Y %I:%M:%S %p')
    return data

def calculate_differences(data):
    data['EB_Khw_Diff'] = data['Meter Reading EB Khw'].diff()
    data['DG_Khw_Diff'] = data['Meter Reading DG Khw'].diff()
    return data

def identify_anomalies(data):
    eb_mean = data['EB_Khw_Diff'].mean()
    eb_std = data['EB_Khw_Diff'].std()
    dg_mean = data['DG_Khw_Diff'].mean()
    dg_std = data['DG_Khw_Diff'].std()
    
    eb_anomalies = data[(data['EB_Khw_Diff'] < 0) | (data['EB_Khw_Diff'] > eb_mean + 3 * eb_std)]
    dg_anomalies = data[(data['DG_Khw_Diff'] < 0) | (data['DG_Khw_Diff'] > dg_mean + 3 * dg_std)]
    
    anomalies = pd.concat([eb_anomalies, dg_anomalies]).drop_duplicates().sort_values(by='Datetime')
    return anomalies

st.title("Meter Reading Anomaly Detection")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    data = load_data(BytesIO(uploaded_file.read()))
    
    data = clean_data(data)
    data = convert_to_datetime(data)
    data = calculate_differences(data)
    anomalies = identify_anomalies(data)
    
    st.write("Anomalies detected:")
    st.write(anomalies)
