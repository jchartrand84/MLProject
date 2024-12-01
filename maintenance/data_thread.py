import threading
import pandas as pd
from datetime import datetime
import time
import os

# Shared data structures
sensor_values = {
    "weather": {
        "ambient_temp": 0,
        "module_temp": 0,
        "irradiation": 0,
    },
    "panels": [
        {"id": i, "predicted_dc": 0, "measured_dc": 0, "percent_diff": 0}
        for i in range(1, 23)
    ],
}
serial_data_lock = threading.Lock()

# Path to the CSV file
INPUT_CSV = os.path.join('maintenance', 'data', 'live_sensor_sim.csv')

# Load the CSV data
try:
    csv_data = pd.read_csv(INPUT_CSV)
except Exception as e:
    print(f"Error loading CSV file: {e}")
    csv_data = pd.DataFrame()

# Thread to simulate live data
def read_csv_data():
    global sensor_values
    try:
        while True:
            now = datetime.now()
            if now.second == 0:  # Simulate live data at the top of each minute
                minute_index = now.minute % len(csv_data)  # Cycle through rows
                row = csv_data.iloc[minute_index].to_dict()

                with serial_data_lock:
                    # Update weather data
                    sensor_values["weather"] = {
                        "ambient_temp": round(row.get("ambient_temp", 0), 2),
                        "module_temp": round(row.get("module_temp", 0), 2),
                        "irradiation": round(row.get("irradiation", 0), 6),
                    }

                    # Update panel data
                    for i in range(1, 23):
                        measured_dc = row.get(f"measured_dc{i}", 0)
                        predicted_dc = measured_dc  # Placeholder; update with ML model later
                        percent_diff = 0  # Placeholder

                        sensor_values["panels"][i - 1] = {
                            "id": i,
                            "predicted_dc": round(predicted_dc, 2),
                            "measured_dc": round(measured_dc, 2),
                            "percent_diff": round(percent_diff, 2),
                        }

                print(f"Updated sensor values: {sensor_values}")  # Debugging log
            time.sleep(1)
    except Exception as e:
        print(f"Error in read_csv_data thread: {e}")

# Start the thread
csv_thread = threading.Thread(target=read_csv_data, daemon=True)
csv_thread.start()
