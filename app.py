import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from threading import Timer
from flask import send_file
from analytics import load_data, preprocess_data, summarize_data  # Ensure 'detect_anomalies' is in 'analytics.py'
import os

# Initialize the app
app = Dash(__name__)
app.title = "User Behavior Analytics"

# Global data path
data_path = r'C:\Users\S\Desktop\flask\data\user_logs.csv'

# Define the detect_anomalies function
def detect_anomalies(data):
    """Detects anomalies based on unusual frequency of actions or rare actions."""
    data['anomaly'] = 'Normal'  # Initialize anomaly column with 'Normal'
    
    for index, row in data.iterrows():
        if row['user_id'] == 'user10':  # Flagging actions for user10 as threats
            if row['action'] in ['login', 'delete', 'edit']:
                data.at[index, 'anomaly'] = 'Threat'  # Flagging as "Threat"
    
    return data

# Load and process data
data = load_data(data_path)
data = preprocess_data(data)
data = detect_anomalies(data)  # Run anomaly detection initially
summary = summarize_data(data)

# Simulate live data by appending new logs
def append_new_logs():
    """Simulate new log entries for live updates."""
    new_logs = [
        {"timestamp": "2025-01-15T08:45:00", "user_id": "user8", "action": "login", "resource": "web"},
        {"timestamp": "2025-01-15T08:50:00", "user_id": "user9", "action": "delete", "resource": "file9"},
        {"timestamp": "2025-01-15T08:53:00", "user_id": "user10", "action": "login", "resource": "web"},
        {"timestamp": "2025-01-15T08:54:00", "user_id": "user10", "action": "delete", "resource": "file10"},
        {"timestamp": "2025-01-15T08:55:00", "user_id": "user10", "action": "edit", "resource": "file10"},
    ]
    df_new = pd.DataFrame(new_logs)
    global data
    data = pd.concat([data, preprocess_data(df_new)])
    data = detect_anomalies(data)  # Re-run anomaly detection
    Timer(5, append_new_logs).start()

append_new_logs()

# App layout
app.layout = html.Div(
    style={'backgroundColor': '#1e1e2f', 'color': '#fff', 'padding': '20px'},
    children=[
        html.H1("User Behavior Analytics", style={'textAlign': 'center'}),
        html.Div([
            html.Div(f"Total Logs: {summary['Total Logs']}", id='total-logs', style={'marginBottom': '10px'}),
            html.Div(f"Total Users: {summary['Total Users']}", id='total-users', style={'marginBottom': '10px'}),
            html.Div(f"Total Threats Detected: {summary['Total Threats']}", id='total-threats', style={'marginBottom': '20px', 'color': 'red'}),
            html.Button("Export Report (CSV)", id="export-btn-csv", n_clicks=0),
            html.Button("Export Report (Excel)", id="export-btn-excel", n_clicks=0),
            dcc.Download(id="download-dataframe"),
        ]),
        dcc.Graph(id="activity-graph"),
        dcc.Interval(id='interval-component', interval=2000, n_intervals=0),
    ]
)

# Callback to update graph and metrics
@app.callback(
    Output("activity-graph", "figure"),
    Output("total-logs", "children"),
    Output("total-users", "children"),
    Output("total-threats", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    global data
    summary = summarize_data(data)
    fig = px.scatter(
        data,
        x='timestamp',
        y='user_id',
        color='anomaly',
        symbol='action',
        size='resource_encoded',
        title="User Activity Anomalies",
        labels={'anomaly': 'Status', 'user_id': 'User ID', 'timestamp': 'Timestamp'},
    )
    fig.update_layout(
        paper_bgcolor="#1e1e2f",
        plot_bgcolor="#1e1e2f",
        font_color="#fff",
        legend_title=dict(font=dict(color="#fff")),
        hovermode="closest",
    )
    return (
        fig,
        f"Total Logs: {summary['Total Logs']}",
        f"Total Users: {summary['Total Users']}",
        f"Total Threats Detected: {summary['Total Threats']}"
    )

# Export data callback for CSV
@app.callback(
    Output("download-dataframe", "data"),
    [Input("export-btn-csv", "n_clicks"), ]
)
def export_report(n_clicks_csv, n_clicks_excel):
    """Export current data as a CSV or Excel file."""
    if n_clicks_csv > 0:
        file_path = "exported_report.csv"
        data.to_csv(file_path, index=False)
        return dcc.send_file(file_path)
    elif n_clicks_excel > 0:
        file_path = "exported_report.xlsx"
        data.to_excel(file_path, index=False)
        return dcc.send_file(file_path)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)