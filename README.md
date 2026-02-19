F1 Monaco 2025 Data Analytics Dashboard

An end-to-end Data Analytics & Visualization project built using real Formula 1 race telemetry.
This project fetches Monaco Grand Prix 2025 race data using FastF1, performs EDA with Pandas, stores data in MySQL, and presents insights through an interactive Dash dashboard

Project Highlights

✔ Automated data pipeline using FastF1 API
✔ CSV export for results, laps, and pit stops
✔ MySQL integration for structured storage
✔ SQL + Pandas analytics
✔ Interactive dashboard with Plotly Dash
✔ Deploy-ready modular code


Tech Stack

* Python
* FastF1
* Pandas / NumPy
* MySQL + SQLAlchemy
* Plotly
* Dash
* pandasql

Project Structure

```
f1-monaco-2025-dashboard/
│
├── f1_monaco_2025_dashboard.py   # Main pipeline script
├── requirements.txt              # Dependencies
├── README.md                     # Project documentation
├── .gitignore
└── screenshots/
    ├── top_drivers.png
    ├── constructors_pie.png
    └── dashboard.png
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/f1-monaco-2025-dashboard.git
cd f1-monaco-2025-dashboard
```

## 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Mac/Linux
```

Install Dependencies

```bash
pip install -r requirements.txt
```

MySQL Configuration

Update credentials in the script:

```python
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_HOST = "localhost"
MYSQL_DB = "f1_db"
```

Ensure MySQL server is running.

---

# ▶️ Run the Project

```bash
python f1_monaco_2025_dashboard.py
```

This will:

1. Fetch Monaco 2025 race data
2. Export CSV files
3. Load data into MySQL
4. Perform EDA
5. Generate plots
6. Launch interactive dashboard

Dashboard runs at:
http://127.0.0.1:8050


 Dashboard Features

* 🏆 Top drivers by points (Bar chart)
* ⏱️ Lap time trends by driver (Line chart)
* 🏁 Constructor points share (Pie chart)


Key Insights

* Track position is critical at Monaco due to limited overtaking
* Pit stop strategy impacts final race position
* Fastest lap does not always correlate with race winner

Skills Demonstrated

* Data pipeline design (API → CSV → SQL → Dashboard)
* Data cleaning & EDA with Pandas
* SQL analytics & query integration
* Interactive data visualization
* Production-ready Python project structure

Future Improvements

 Add qualifying & practice session filters
 Deploy dashboard on Render/Heroku
 Add driver comparison too
 Add lap pace prediction using ML



