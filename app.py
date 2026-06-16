import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import joblib
import keras

# ── page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Network IDS Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ── load everything ───────────────────────────────────────
@st.cache_resource
def load_models():
    autoencoder = keras.models.load_model('models/autoencoder.keras')
    classifier = keras.models.load_model('models/classifier.keras')
    le = joblib.load('data/label_encoder.pkl')
    return autoencoder, classifier, le

@st.cache_data
def load_data():
    all_errors    = np.load('data/all_errors.npy')
    anomaly_flags = np.load('data/anomaly_flags.npy')
    threshold     = np.load('data/threshold.npy')[0]
    shap_values   = np.load('data/shap_values.npy', allow_pickle=True)
    X_sample      = np.load('data/X_sample.npy')
    return all_errors, anomaly_flags, threshold, shap_values, X_sample

autoencoder, classifier, le = load_models()
all_errors, anomaly_flags, threshold, shap_values, X_sample = load_data()

# ── header ────────────────────────────────────────────────
st.title("🛡️ Network Intrusion Detection System")
st.caption("Two-stage anomaly detection using autoencoder + neural network classifier on NSL-KDD dataset")

# ── top metrics ───────────────────────────────────────────
total      = len(anomaly_flags)
flagged    = int(anomaly_flags.sum())
clean      = total - flagged

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Connections",   f"{total:,}")
col2.metric("Flagged as Anomalies", f"{flagged:,}")
col3.metric("Normal Connections",   f"{clean:,}")
col4.metric("Detection Threshold",  f"{threshold:.4f}")

st.divider()

# ── reconstruction error plot ─────────────────────────────
st.subheader("Reconstruction Error Distribution")
st.caption("Autoencoder trained on normal traffic only. High reconstruction error signals anomalous behaviour.")

fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(all_errors[anomaly_flags == 0], bins=60,
        alpha=0.7, label='Normal traffic', color='steelblue')
ax.hist(all_errors[anomaly_flags == 1], bins=60,
        alpha=0.5, label='Flagged anomalies', color='tomato')
ax.axvline(threshold, color='red', linewidth=2,
           label=f'Threshold: {threshold:.4f}')
ax.set_xlabel('Reconstruction Error')
ax.set_ylabel('Count')
ax.legend()
st.pyplot(fig)

st.divider()

# ── classifier results ────────────────────────────────────
st.subheader("Classifier Performance on Test Set")

results = {
    'Attack':    ['neptune', 'satan', 'normal', 'portsweep', 'smurf', 'ipsweep', 'guess_passwd', 'warezmaster'],
    'Type':      ['DoS', 'Probe', 'Normal', 'Probe', 'DoS', 'Probe', 'R2L', 'R2L'],
    'Precision': [1.00, 0.82, 0.79, 0.56, 0.46, 0.24, 0.00, 0.00],
    'Recall':    [1.00, 0.89, 0.90, 0.96, 0.91, 0.99, 0.00, 0.00],
    'F1':        [1.00, 0.86, 0.84, 0.71, 0.61, 0.38, 0.00, 0.00],
    'Support':   [4657, 735, 9711, 157, 665, 141, 1231, 944]
}

import pandas as pd
df_results = pd.DataFrame(results)
st.dataframe(df_results, use_container_width=True)

st.divider()

# ── shap plots ────────────────────────────────────────────
st.subheader("SHAP Explainability")
st.caption("Which features most influenced each classification decision.")

tab1, tab2 = st.tabs(["Neptune (DoS)", "Normal Traffic"])

with tab1:
    st.image('models/shap_neptune.png', use_column_width=True)

with tab2:
    st.image('models/shap_normal.png', use_column_width=True)

st.divider()

# ── project info ──────────────────────────────────────────
st.subheader("About This Project")
st.markdown("""
This is a learning project built to develop practical skills in machine learning and cybersecurity.

**Pipeline:**
1. Autoencoder trained on normal traffic learns to reconstruct it well
2. Attack traffic has high reconstruction error and gets flagged
3. Flagged connections passed to neural network classifier for attack type labelling
4. SHAP explains which features drove each classification

**Dataset:** NSL-KDD (Canadian Institute for Cybersecurity)
**GitHub:** [network-anomaly-detection-ids](https://github.com/ShivaramHR/network-anomaly-detection-ids)
""")