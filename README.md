# ML-Based Network Intrusion Detection System with Explainable AI

> This is a learning project built to develop practical skills in machine learning, cybersecurity data, and explainable AI. It is not production-ready software.

---

## What This Project Does

Most traditional intrusion detection systems rely on signature matching - they flag traffic that matches a known attack pattern. This means they completely miss attacks they have never seen before.

This project takes a different approach: instead of learning what attacks look like, the model learns what **normal traffic** looks like. Anything that deviates significantly from normal gets flagged as suspicious. This is called **anomaly-based detection** and is the approach used in modern commercial security tools like Palo Alto's Cortex XDR.

The pipeline has four stages:

```
Normal traffic → Train Autoencoder → learns normal behaviour
                                              │
All traffic → Autoencoder → Reconstruction Error
                                              │
                         ┌────────────────────┴────────────────────┐
                      Low error                               High error
                         │                                         │
                    Not flagged                              Flagged
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

**NSL-KDD** - a benchmark dataset for network intrusion detection research, provided by the Canadian Institute for Cybersecurity.

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
| `scikit-learn` | Preprocessing - OneHotEncoder, MinMaxScaler, ColumnTransformer |
| `tensorflow / keras` | Autoencoder and classifier neural networks |
| `shap` | Explainability - which features triggered each classification |
| `streamlit` | Interactive results dashboard |

---

## Project Structure

```
network-anomaly-detection-ids/
│
├── Notebooks/
│   ├── 01_eda_and_preprocessing.ipynb   - data exploration and preprocessing
│   ├── 02_autoencoder.ipynb             - anomaly detection model
│   ├── 03_classifier.ipynb              - attack type classification
│   └── 04_shap.ipynb                   - SHAP explainability
│
├── models/
│   ├── autoencoder.keras               - saved autoencoder weights
│   ├── classifier.keras                - saved classifier weights
│   ├── shap_neptune.png                - SHAP plot for DoS attacks
│   └── shap_normal.png                 - SHAP plot for normal traffic
│
├── data/                               - not tracked by git (see setup)
│   ├── KDDTrain+.txt
│   └── KDDTest+.txt
│
├── app.py                              - Streamlit dashboard
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
pip install tensorflow numpy pandas scikit-learn jupyterlab matplotlib seaborn shap streamlit joblib

# Download the NSL-KDD dataset from Kaggle (link above)
# Place KDDTrain+.txt and KDDTest+.txt in the data/ folder

# Run notebooks in order
jupyter lab

