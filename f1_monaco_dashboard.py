# ==========================================================
# F1 MONACO 2025 DATA ANALYTICS DASHBOARD
# Portfolio Project – Data Analyst
# ==========================================================

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

import fastf1
from fastf1 import get_session

from sqlalchemy import create_engine, text

import plotly.express as px
from dash import Dash, dcc, html, Input, Output

from pandasql import sqldf

# ==========================================================
# CONFIG
# ==========================================================

CACHE_DIR = "f1_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

MYSQL_USER = "root"
MYSQL_PASSWORD = "password"   # 🔁 change this
MYSQL_HOST = "localhost"
MYSQL_DB = "f1_db"

# ==========================================================
# 1️⃣ FETCH DATA FROM FASTF1
# ==========================================================

def fetch_data():
    try:
        print("📥 Loading Monaco 2025 Race Session...")
        session = get_session(2025, "Monaco", "R")
        session.load()

        results_df = session.results.copy()

        # 🔧 Handle FastF1 column name differences
        if "FastestLapTime" in results_df.columns:
            fastest_col = "FastestLapTime"
        elif "FastestLap" in results_df.columns:
            fastest_col = "FastestLap"
        else:
            fastest_col = None

        cols = [
            "DriverNumber",
            "FullName",
            "TeamName",
            "Position",
            "Points",
            "Time",
            "Status"
        ]

        if fastest_col:
            cols.append(fastest_col)

        results = results_df[cols].copy()

        results.rename(columns={
            "DriverNumber": "driverId",
            "FullName": "driverName",
            "TeamName": "constructor",
            "Position": "position",
            "Points": "points",
            "Time": "raceTime",
        }, inplace=True)

        if fastest_col:
            results.rename(columns={fastest_col: "fastestLap"}, inplace=True)
        else:
            results["fastestLap"] = None

        results["raceTime"] = results["raceTime"].astype(str)
        results["fastestLap"] = results["fastestLap"].astype(str)

        # ================= LAPS =================
        laps = session.laps[[
            "Driver", "LapNumber", "LapTime", "Stint", "Compound"
        ]].copy()

        laps["LapTime"] = laps["LapTime"].astype(str)

        # ================= PIT STOPS =================
        pit_stops = session.laps[session.laps["PitInTime"].notna()][[
            "Driver", "LapNumber", "PitInTime", "PitOutTime"
        ]].copy()

        pit_stops["PitInTime"] = pit_stops["PitInTime"].astype(str)
        pit_stops["PitOutTime"] = pit_stops["PitOutTime"].astype(str)

        # ================= EXPORT CSV =================
        results.to_csv("results.csv", index=False)
        laps.to_csv("laps.csv", index=False)
        pit_stops.to_csv("pit_stops.csv", index=False)

        print("✅ CSV files exported")

        return results, laps, pit_stops

    except Exception as e:
        print("❌ Error fetching data:", e)
        return None, None, None


# ==========================================================
# 2️⃣ LOAD INTO MYSQL
# ==========================================================

def load_sql(results_df, laps_df, pit_df):
    try:
        engine = create_engine(
            f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}"
        )

        with engine.connect() as conn:
            conn.execute(text("CREATE DATABASE IF NOT EXISTS f1_db"))

        engine = create_engine(
            f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
        )

        results_df.to_sql("results", engine, if_exists="replace", index=False)
        laps_df.to_sql("laps", engine, if_exists="replace", index=False)
        pit_df.to_sql("pit_stops", engine, if_exists="replace", index=False)

        print("✅ Data loaded into MySQL")

        return engine

    except Exception as e:
        print("⚠️ MySQL not connected. Skipping SQL load.")
        print("Reason:", e)
        return None


# ==========================================================
# 3️⃣ EDA WITH PANDAS
# ==========================================================

