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

def generate_summary(anomalies):
    summary = "The following anomalies were identified in the meter readings:\n"
    for i, row in anomalies.iterrows():
        summary += f"\n{len(summary.splitlines())}. **{row['Datetime'].strftime('%d-%b-%Y %H:%M:%S')}**:\n"
        if row['EB_Khw_Diff'] < 0:
            summary += f"   - Negative change in `Meter Reading EB Khw` ({row['EB_Khw_Diff']} kWh).\n"
        elif row['EB_Khw_Diff'] > anomalies['EB_Khw_Diff'].mean() + 3 * anomalies['EB_Khw_Diff'].std():
            summary += f"   - Unusually high increase in `Meter Reading EB Khw` ({row['EB_Khw_Diff']} kWh).\n"
        if row['DG_Khw_Diff'] < 0:
            summary += f"   - Negative change in `Meter Reading DG Khw` ({row['DG_Khw_Diff']} kWh).\n"
        elif row['DG_Khw_Diff'] > anomalies['DG_Khw_Diff'].mean() + 3 * anomalies['DG_Khw_Diff'].std():
            summary += f"   - Unusually high increase in `Meter Reading DG Khw` ({row['DG_Khw_Diff']} kWh).\n"
    return summary

st.title("Meter Reading Anomaly Detection - Created by Debaprasad")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    data = load_data(BytesIO(uploaded_file.read()))
    
    data = clean_data(data)
    data = convert_to_datetime(data)
    data = calculate_differences(data)
    anomalies = identify_anomalies(data)
    
    if not anomalies.empty:
        summary = generate_summary(anomalies)
        st.write(summary)
    else:
        st.write("No anomalies detected.")