# Launch dashboard (after running all notebooks)
streamlit run app.py
```

Run the notebooks in order: 01 → 02 → 03 → 04

---

## Progress

- [x] EDA and preprocessing
- [x] Autoencoder anomaly detection
- [x] Neural network classifier
- [x] SHAP explainability
- [x] Streamlit dashboard

---

## Results

### Stage 1 - Autoencoder Anomaly Detection

The autoencoder was trained exclusively on normal traffic (67,343 connections) and achieved a final MSE loss of **0.0174**, converging by epoch 10 out of 20 - a healthy plateau indicating the model learned general normal traffic patterns without memorising individual samples.

Detection threshold was set at the **95th percentile** of normal traffic reconstruction errors (threshold = 0.0492).

| Metric | Value |
|---|---|
| Total connections evaluated | 125,973 |
| Flagged as anomalies | 52,391 (41.6%) |
| Actual attacks in dataset | 58,630 |
| Estimated attack recall | ~83.6% |
| Expected false positive rate | ~5% (by threshold design) |

**Notable observation:** The reconstruction error distribution of normal traffic is bimodal - two distinct clusters appear around error values 0.003 and 0.025. This reflects two behavioural patterns in normal traffic: short lightweight connections (low error) and longer HTTP-style sessions (moderate error). The autoencoder learned both patterns independently.

**Novel attack detection:** The test set contains 17 attack types unseen during training. The autoencoder flags these as anomalies based purely on their deviation from normal traffic - demonstrating the core advantage of anomaly-based detection over signature matching, which would miss these entirely.

---

### Stage 2 - Neural Network Classifier

A three-layer neural network (64→32→16→softmax) with dropout was trained on flagged anomalies from the training set to classify attack types.

| Metric | Value |
|---|---|
| Training accuracy | 95.52% |
| Validation accuracy | 97.65% |
| Test accuracy | 80.00% |
| Weighted F1-score | 0.75 |

**Per-class breakdown (key classes):**

| Attack | Type | Precision | Recall | F1 | Support |
|---|---|---|---|---|---|
| neptune | DoS | 1.00 | 1.00 | 1.00 | 4,657 |
| satan | Probe | 0.82 | 0.89 | 0.86 | 735 |
| normal | - | 0.79 | 0.90 | 0.84 | 9,711 |
| portsweep | Probe | 0.56 | 0.96 | 0.71 | 157 |
| smurf | DoS | 0.46 | 0.91 | 0.61 | 665 |
| guess_passwd | R2L | 0.00 | 0.00 | 0.00 | 1,231 |
| warezmaster | R2L | 0.00 | 0.00 | 0.00 | 944 |

**Key finding:** The classifier performs strongly on DoS and Probe attacks but fails entirely on R2L attacks (guess_passwd, warezmaster) despite their significant representation in the test set. R2L attacks are specifically designed to mimic legitimate user behaviour, resulting in low autoencoder reconstruction error - meaning fewer R2L samples were flagged and passed to the classifier during training. This creates a learned blind spot that mirrors a well-documented challenge in real-world intrusion detection research.

---

### Stage 3 - SHAP Explainability

SHAP (SHapley Additive exPlanations) was applied to the trained classifier using GradientExplainer with 200 background samples and 400 explanation samples. SHAP values were computed per class across all 122 input features, revealing which features drove each classification decision.

**Neptune (DoS) - key features identified by SHAP:**
- `dst_host_srv_count` - number of connections to the same service on the destination host. DoS attacks flood a single service, making this feature spike abnormally high
- `src_bytes` - bytes sent from source. DoS attacks send large volumes of data, producing unusually high values
- `count` - connections to the same host in the last 2 seconds. Flood attacks produce extremely high values that are almost never seen in normal traffic
- `serror_rate` - percentage of connections with SYN errors. Neptune specifically creates half-open TCP connections, making this rate approach 1.0

**Normal traffic - key features identified by SHAP:**
- `dst_host_same_srv_rate` - normal users connect to varied services, keeping this rate moderate
- `flag = SF` - normal connections complete properly (SYN-FIN), a strong signal of legitimate traffic
- `logged_in` - normal sessions involve successful logins, consistently pushing predictions toward normal

**Broader insight:** SHAP confirms that the classifier learned domain-relevant patterns rather than spurious correlations. The features it relies on for DoS detection (connection rates, byte volumes, error rates) align directly with what security researchers know about how DoS attacks behave at the network level.

---

## EDA Findings

- Normal traffic: 67,343 connections (53.5%) - dominant class
- Neptune (DoS): 41,214 connections (32.7%) - largest attack type
- Remaining 21 attack types: 17,416 connections combined (13.8%)
- `flag = S0` (incomplete connection) appears almost exclusively in attack traffic
- `protocol_type`: 3 values (tcp, udp, icmp) - tcp dominates attack traffic
- After OneHotEncoding categorical features, input dimensionality expands from 41 to 122 features

---

## What I Would Improve With More Time

- Experiment with convolutional autoencoders on the feature matrix
- Add threshold tuning curve (precision-recall tradeoff at different thresholds)
- Extend to CICIDS2017 dataset for more realistic modern attack patterns
- Add real-time packet capture using Scapy for live detection
- Address R2L blind spot using SMOTE oversampling on underrepresented attack classes

---

## References

- [NSL-KDD Dataset - Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/nsl.html)
- [Palo Alto Networks Unit 42 Threat Research](https://unit42.paloaltonetworks.com)
- [A Detailed Analysis of the KDD CUP 99 Data Set - Tavallaee et al.](https://www.semanticscholar.org/paper/A-detailed-analysis-of-the-KDD-CUP-99-data-set-Tavallaee-Bagheri/4dd66fb0db9c90f2da4f84a6e3dd01428d67c91b)