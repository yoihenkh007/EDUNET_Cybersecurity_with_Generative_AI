import streamlit as st
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

import seaborn as sns
import matplotlib.pyplot as plt


# PAGE CONFIG
st.set_page_config(page_title="AI NIDS", layout="wide")

st.title("AI Network Intrusion Detection System")
st.write("Detects **DDoS or BENIGN**")


# LOAD DATA
@st.cache_data
def load_dataset():
    df = pd.read_csv("Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv")

    # clean column names
    df.columns = df.columns.str.strip()

    # normalize labels
    df["Label"] = df["Label"].astype(str).str.upper().str.strip()

    # binary encoding
    df["Label_Numeric"] = (df["Label"] != "BENIGN").astype(int)

    df = df.fillna(0)

    return df


df = load_dataset()


# FEATURE ENGINEERING
df["Total_Packets"] = df["Total Fwd Packets"] + df["Total Backward Packets"]

df["Packet_Rate"] = df["Total_Packets"] / (df["Flow Duration"] + 1)
df["Packet_Rate"] = df["Packet_Rate"].replace([np.inf, -np.inf], np.nan)
df["Packet_Rate"] = df["Packet_Rate"].clip(upper=1e6).fillna(0)

df["Fwd_Back_Ratio"] = (df["Total Fwd Packets"] + 1) / (df["Total Backward Packets"] + 1)

features = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total_Packets",
    "Packet_Rate",
    "Fwd_Back_Ratio"
]

X = df[features]
y = df["Label_Numeric"]

X = X.replace([np.inf, -np.inf], 0)

# SIDEBAR
st.sidebar.header("Training Controls")

split_size = st.sidebar.slider("Training %", 50, 90, 80)
n_estimators = st.sidebar.slider("Random Forest Trees", 10, 400, 200)

# TRAIN/TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=(100 - split_size) / 100,
    stratify=y,
    random_state=42
)


# TRAINING
st.subheader("1️⃣ Train Model")

if st.button("Train Model"):
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=42,
        class_weight="balanced_subsample"
    )

    model.fit(X_train, y_train)

    st.session_state["model"] = model
    st.success("Model trained successfully!")


# EVALUATION
st.subheader("2️⃣ Model Performance")

if "model" in st.session_state:

    model = st.session_state["model"]

    y_prob = model.predict_proba(X_test)[:, 1]

    # lower threshold -> more sensitive IDS
    threshold = 0.35

    y_pred = (y_prob >= threshold).astype(int)

    accuracy = accuracy_score(y_test, y_pred)

    c1, c2, c3 = st.columns(3)
    c1.metric("Accuracy", f"{accuracy*100:.2f}%")
    c2.metric("Total Samples", len(df))
    c3.metric("Attack % in Test", f"{100*y_test.mean():.2f}%")

    st.write("### Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    st.pyplot(fig)
   

else:
    st.info("Train the model above to view metrics.")


# LIVE SINGLE PACKET ANALYZER (FINAL)
st.subheader("3️⃣ Live Traffic Attack Simulator")

c1, c2, c3, c4 = st.columns(4)

p_port = c1.number_input("Destination Port", 0, 65535, 80)
p_dur = c2.number_input("Flow Duration", 0, 1000000, 200)
p_fwd = c3.number_input("Total Fwd Packets", 0, 500000, 2000)
p_bwd = c4.number_input("Total Backward Packets", 0, 500000, 10)

if st.button("Analyze Packet"):

    if "model" not in st.session_state:
        st.error("Train the model first.")
    else:
        model = st.session_state["model"]

        total_packets = p_fwd + p_bwd
        packet_rate = total_packets / (p_dur + 1)
        packet_rate = min(packet_rate, 1e6)

        fwd_back_ratio = (p_fwd + 1) / (p_bwd + 1)

        # ML input
        input_df = pd.DataFrame([[
            p_port,
            p_dur,
            p_fwd,
            p_bwd,
            total_packets,
            packet_rate,
            fwd_back_ratio
        ]], columns=features)

        ml_prob = model.predict_proba(input_df)[0][1]
        ml_attack = ml_prob >= 0.35

        #  ATTACK LABELING LOGIC 
        attack_label = "BENIGN"

       
        if packet_rate > 8:
            attack_label = "DDOS"

        else :
            attack_label = "BENIGN"

        # OUTPUT 
        if attack_label == "BENIGN":
            st.success("Traffic classified as BENIGN (safe)")
        else:
            st.error(f" {attack_label} DETECTED")
            st.write(f"**ML Attack Probability:** `{ml_prob:.2f}`")
            st.write(f"**Packet Rate:** `{packet_rate:.2f}` packets/ms")
            st.write(f"**Fwd/Back Ratio:** `{fwd_back_ratio:.2f}`")
