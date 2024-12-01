"""
Project Team: Jonathan Chartrand & Robert Boutette
Course: ENGM 4676 Machine Learning for Engineers
Title: SolarGuard - LSTM Models for Maintenance Optimization
Date: Dec 1, 2024

This file defines the backend logic for the SolarGuard project:
- Simulates live sensor data from a CSV file.
- Uses pre-trained LSTM models to predict DC values.
- Tracks warnings and faults for solar inverters.
- Handles rendering of dynamic web pages for monitoring and control.
"""

from django.shortcuts import render
from django.http import JsonResponse
import threading
import logging
import pandas as pd
import time
import os
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import json

# Initialize logging for debugging
logging.basicConfig(level=logging.DEBUG)

# --- FILE PATHS ---
# Path to the CSV file used for simulating live data
CSV_FILE_PATH = os.path.join('maintenance', 'data', 'live_sim_data.csv')
# Directory containing the pre-trained LSTM models
models_dir = os.path.join('maintenance', 'models')

# --- SHARED DATA STRUCTURES ---
# Holds the latest sensor data
sensor_values = {}
# DataFrame to store live and historical data for all sensors
sensor_data_df = pd.DataFrame()
# DataFrame to log warnings for inverters
warnings_df = pd.DataFrame(columns=[
    'timestamp', 'ambient_temp', 'module_temp', 'irradiation', 'panel',
    'measured_dc', 'predicted_dc', 'pdiff'
])
# DataFrame to log suspected faults for inverters
faults_df = pd.DataFrame(columns=[
    'timestamp', 'ambient_temp', 'module_temp', 'irradiation', 'panel',
    'measured_dc', 'predicted_dc', 'pdiff'
])
# Keeps track of the current row being processed from the CSV file
current_row_index = 0

# --- THREAD-SAFE LOCKS ---
# Lock for thread-safe access to `sensor_values`
sensor_values_lock = threading.Lock()
# Lock for thread-safe access to shared DataFrames
data_lock = threading.Lock()

# --- LOAD MODELS AND SCALERS ---
# Define scalers for feature normalization
scaler_X = MinMaxScaler().fit([[20.4, 18.14, 0.0], [35.25, 65.55, 1.22]])  # Feature scaler
scaler_y = MinMaxScaler().fit([[0], [14471.13]])  # Target scaler
# Load pre-trained LSTM models for each solar panel
models = {f'panel{i}': load_model(os.path.join(models_dir, f'panel{i}_lstm_model.h5')) for i in range(1, 23)}

# --- SIMULATE LIVE SENSOR DATA ---
def simulate_csv_data():
    """
    Simulates live sensor data by reading rows from the CSV file.

    - Processes each row to predict DC values using LSTM models.
    - Updates warnings and faults based on percentage differences.
    - Runs continuously to simulate real-time updates.
    """
    global sensor_data_df, warnings_df, faults_df, current_row_index

    try:
        if not os.path.exists(CSV_FILE_PATH):
            logging.error(f"CSV file not found at '{CSV_FILE_PATH}'. Please ensure the file exists.")
            return

        # Load CSV data into a DataFrame
        csv_data = pd.read_csv(CSV_FILE_PATH)
        csv_data.rename(columns={
            'ambient_temperature': 'ambient_temp',
            'module_temperature': 'module_temp',
            'irradiation': 'irradiation',
        }, inplace=True)

        while True:
            with data_lock:
                if current_row_index < len(csv_data):
                    # Get the current row as a dictionary
                    current_row = csv_data.iloc[current_row_index].to_dict()

                    # List to store predicted DC values for all panels
                    predicted_dc_values = []
                    # Extract input features
                    ambient_temp = current_row['ambient_temp']
                    module_temp = current_row['module_temp']
                    irradiation = current_row['irradiation']

                    # Scale input features for prediction
                    weather_features = np.array([[ambient_temp, module_temp, irradiation]])
                    weather_features_scaled = scaler_X.transform(weather_features)

                    # Loop through all panels to predict DC values
                    for i in range(1, 23):
                        model = models[f'panel{i}']
                        try:
                            # Prepare input for the LSTM model
                            input_sequence = np.array([weather_features_scaled] * 15).reshape(1, 15, -1)
                            # Predict the scaled DC value and inverse transform to the original scale
                            predicted_scaled = model.predict(input_sequence)
                            predicted_dc = scaler_y.inverse_transform(predicted_scaled)[0][0]
                        except Exception as e:
                            logging.error(f"Prediction error for Panel {i}: {e}")
                            predicted_dc = np.nan  # Set to NaN if prediction fails
                        predicted_dc_values.append(round(predicted_dc, 3) if not np.isnan(predicted_dc) else "Error")

                    # Update warnings and faults based on percentage difference
                    for i, predicted_dc in enumerate(predicted_dc_values, start=1):
                        current_row[f'predicted_dc{i}'] = predicted_dc
                        measured_dc = current_row.get(f'measured_dc{i}')
                        if measured_dc is not None and not np.isnan(measured_dc) and predicted_dc != "Error":
                            pdiff = abs((predicted_dc - measured_dc) / measured_dc) * 100
                            if pdiff >= 10:  # Fault condition
                                faults_df = pd.concat([faults_df, pd.DataFrame([{
                                    'timestamp': current_row['timestamp'],
                                    'ambient_temp': ambient_temp,
                                    'module_temp': module_temp,
                                    'irradiation': irradiation,
                                    'panel': i,
                                    'measured_dc': measured_dc,
                                    'predicted_dc': predicted_dc,
                                    'pdiff': pdiff
                                }])], ignore_index=True)
                            elif 5 <= pdiff < 10:  # Warning condition
                                warnings_df = pd.concat([warnings_df, pd.DataFrame([{
                                    'timestamp': current_row['timestamp'],
                                    'ambient_temp': ambient_temp,
                                    'module_temp': module_temp,
                                    'irradiation': irradiation,
                                    'panel': i,
                                    'measured_dc': measured_dc,
                                    'predicted_dc': predicted_dc,
                                    'pdiff': pdiff
                                }])], ignore_index=True)

                    # Update shared sensor data and append to historical data
                    with sensor_values_lock:
                        sensor_values.clear()
                        sensor_values.update(current_row)
                    sensor_data_df = pd.concat([sensor_data_df, pd.DataFrame([current_row])], ignore_index=True)

                    # Move to the next row
                    current_row_index += 1
                else:
                    # Reset to the first row if all rows are processed
                    current_row_index = 0

            # Wait for 30 seconds before processing the next row
            time.sleep(30)

    except Exception as e:
        logging.error(f"Error in simulate_csv_data: {e}")