def eda(results_df, laps_df, pit_df):
    print("\n📊 RUNNING EDA...\n")

    results_df = results_df.fillna("NA")

    # Top drivers by points
    top_drivers = results_df.sort_values("points", ascending=False)

    # Pit stops per driver
    avg_pits = pit_df.groupby("Driver").size().reset_index(name="pitStops")

    # Win rate
    results_df["win"] = np.where(results_df["position"] == 1, 1, 0)
    win_rate = results_df[["driverName", "win"]]

    print("🏆 Top Drivers by Points")
    print(top_drivers[["driverName", "points"]].head())

    print("\n⛽ Pit Stops per Driver")
    print(avg_pits)

    print("\n🥇 Win Rate")
    print(win_rate)

    return top_drivers, avg_pits, win_rate


# ==========================================================
# 4️⃣ SQL ANALYTICS
# ==========================================================

def sql_queries(engine):
    try:
        query = """
        SELECT driverName, fastestLap
        FROM results
        WHERE fastestLap IS NOT NULL
        ORDER BY fastestLap ASC
        LIMIT 5;
        """

        fastest = pd.read_sql(query, engine)

        print("\n⚡ Fastest Laps (SQL)")
        print(fastest)

        return fastest

    except Exception as e:
        print("⚠️ SQL query skipped:", e)
        return None


# ==========================================================
# 5️⃣ INSIGHTS
# ==========================================================

def print_insights(top_drivers, avg_pits):
    leader = top_drivers.iloc[0]

    print("\n📌 KEY INSIGHTS")
    print(f"🏆 {leader['driverName']} leads Monaco 2025 with {leader['points']} points")

    if not avg_pits.empty:
        most_pits = avg_pits.sort_values("pitStops", ascending=False).iloc[0]
        print(f"⛽ {most_pits['Driver']} had the most pit stops ({most_pits['pitStops']})")

    print("📈 Monaco is a track where qualifying position is crucial.")


# ==========================================================
# 6️⃣ DASHBOARD
# ==========================================================

def run_dashboard(top_drivers_df, laps_df, results_df):
    app = Dash(__name__)

    app.layout = html.Div([
        html.H1("🏎️ F1 Monaco 2025 Dashboard"),

        dcc.Graph(id="top-drivers-bar"),
        dcc.Graph(id="lap-times-line"),
        dcc.Graph(id="constructors-pie")
    ])

    @app.callback(
        Output("top-drivers-bar", "figure"),
        Input("top-drivers-bar", "id")
    )
    def update_bar(_):
        return px.bar(
            top_drivers_df,
            x="driverName",
            y="points",
            color="constructor",
            title="Top Drivers by Points"
        )

    @app.callback(
        Output("lap-times-line", "figure"),
        Input("lap-times-line", "id")
    )
    def update_line(_):
        sample_drivers = laps_df["Driver"].unique()[:3]
        lap_sample = laps_df[laps_df["Driver"].isin(sample_drivers)]

        return px.line(
            lap_sample,
            x="LapNumber",
            y="LapTime",
            color="Driver",
            title="Lap Time Trends"
        )

    @app.callback(
        Output("constructors-pie", "figure"),
        Input("constructors-pie", "id")
    )
    def update_pie(_):
        return px.pie(
            results_df,
            names="constructor",
            values="points",
            title="Constructor Points Share"
        )

    app.run_server(debug=True)


# ==========================================================
# 7️⃣ MAIN PIPELINE
# ==========================================================

def main():
    results_df, laps_df, pit_df = fetch_data()

    if results_df is None:
        return

    engine = load_sql(results_df, laps_df, pit_df)

    top_drivers_df, avg_pits_df, win_rate_df = eda(results_df, laps_df, pit_df)

    if engine:
        sql_queries(engine)

    print_insights(top_drivers_df, avg_pits_df)

    # 📊 Static plots for screenshots
    fig1 = px.bar(
        top_drivers_df,
        x="driverName",
        y="points",
        color="constructor",
        title="Top Drivers – Monaco 2025"
    )
    fig1.show()

    fig2 = px.pie(
        results_df,
        names="constructor",
        values="points",
        title="Constructor Points Distribution"
    )
    fig2.show()

    # 🚀 Launch Dashboard
    run_dashboard(top_drivers_df, laps_df, results_df)


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    main()
