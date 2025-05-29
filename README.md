# AQI Dashboard: Real-time & Historical Air Quality Insights

Welcome to the **AQI Dashboard** project! This application provides a comprehensive and interactive dashboard for monitoring air quality across various countries and cities worldwide. Leveraging real-time and historical data, it offers in-depth insights into pollution levels, dominant pollutants, and future forecasts, all presented with intuitive visualizations.

## ✨ Features

This dashboard is designed to give you a complete picture of air quality, offering:

- **Real-time AQI Data**: Get instant Air Quality Index readings for cities, including their names, longitude, and latitude
- **Detailed Pollutant Breakdown**: View dashboards for specific pollutants such as PM2.5, Carbon Monoxide (CO), Ozone (O₃), Sulfur Dioxide (SO₂), and Nitrogen Dioxide (NO₂)
- **7-8 Day Forecast**: Plan ahead with air quality forecasts for the coming 7 to 8 days for any selected city
- **Dominant Pollutant Analysis**: Understand which pollutant is currently most prevalent and its percentage of occupancy in the air
- **Historical Data Exploration**: Access and visualize historical air quality data from different monitoring stations
- **Rich Visualizations**: Gain better understanding through detailed charts, pie graphs, and heatmaps for historical data

## 🚀 Getting Started

Follow these steps to set up and run the AQI Dashboard on your local machine.

### Prerequisites

- **Python 3.10 or higher** is required. You can download it from [python.org](https://python.org)
- **pip** (Python package installer), which usually comes with Python

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rahulnamilakonda/AQI-Dashboard.git
   cd AQI-Dashboard
   ```

2. **Create a Virtual Environment** (Recommended):
   It's highly recommended to create a virtual environment to manage project dependencies.
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - **On macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **On Windows (Command Prompt)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **On Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

4. **Install Dependencies**:
   Install all required Python packages using the requirements.txt file:
   ```bash
   pip install -r requirements.txt
   ```

### API Keys Setup

This project uses data from **OpenAQ** and **AQICN (WAQI)**. You'll need to obtain API tokens for both services.

1. **Get OpenAQ Token**:
   - Visit the [OpenAQ documentation](https://docs.openaq.org/)
   - Follow their instructions to sign up and obtain your `OPENAQ_TOKEN`

2. **Get WAQI Token (AQICN)**:
   - Visit the [AQICN API page](https://aqicn.org/api/)
   - Register and get your `WAQI_TOKEN`

3. **Create a `.env` file**:
   In the root directory of your project, create a file named `.env` and add your API tokens as follows:
   ```env
   OPENAQ_TOKEN="your_openaq_api_key_here"
   WAQI_TOKEN="your_waqi_api_key_here"
   ```

   > **Important**: Replace `"your_openaq_api_key_here"` and `"your_waqi_api_key_here"` with your actual API keys. Do not commit this `.env` file to your version control system for security reasons.

## ▶️ Running the Application

Once you have installed the dependencies and set up your API keys, you can run the dashboard:

1. **Ensure your virtual environment is active**:
   - If not already active, activate it using the commands from step 3 in the installation section

2. **Navigate to the project directory** (if not already there):
   ```bash
   cd AQI-Dashboard
   ```

3. **Run the Streamlit application**:
   ```bash
   streamlit run dashboard.py
   ```

4. **Access the dashboard**:
   - The command will automatically open the AQI Dashboard in your default web browser
   - If it doesn't open automatically, you can manually navigate to the URL shown in the terminal (usually `http://localhost:8501`)

### Stopping the Application

To stop the dashboard, press `Ctrl + C` in the terminal where the application is running.

## 🌐 Live Demo

You can access a live version of the dashboard at: [www.aqi-dashboard-servs.streamlit.app/](https://aqi-dashboard-servs.streamlit.app/)

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please feel free to open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

*Built with ❤️ for cleaner air and better environmental awareness*