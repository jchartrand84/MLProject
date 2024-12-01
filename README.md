# SolarGuard - LSTM Models for Maintenance Optimization

## Project Overview
SolarGuard is an advanced system designed to predict DC power generation in solar panels using machine learning techniques, specifically Long Short-Term Memory (LSTM) models. By analyzing historical and real-time solar irradiation data, SolarGuard forecasts DC power generation to identify discrepancies and optimize solar panel maintenance.

### Features:
- **DC Prediction:** Uses LSTM models to predict solar panel power generation.
- **Fault & Warning Logs:** Flags discrepancies between measured and predicted DC output.
- **Web App:** Interactive dashboard for live sensor data, maintenance logs, and control panel.

---

## About the LSTM Model
The LSTM model processes incoming irradiation, ambient temperature, and module temperature data to predict DC output for solar panels.

### Model Architecture:
- **Bidirectional LSTM Layers:** Captures both forward and backward temporal dependencies.
- **Dropout Layers:** Prevents overfitting during training.
- **Dense Output Layer:** Predicts a single target: DC power generation.

---

## Core Components

### 1. **Model Training Code**
The Bidirectional LSTM model is trained using historical solar data. Here's an overview of the process:

- **Input:** Ambient temperature, module temperature, and irradiation.
- **Output:** DC power generation prediction.
- **Sequence Length:** 15-time steps for temporal patterns.
- **Optimization:** Uses `adam` optimizer with early stopping and learning rate reduction for efficient training.

Training Results: Results, including R² scores and Mean Absolute Error (MAE), are saved in `bidirectional_lstm_results_per_panel_dc_power.csv`.

---

## 2. Web Application
The web application, built with Django, provides an interactive interface for monitoring real-time solar panel performance.

### Views Overview:
- **home**: Displays an introduction and project overview.
- **sensor_data**: Shows live updates from environmental sensors and inverter performance.
- **control_panel**: Provides detailed health and fault metrics for each solar inverter.
- **maintenance_log**: Logs warnings and faults with acknowledgment functionality.

### Fault Logging:
- **Faults**: Percentage difference ≥ 10%.
- **Warnings**: Percentage difference between 5% and 10%.

---

## Installation

### Prerequisites
- Python 3.8 or later
- Pip installed

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/jchartrand84/MLProject.git
   cd MLProject
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Directory Structure
```plaintext
SolarGuard/
├── maintenance/           # CSV files for simulation
│   ├── data/            # Pre-trained LSTM models
│   ├── models/          # Static files (CSS, JS, Images)
│   ├── static/          # Django templates
│   ├── templates/       # Backend logic
│   ├── views.py          
│   ── ...
├── SolarSystemML/

```

---

## Contact Information
For more information, please contact:

- **Jonathan Chartrand & Robert Boutette**: 4th Year CE Students, Dalhousie University.
- Email: [jonathan.chartrand@dal.ca](mailto:jonathan.chartrand@dal.ca)
         [robert.boutette@dal.ca](mailto:robert.boutette@dal.ca)

---

© Dalhousie University, SolarGuard Project