# Start the simulation thread
csv_simulation_thread = threading.Thread(target=simulate_csv_data, daemon=True)
csv_simulation_thread.start()

def get_sensor_data(request):
    """
    Returns the current sensor data as a JSON response.

    This function fetches the most recent sensor data from the shared data structure (`sensor_values`)
    and, if available, merges it with the last row of historical data from the `sensor_data_df` DataFrame.
    If no data exists in the DataFrame, it returns the sensor values with a message indicating
    that no data is available.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON object containing the current sensor data.
    """
    global sensor_data_df  # Access the global DataFrame storing historical data

    # Use a lock to safely access and copy the shared sensor data
    with sensor_values_lock:
        current_data = sensor_values.copy()  # Make a copy of the current sensor data

    # Check if there is any data in the historical DataFrame
    if len(sensor_data_df) > 0:
        # Get the last row of data as a dictionary (most recent sensor reading)
        latest_row = sensor_data_df.iloc[-1].to_dict()
        # Merge the last row of historical data with the current sensor data
        current_data.update(latest_row)
    else:
        # If the DataFrame is empty, log a warning and provide a default response
        logging.warning("sensor_data_df is empty. No data available.")
        # Update the current data with placeholders indicating no data
        current_data.update({key: 'No data' for key in sensor_values.keys()})

    # Return the combined data as a JSON response
    return JsonResponse(current_data)

# --- VIEW FUNCTIONS ---
def home(request):
    """Render the home page."""
    return render(request, 'maintenance/index.html')

def sensor_data(request):
    """Render the live sensor data page."""
    return render(request, 'maintenance/sensor_data.html')

def maintenance_log(request):
    """Render the maintenance log showing warnings and faults."""
    global warnings_df, faults_df
    return render(request, 'maintenance/log.html', {
        'warning_log_data': warnings_df.to_dict(orient='records'),
        'faulted_log_data': faults_df.to_dict(orient='records')
    })

def control_panel(request):
    """
    Render the control panel showing inverter statuses.

    Displays inverter health status, degradation percentages, and fault counts.
    """
    global warnings_df, faults_df, sensor_data_df
    FAULT_THRESHOLD = 3
    panel_status = []
    for i in range(1, 23):
        fault_count = faults_df[faults_df['panel'] == i].shape[0]
        status = "FAULT" if fault_count >= FAULT_THRESHOLD else "WARNING" if not warnings_df[warnings_df['panel'] == i].empty else "OK"
        degradation = "N/A"
        try:
            if not sensor_data_df.empty:
                panel_data = sensor_data_df[
                    sensor_data_df[f'measured_dc{i}'].notnull() &
                    sensor_data_df[f'predicted_dc{i}'].notnull()
                ]
                if not panel_data.empty:
                    sum_predicted = panel_data[f'predicted_dc{i}'].sum()
                    sum_measured = panel_data[f'measured_dc{i}'].sum()
                    degradation = abs((sum_predicted - sum_measured) / ((sum_predicted + sum_measured) / 2)) * 100
                    degradation = 100 - round(degradation, 2)
        except Exception as e:
            logging.error(f"Error calculating degradation for Panel {i}: {e}")
        panel_status.append({
            'panel': i,
            'status': status,
            'degradation': degradation,
            'fault_count': fault_count
        })
    return render(request, 'maintenance/controlpanel.html', {'panel_status': panel_status})

@csrf_exempt
def acknowledge_warning(request):
    """Handle acknowledgment of warnings by removing them."""
    global warnings_df
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            timestamp = float(data.get('timestamp'))
            panel = int(data.get('panel'))
            warnings_df = warnings_df[~((warnings_df['timestamp'] == timestamp) & (warnings_df['panel'] == panel))]
            return JsonResponse({'success': True})
        except Exception as e:
            logging.error(f"Error acknowledging warning: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_panel_data(request):
    """Fetch historical data for a specific panel."""
    global sensor_data_df
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            panel = int(data.get('panel'))
            panel_columns = ['timestamp', 'ambient_temp', 'module_temp', 'irradiation', f'measured_dc{panel}', f'predicted_dc{panel}']
            panel_data = sensor_data_df[panel_columns].dropna().rename(columns={
                f'measured_dc{panel}': 'measured_dc',
                f'predicted_dc{panel}': 'predicted_dc'
            })
            return JsonResponse({'success': True, 'data': panel_data.to_dict(orient='records')})
        except Exception as e:
            logging.error(f"Error fetching panel data: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
