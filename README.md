# ML-Based Network Intrusion Detection System with Explainable AI

> ⚠️ This is a learning project built to develop practical skills in machine learning, cybersecurity data, and explainable AI. It is not production-ready software.

---

## What This Project Does

Most traditional intrusion detection systems rely on signature matching — they flag traffic that matches a known attack pattern. This means they completely miss attacks they have never seen before.

This project takes a different approach: instead of learning what attacks look like, the model learns what **normal traffic** looks like. Anything that deviates significantly from normal gets flagged as suspicious. This is called **anomaly-based detection** and is the approach used in modern commercial security tools like Palo Alto's Cortex XDR.

The pipeline has three stages:

```
Normal traffic → Train Autoencoder → learns normal behaviour
                                              │
All traffic → Autoencoder → Reconstruction Error
                                              │
                         ┌────────────────────┴────────────────────┐
                      Low error                               High error
                         │                                         │
                    Not flagged                              Flagged 🚨
                                                                   │
                                                    Neural Network Classifier
                                                                   │
                                                   Attack Type (DoS/Probe/R2L/U2R)
                                                                   │
                                                    SHAP Explainability
                                                                   │
                                                    Streamlit Dashboard
```

---

## Dataset

**NSL-KDD** — a benchmark dataset for network intrusion detection research, provided by the Canadian Institute for Cybersecurity.

- 125,973 training samples
- 22,544 test samples
- 41 features per network connection
- 23 attack types grouped into 4 categories: DoS, Probe, R2L, U2R

Download: https://www.kaggle.com/datasets/hassan06/nslkdd

Place the downloaded files in the `data/` folder:
```
data/
├── KDDTrain+.txt
└── KDDTest+.txt
```

---

## Tech Stack

| Library | Purpose |
|---|---|
| `pandas` | Data loading, filtering, inspection |
| `numpy` | Array operations, reconstruction error calculation |
| `scikit-learn` | Preprocessing — OneHotEncoder, MinMaxScaler, ColumnTransformer |
| `tensorflow / keras` | Autoencoder and classifier neural networks |
| `SHAP` | Explainability — which features triggered each alert |
| `streamlit` | Alert dashboard |

---

## Project Structure

```
network-anomaly-detection-ids/
│
├── Notebooks/
│   ├── 01_eda_and_preprocessing.ipynb   ← data exploration and preprocessing
│   ├── 02_autoencoder.ipynb             ← anomaly detection model
│   ├── 03_classifier.ipynb              ← attack type classification
│   └── 04_results_and_shap.ipynb        ← evaluation and explainability
│
├── models/
│   ├── autoencoder.h5                   ← saved autoencoder weights
│   └── classifier.h5                   ← saved classifier weights
│
├── data/                                ← not tracked by git (see setup)
│   ├── KDDTrain+.txt
│   └── KDDTest+.txt
│
├── .gitignore
└── README.md
```

---

## Setup

**Requirements:** Python 3.11, pip

```bash
# Clone the repo
git clone https://github.com/ShivaramHR/network-anomaly-detection-ids.git
cd network-anomaly-detection-ids

# Create and activate virtual environment
python3.11 -m venv ids-env
source ids-env/bin/activate

# Install dependencies
pip install tensorflow numpy pandas scikit-learn jupyterlab matplotlib seaborn shap streamlit

# Download the NSL-KDD dataset from Kaggle (link above)
# Place KDDTrain+.txt and KDDTest+.txt in the data/ folder

# Launch Jupyter
jupyter lab
```

Run the notebooks in order: 01 → 02 → 03 → 04

---

## Progress

- [x] EDA and preprocessing
- [x] Autoencoder anomaly detection
- [ ] Neural network classifier
- [ ] SHAP explainability
- [ ] Streamlit dashboard

---

## Key Findings So Far

**Class distribution (training set):**
- Normal traffic: 67,343 connections (53.5%)
- Neptune (DoS): 41,214 connections (32.7%) — dominant attack type
- Remaining 21 attack types: combined 17,416 connections (13.8%)

This heavy imbalance is why accuracy alone is a misleading metric for this problem. The project uses precision, recall and F1-score per class to evaluate honestly.

**Categorical features:**
- `protocol_type`: 3 unique values (tcp, udp, icmp)
- `service`: 70 unique values
- `flag`: 11 unique values — notably `S0` appears almost exclusively in attack traffic

---

## What I Would Improve With More Time

- Experiment with convolutional autoencoders on the feature matrix
- Add threshold tuning curve (precision-recall tradeoff at different thresholds)
- Extend to CICIDS2017 dataset for more realistic modern attack patterns
- Add real-time packet capture using Scapy for live detection

---

## References

- [NSL-KDD Dataset — Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/nsl.html)
- [Palo Alto Networks Unit 42 Threat Research](https://unit42.paloaltonetworks.com)
- [A Detailed Analysis of the KDD CUP 99 Data Set — Tavallaee et al.](https://www.semanticscholar.org/paper/A-detailed-analysis-of-the-KDD-CUP-99-data-set-Tavallaee-Bagheri/4dd66fb0db9c90f2da4f84a6e3dd01428d67c91b)