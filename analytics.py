import pandas as pd
from sklearn.ensemble import IsolationForest

def load_data(file_path):
    """Load user logs from a CSV file."""
    return pd.read_csv(file_path)

def preprocess_data(df):
    """Preprocess data by encoding categorical columns."""
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['action_encoded'] = pd.factorize(df['action'])[0]
    df['resource_encoded'] = pd.factorize(df['resource'])[0]
    return df

def detect_anomalies(data):
    """Detect anomalies using Isolation Forest."""
    data['anomaly'] = 'Normal'  # Initialize with 'Normal'
    
    # Feature engineering: using action and resource encoded values
    features = data[['action_encoded', 'resource_encoded']]
    
    # Initialize Isolation Forest for anomaly detection
    model = IsolationForest(contamination=0.1)  # Adjust contamination based on expected anomaly rate
    data['anomaly'] = model.fit_predict(features)  # Anomaly prediction (-1 for outliers, 1 for normal)
    
    # Convert -1 to 'Threat' and 1 to 'Normal'
    data['anomaly'] = data['anomaly'].map({-1: 'Threat', 1: 'Normal'})
    
    return data

def summarize_data(df):
    """Generate summary statistics."""
    total_logs = len(df)
    total_users = df['user_id'].nunique()
    total_threats = len(df[df['anomaly'] == 'Threat'])
    return {
        'Total Logs': total_logs,
        'Total Users': total_users,
        'Total Threats': total_threats
    }

# Example usage:
file_path = 'C:\\Users\\S\\Desktop\\flask\\data\\user_logs.csv'

df = load_data(file_path)
df = preprocess_data(df)
df = detect_anomalies(df)
summary = summarize_data(df)
print(summary)
